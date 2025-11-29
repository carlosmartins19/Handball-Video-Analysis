"""
Tests for Statistics Module
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from handball_analysis.statistics import GameStatistics


class TestGameStatistics(unittest.TestCase):
    """Test cases for GameStatistics class."""
    
    def test_init(self):
        """Test GameStatistics initialization."""
        stats = GameStatistics()
        self.assertEqual(stats.stats['total_frames'], 0)
        self.assertEqual(stats.stats['frames_with_motion'], 0)
        self.assertEqual(stats.stats['frames_analyzed'], 0)
    
    def test_update_motion_stats(self):
        """Test updating motion statistics."""
        stats = GameStatistics()
        
        stats.update_motion_stats(True, 15.5)
        self.assertEqual(stats.stats['frames_with_motion'], 1)
        self.assertEqual(stats.stats['frames_analyzed'], 1)
        self.assertEqual(stats.stats['average_motion_percentage'], 15.5)
        
        stats.update_motion_stats(False, 0.2)
        self.assertEqual(stats.stats['frames_with_motion'], 1)
        self.assertEqual(stats.stats['frames_analyzed'], 2)
        self.assertAlmostEqual(stats.stats['average_motion_percentage'], 7.85)
    
    def test_update_player_stats(self):
        """Test updating player statistics."""
        stats = GameStatistics()
        
        stats.update_player_stats(5)
        self.assertEqual(stats.stats['total_player_detections'], 5)
        
        stats.update_player_stats(3)
        self.assertEqual(stats.stats['total_player_detections'], 8)
    
    def test_set_total_frames(self):
        """Test setting total frames."""
        stats = GameStatistics()
        stats.set_total_frames(1000)
        self.assertEqual(stats.stats['total_frames'], 1000)
    
    def test_get_summary(self):
        """Test getting statistics summary."""
        stats = GameStatistics()
        stats.set_total_frames(100)
        stats.update_motion_stats(True, 10.0)
        stats.update_motion_stats(True, 20.0)
        stats.update_player_stats(5)
        stats.update_player_stats(3)
        
        summary = stats.get_summary()
        
        self.assertEqual(summary['total_frames'], 100)
        self.assertEqual(summary['frames_analyzed'], 2)
        self.assertEqual(summary['frames_with_motion'], 2)
        self.assertEqual(summary['motion_detection_rate'], 100.0)
        self.assertEqual(summary['average_motion_percentage'], 15.0)
        self.assertEqual(summary['total_player_detections'], 8)
        self.assertEqual(summary['average_players_per_frame'], 4.0)
    
    def test_get_summary_no_analysis(self):
        """Test getting summary with no frames analyzed."""
        stats = GameStatistics()
        summary = stats.get_summary()
        
        self.assertEqual(summary['motion_detection_rate'], 0.0)
        self.assertEqual(summary['average_players_per_frame'], 0.0)


if __name__ == '__main__':
    unittest.main()
