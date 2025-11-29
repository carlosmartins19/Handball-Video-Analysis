"""
Video Processor Module

Handles video loading, frame extraction, and basic video processing operations.
"""

import cv2
import numpy as np


class VideoProcessor:
    """Process handball game videos for analysis."""
    
    def __init__(self, video_path):
        """
        Initialize the video processor.
        
        Args:
            video_path (str): Path to the video file
        """
        self.video_path = video_path
        self.capture = None
        self.fps = 0
        self.frame_count = 0
        self.width = 0
        self.height = 0
        
    def load_video(self):
        """Load the video file and extract metadata."""
        self.capture = cv2.VideoCapture(self.video_path)
        
        if not self.capture.isOpened():
            raise ValueError(f"Unable to open video file: {self.video_path}")
        
        self.fps = int(self.capture.get(cv2.CAP_PROP_FPS))
        self.frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        return {
            'fps': self.fps,
            'frame_count': self.frame_count,
            'width': self.width,
            'height': self.height,
            'duration': self.frame_count / self.fps if self.fps > 0 else 0
        }
    
    def get_frame(self, frame_number):
        """
        Get a specific frame from the video.
        
        Args:
            frame_number (int): Frame number to retrieve
            
        Returns:
            numpy.ndarray: The frame as a numpy array, or None if failed
        """
        if self.capture is None:
            raise RuntimeError("Video not loaded. Call load_video() first.")
        
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.capture.read()
        
        return frame if ret else None
    
    def extract_frames(self, start_frame=0, end_frame=None, step=1):
        """
        Extract frames from the video.
        
        Args:
            start_frame (int): Starting frame number
            end_frame (int): Ending frame number (None for all frames)
            step (int): Step size between frames
            
        Yields:
            tuple: (frame_number, frame)
        """
        if self.capture is None:
            raise RuntimeError("Video not loaded. Call load_video() first.")
        
        if end_frame is None:
            end_frame = self.frame_count
        
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        for frame_num in range(start_frame, end_frame, step):
            ret, frame = self.capture.read()
            if not ret:
                break
            yield frame_num, frame
            
            # Skip frames according to step
            for _ in range(step - 1):
                self.capture.read()
    
    def detect_motion(self, frame1, frame2, threshold=25):
        """
        Detect motion between two frames.
        
        Args:
            frame1 (numpy.ndarray): First frame
            frame2 (numpy.ndarray): Second frame
            threshold (int): Threshold for motion detection
            
        Returns:
            tuple: (motion_detected, motion_percentage)
        """
        # Convert frames to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Apply threshold
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
        
        # Calculate motion percentage
        motion_pixels = np.count_nonzero(thresh)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        motion_percentage = (motion_pixels / total_pixels) * 100
        
        return motion_percentage > 0.5, motion_percentage
    
    def release(self):
        """Release the video capture object."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None
    
    def __enter__(self):
        """Context manager entry."""
        self.load_video()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
