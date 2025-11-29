"""
Player Tracker Module

Handles tracking individual players across frames and assigning unique IDs.
"""

import cv2
import numpy as np
from collections import defaultdict


class PlayerTracker:
    """Track individual players across frames using centroid tracking."""

    def __init__(self, max_disappeared=30, max_distance=50):
        """
        Initialize the player tracker.

        Args:
            max_disappeared (int): Maximum frames a player can disappear before deregistering
            max_distance (int): Maximum distance for matching players between frames
        """
        self.next_player_id = 0
        self.players = {}  # player_id -> centroid
        self.disappeared = {}  # player_id -> frame count
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.player_boxes = {}  # player_id -> (x, y, w, h)

    def _compute_centroid(self, box):
        """
        Compute the centroid of a bounding box.

        Args:
            box (tuple): Bounding box (x, y, w, h)

        Returns:
            tuple: Centroid (cx, cy)
        """
        x, y, w, h = box
        cx = x + w // 2
        cy = y + h // 2
        return (cx, cy)

    def update(self, detections):
        """
        Update tracker with new detections.

        Args:
            detections (list): List of bounding boxes [(x, y, w, h), ...]

        Returns:
            dict: Dictionary mapping player_id to bounding box
        """
        # If no detections, mark all existing players as disappeared
        if len(detections) == 0:
            for player_id in list(self.disappeared.keys()):
                self.disappeared[player_id] += 1

                # Deregister if disappeared for too long
                if self.disappeared[player_id] > self.max_disappeared:
                    self._deregister(player_id)

            return {}

        # Compute centroids for all detections
        input_centroids = np.array([self._compute_centroid(box) for box in detections])

        # If no existing players, register all detections as new players
        if len(self.players) == 0:
            for i, box in enumerate(detections):
                self._register(input_centroids[i], box)
        else:
            # Get existing player IDs and centroids
            player_ids = list(self.players.keys())
            player_centroids = np.array(list(self.players.values()))

            # Compute distance between each pair of centroids
            distances = np.linalg.norm(
                player_centroids[:, np.newaxis] - input_centroids,
                axis=2
            )

            # Find the minimum distance for each existing player
            rows = distances.min(axis=1).argsort()
            cols = distances.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            # Match existing players with new detections
            for row, col in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                if distances[row, col] > self.max_distance:
                    continue

                player_id = player_ids[row]
                self.players[player_id] = input_centroids[col]
                self.player_boxes[player_id] = detections[col]
                self.disappeared[player_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            # Mark unmatched existing players as disappeared
            unused_rows = set(range(len(player_centroids))) - used_rows
            for row in unused_rows:
                player_id = player_ids[row]
                self.disappeared[player_id] += 1

                if self.disappeared[player_id] > self.max_disappeared:
                    self._deregister(player_id)

            # Register new players for unmatched detections
            unused_cols = set(range(len(input_centroids))) - used_cols
            for col in unused_cols:
                self._register(input_centroids[col], detections[col])

        return self.player_boxes.copy()

    def _register(self, centroid, box):
        """
        Register a new player.

        Args:
            centroid (tuple): Centroid (cx, cy)
            box (tuple): Bounding box (x, y, w, h)
        """
        self.players[self.next_player_id] = centroid
        self.player_boxes[self.next_player_id] = box
        self.disappeared[self.next_player_id] = 0
        self.next_player_id += 1

    def _deregister(self, player_id):
        """
        Deregister a player.

        Args:
            player_id (int): ID of the player to deregister
        """
        del self.players[player_id]
        del self.disappeared[player_id]
        if player_id in self.player_boxes:
            del self.player_boxes[player_id]

    def get_active_players(self):
        """
        Get list of currently active player IDs.

        Returns:
            list: List of active player IDs
        """
        return list(self.players.keys())
