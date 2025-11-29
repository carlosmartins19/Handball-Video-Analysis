"""
Player Detector Module

Handles player detection and tracking in handball game videos.
"""

import cv2
import numpy as np


class PlayerDetector:
    """Detect and track players in handball game videos."""
    
    def __init__(self):
        """Initialize the player detector."""
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=True
        )
    
    def detect_players(self, frame, min_area=500):
        """
        Detect players in a frame using background subtraction.
        
        Args:
            frame (numpy.ndarray): Input frame
            min_area (int): Minimum area for a detected object
            
        Returns:
            list: List of detected player bounding boxes [(x, y, w, h), ...]
        """
        # Apply background subtraction
        fg_mask = self.background_subtractor.apply(frame)
        
        # Remove shadows
        fg_mask[fg_mask == 127] = 0
        
        # Apply morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            fg_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by area and extract bounding boxes
        players = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                players.append((x, y, w, h))
        
        return players
    
    def detect_motion_regions(self, frame1, frame2, threshold=25, min_area=500):
        """
        Detect regions with motion between two frames.
        
        Args:
            frame1 (numpy.ndarray): First frame
            frame2 (numpy.ndarray): Second frame
            threshold (int): Threshold for motion detection
            min_area (int): Minimum area for a motion region
            
        Returns:
            list: List of motion region bounding boxes [(x, y, w, h), ...]
        """
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Apply threshold
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours and extract bounding boxes
        motion_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                motion_regions.append((x, y, w, h))
        
        return motion_regions
    
    def draw_detections(self, frame, detections, color=(0, 255, 0), thickness=2):
        """
        Draw bounding boxes on frame.
        
        Args:
            frame (numpy.ndarray): Input frame
            detections (list): List of bounding boxes [(x, y, w, h), ...]
            color (tuple): Color for bounding boxes
            thickness (int): Line thickness
            
        Returns:
            numpy.ndarray: Frame with bounding boxes drawn
        """
        output = frame.copy()
        for (x, y, w, h) in detections:
            cv2.rectangle(output, (x, y), (x + w, y + h), color, thickness)
        return output
