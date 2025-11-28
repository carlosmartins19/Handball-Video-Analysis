"""
Statistics Module

Handles game statistics collection and analysis.
"""

import numpy as np


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
    
    def get_summary(self):
        """
        Get a summary of the collected statistics.
        
        Returns:
            dict: Statistics summary
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
        
        return summary
    
    def print_summary(self):
        """Print a formatted summary of statistics."""
        summary = self.get_summary()
        
        print("\n" + "="*50)
        print("Handball Game Analysis Summary")
        print("="*50)
        print(f"Total Frames: {summary['total_frames']}")
        print(f"Frames Analyzed: {summary['frames_analyzed']}")
        print(f"Frames with Motion: {summary['frames_with_motion']}")
        print(f"Motion Detection Rate: {summary['motion_detection_rate']:.2f}%")
        print(f"Average Motion Percentage: {summary['average_motion_percentage']:.2f}%")
        print(f"Total Player Detections: {summary['total_player_detections']}")
        print(f"Average Players per Frame: {summary['average_players_per_frame']:.2f}")
        print("="*50 + "\n")
