"""
Statistics Module

Handles game statistics collection and analysis.
"""

import numpy as np
from collections import defaultdict


class GameStatistics:
    """Collect and analyze handball game statistics."""

    def __init__(self):
        """Initialize the statistics collector."""
        self.stats = {
            'total_frames': 0,
            'frames_with_motion': 0,
            'average_motion_percentage': 0.0,
            'total_player_detections': 0,
            'frames_analyzed': 0,
            'motion_percentages': []
        }

        # Per-player statistics
        self.player_stats = defaultdict(lambda: {
            'goals': 0,
            'shots': 0,
            'passes_made': 0,
            'passes_received': 0,
            'bad_passes': 0,
            'possession_frames': 0,
            'distance_covered': 0.0,
            'average_speed': 0.0,
            'speeds': []
        })

        # Team statistics
        self.team_stats = {
            'total_goals': 0,
            'total_shots': 0,
            'total_passes': 0,
            'total_bad_passes': 0,
            'possession_changes': 0
        }

        # Event history
        self.events = []
    
    def update_motion_stats(self, motion_detected, motion_percentage):
        """
        Update motion statistics.
        
        Args:
            motion_detected (bool): Whether motion was detected
            motion_percentage (float): Percentage of frame with motion
        """
        if motion_detected:
            self.stats['frames_with_motion'] += 1
        
        self.stats['motion_percentages'].append(motion_percentage)
        self.stats['frames_analyzed'] += 1
        
        # Update average
        self.stats['average_motion_percentage'] = np.mean(
            self.stats['motion_percentages']
        )
    
    def update_player_stats(self, player_count):
        """
        Update player detection statistics.
        
        Args:
            player_count (int): Number of players detected in current frame
        """
        self.stats['total_player_detections'] += player_count
    
    def set_total_frames(self, frame_count):
        """
        Set the total number of frames in the video.

        Args:
            frame_count (int): Total number of frames
        """
        self.stats['total_frames'] = frame_count

    def record_event(self, event):
        """
        Record a game event.

        Args:
            event (dict): Event details
        """
        self.events.append(event)

        event_type = event.get('type')

        # Update team and player stats based on event type
        if event_type == 'goal':
            self.team_stats['total_goals'] += 1
            if 'player' in event:
                self.player_stats[event['player']]['goals'] += 1

        elif event_type == 'shot':
            self.team_stats['total_shots'] += 1
            if 'player' in event:
                self.player_stats[event['player']]['shots'] += 1

        elif event_type == 'pass':
            self.team_stats['total_passes'] += 1
            from_player = event.get('from_player')
            to_player = event.get('to_player')

            if from_player is not None:
                self.player_stats[from_player]['passes_made'] += 1
            if to_player is not None:
                self.player_stats[to_player]['passes_received'] += 1

            # Check if it's a bad pass (unsuccessful)
            if event.get('unsuccessful', False):
                self.team_stats['total_bad_passes'] += 1
                if from_player is not None:
                    self.player_stats[from_player]['bad_passes'] += 1

        elif event_type == 'possession_change':
            self.team_stats['possession_changes'] += 1

    def update_player_possession(self, player_id):
        """
        Update possession frames for a player.

        Args:
            player_id (int): Player ID
        """
        if player_id is not None:
            self.player_stats[player_id]['possession_frames'] += 1

    def update_player_movement(self, player_id, distance, speed):
        """
        Update player movement statistics.

        Args:
            player_id (int): Player ID
            distance (float): Distance covered in this frame
            speed (float): Current speed
        """
        self.player_stats[player_id]['distance_covered'] += distance
        self.player_stats[player_id]['speeds'].append(speed)

        # Update average speed
        speeds = self.player_stats[player_id]['speeds']
        if speeds:
            self.player_stats[player_id]['average_speed'] = np.mean(speeds)
    
    def get_summary(self):
        """
        Get a summary of the collected statistics.

        Returns:
            dict: Statistics summary including player and team stats
        """
        summary = self.stats.copy()

        if summary['frames_analyzed'] > 0:
            summary['motion_detection_rate'] = (
                summary['frames_with_motion'] / summary['frames_analyzed'] * 100
            )
            summary['average_players_per_frame'] = (
                summary['total_player_detections'] / summary['frames_analyzed']
            )
        else:
            summary['motion_detection_rate'] = 0.0
            summary['average_players_per_frame'] = 0.0

        # Remove the raw list to keep summary clean
        summary.pop('motion_percentages', None)

        # Add team statistics
        summary['team_stats'] = self.team_stats.copy()

        # Add player statistics (clean up internal lists)
        player_summary = {}
        for player_id, stats in self.player_stats.items():
            player_summary[f"player_{player_id}"] = {
                'goals': stats['goals'],
                'shots': stats['shots'],
                'passes_made': stats['passes_made'],
                'passes_received': stats['passes_received'],
                'bad_passes': stats['bad_passes'],
                'possession_frames': stats['possession_frames'],
                'distance_covered': round(stats['distance_covered'], 2),
                'average_speed': round(stats['average_speed'], 2)
            }

        summary['player_stats'] = player_summary

        return summary
    
    def print_summary(self):
        """Print a formatted summary of statistics."""
        summary = self.get_summary()

        print("\n" + "="*70)
        print("Handball Game Analysis Summary")
        print("="*70)

        # Basic statistics
        print("\n--- General Statistics ---")
        print(f"Total Frames: {summary['total_frames']}")
        print(f"Frames Analyzed: {summary['frames_analyzed']}")
        print(f"Frames with Motion: {summary['frames_with_motion']}")
        print(f"Motion Detection Rate: {summary['motion_detection_rate']:.2f}%")
        print(f"Average Motion Percentage: {summary['average_motion_percentage']:.2f}%")
        print(f"Total Player Detections: {summary['total_player_detections']}")
        print(f"Average Players per Frame: {summary['average_players_per_frame']:.2f}")

        # Team statistics
        print("\n--- Team Statistics ---")
        team_stats = summary.get('team_stats', {})
        print(f"Total Goals: {team_stats.get('total_goals', 0)}")
        print(f"Total Shots: {team_stats.get('total_shots', 0)}")
        print(f"Total Passes: {team_stats.get('total_passes', 0)}")
        print(f"Bad Passes: {team_stats.get('total_bad_passes', 0)}")
        print(f"Possession Changes: {team_stats.get('possession_changes', 0)}")

        # Player statistics
        player_stats = summary.get('player_stats', {})
        if player_stats:
            print("\n--- Player Statistics ---")
            for player_id, stats in sorted(player_stats.items()):
                print(f"\n{player_id}:")
                print(f"  Goals: {stats['goals']}")
                print(f"  Shots: {stats['shots']}")
                print(f"  Passes Made: {stats['passes_made']}")
                print(f"  Passes Received: {stats['passes_received']}")
                print(f"  Bad Passes: {stats['bad_passes']}")
                print(f"  Possession Frames: {stats['possession_frames']}")
                print(f"  Distance Covered: {stats['distance_covered']:.2f} pixels")
                print(f"  Average Speed: {stats['average_speed']:.2f} pixels/frame")

        print("\n" + "="*70 + "\n")
