"""
Event Detector Module

Detects handball-specific events like goals, passes, shots, and ball possession.
"""

import cv2
import numpy as np
from collections import deque


class EventDetector:
    """Detect handball game events."""

    def __init__(self):
        """Initialize the event detector."""
        self.ball_tracker = BallTracker()
        self.event_history = []
        self.player_possession = {}  # player_id -> frames with possession
        self.player_movements = {}  # player_id -> deque of positions

    def detect_ball(self, frame):
        """
        Detect the ball in the frame using color and shape detection.

        Args:
            frame (numpy.ndarray): Input frame

        Returns:
            tuple: Ball position (x, y) or None if not detected
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define range for ball colors (typically orange/yellow for handball)
        # This can be adjusted based on the actual ball color
        lower_orange = np.array([5, 100, 100])
        upper_orange = np.array([25, 255, 255])

        # Create mask
        mask = cv2.inRange(hsv, lower_orange, upper_orange)

        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Find the largest circular contour (likely the ball)
        ball_contour = None
        max_circularity = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:  # Minimum size filter
                continue

            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue

            circularity = 4 * np.pi * area / (perimeter * perimeter)

            if circularity > max_circularity and circularity > 0.6:
                max_circularity = circularity
                ball_contour = contour

        if ball_contour is not None:
            M = cv2.moments(ball_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return (cx, cy)

        return None

    def detect_possession(self, ball_pos, tracked_players):
        """
        Determine which player has possession of the ball.

        Args:
            ball_pos (tuple): Ball position (x, y) or None
            tracked_players (dict): Dictionary of player_id -> (x, y, w, h)

        Returns:
            int: Player ID with possession or None
        """
        if ball_pos is None or not tracked_players:
            return None

        ball_x, ball_y = ball_pos
        min_distance = float('inf')
        possessing_player = None

        for player_id, (x, y, w, h) in tracked_players.items():
            # Check if ball is within or very close to player's bounding box
            player_cx = x + w // 2
            player_cy = y + h // 2

            distance = np.sqrt((ball_x - player_cx) ** 2 + (ball_y - player_cy) ** 2)

            # If ball is within the player's box or close proximity
            if distance < min(w, h) and distance < min_distance:
                min_distance = distance
                possessing_player = player_id

        return possessing_player

    def detect_pass(self, prev_possession, current_possession, ball_movement):
        """
        Detect if a pass occurred.

        Args:
            prev_possession (int): Previous player with possession
            current_possession (int): Current player with possession
            ball_movement (float): Distance the ball moved

        Returns:
            dict: Pass event details or None
        """
        # Pass detected if possession changed and ball moved significantly
        if (prev_possession is not None and
            current_possession is not None and
            prev_possession != current_possession and
            ball_movement > 50):  # Minimum distance threshold

            return {
                'type': 'pass',
                'from_player': prev_possession,
                'to_player': current_possession,
                'distance': ball_movement
            }
        return None

    def detect_shot(self, player_id, ball_velocity, goal_regions):
        """
        Detect if a player took a shot.

        Args:
            player_id (int): Player ID
            ball_velocity (tuple): Ball velocity (vx, vy)
            goal_regions (list): List of goal region coordinates

        Returns:
            dict: Shot event details or None
        """
        if ball_velocity is None:
            return None

        vx, vy = ball_velocity
        speed = np.sqrt(vx ** 2 + vy ** 2)

        # Shot detected if ball is moving fast
        if speed > 30:  # Velocity threshold
            return {
                'type': 'shot',
                'player': player_id,
                'velocity': speed
            }
        return None

    def detect_goal(self, ball_pos, goal_regions, ball_velocity):
        """
        Detect if a goal was scored.

        Args:
            ball_pos (tuple): Ball position (x, y)
            goal_regions (list): List of goal region coordinates [(x1, y1, x2, y2), ...]
            ball_velocity (tuple): Ball velocity (vx, vy)

        Returns:
            dict: Goal event details or None
        """
        if ball_pos is None or ball_velocity is None:
            return None

        ball_x, ball_y = ball_pos
        vx, vy = ball_velocity
        speed = np.sqrt(vx ** 2 + vy ** 2)

        # Check if ball entered goal region with sufficient velocity
        for i, (x1, y1, x2, y2) in enumerate(goal_regions):
            if x1 <= ball_x <= x2 and y1 <= ball_y <= y2 and speed > 20:
                return {
                    'type': 'goal',
                    'position': ball_pos,
                    'goal_id': i,
                    'velocity': speed
                }
        return None

    def analyze_player_movement(self, player_id, position, prev_position):
        """
        Analyze player movement patterns.

        Args:
            player_id (int): Player ID
            position (tuple): Current position (x, y)
            prev_position (tuple): Previous position (x, y)

        Returns:
            dict: Movement analysis
        """
        if prev_position is None:
            return None

        # Calculate movement
        dx = position[0] - prev_position[0]
        dy = position[1] - prev_position[1]
        distance = np.sqrt(dx ** 2 + dy ** 2)

        # Initialize movement history if not exists
        if player_id not in self.player_movements:
            self.player_movements[player_id] = deque(maxlen=30)  # Keep last 30 positions

        self.player_movements[player_id].append(position)

        return {
            'distance': distance,
            'direction': (dx, dy),
            'speed': distance  # Speed per frame
        }


class BallTracker:
    """Track ball position and velocity across frames."""

    def __init__(self, history_length=10):
        """
        Initialize ball tracker.

        Args:
            history_length (int): Number of positions to track
        """
        self.positions = deque(maxlen=history_length)
        self.history_length = history_length

    def update(self, position):
        """
        Update ball position.

        Args:
            position (tuple): Ball position (x, y) or None
        """
        if position is not None:
            self.positions.append(position)

    def get_velocity(self):
        """
        Calculate ball velocity based on recent positions.

        Returns:
            tuple: Velocity (vx, vy) or None
        """
        if len(self.positions) < 2:
            return None

        # Use last two positions for velocity
        pos1 = self.positions[-2]
        pos2 = self.positions[-1]

        vx = pos2[0] - pos1[0]
        vy = pos2[1] - pos1[1]

        return (vx, vy)

    def get_movement(self):
        """
        Calculate total distance moved since last position.

        Returns:
            float: Distance moved or 0
        """
        if len(self.positions) < 2:
            return 0

        pos1 = self.positions[-2]
        pos2 = self.positions[-1]

        return np.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)
