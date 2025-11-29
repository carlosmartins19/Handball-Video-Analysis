"""
Tests for Video Processor Module
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from handball_analysis.video_processor import VideoProcessor


class TestVideoProcessor(unittest.TestCase):
    """Test cases for VideoProcessor class."""
    
    @patch('handball_analysis.video_processor.cv2.VideoCapture')
    def test_init(self, mock_capture):
        """Test VideoProcessor initialization."""
        processor = VideoProcessor('test_video.mp4')
        self.assertEqual(processor.video_path, 'test_video.mp4')
        self.assertIsNone(processor.capture)
        self.assertEqual(processor.fps, 0)
        self.assertEqual(processor.frame_count, 0)
    
    @patch('handball_analysis.video_processor.cv2.VideoCapture')
    def test_load_video_success(self, mock_capture_class):
        """Test successful video loading."""
        # Setup mock
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.get.side_effect = [30, 900, 1920, 1080]  # fps, frames, width, height
        mock_capture_class.return_value = mock_capture
        
        processor = VideoProcessor('test_video.mp4')
        metadata = processor.load_video()
        
        self.assertEqual(metadata['fps'], 30)
        self.assertEqual(metadata['frame_count'], 900)
        self.assertEqual(metadata['width'], 1920)
        self.assertEqual(metadata['height'], 1080)
        self.assertEqual(metadata['duration'], 30.0)
    
    @patch('handball_analysis.video_processor.cv2.VideoCapture')
    def test_load_video_failure(self, mock_capture_class):
        """Test video loading failure."""
        # Setup mock
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = False
        mock_capture_class.return_value = mock_capture
        
        processor = VideoProcessor('invalid_video.mp4')
        
        with self.assertRaises(ValueError):
            processor.load_video()
    
    @patch('handball_analysis.video_processor.cv2.VideoCapture')
    def test_detect_motion(self, mock_capture):
        """Test motion detection between frames."""
        processor = VideoProcessor('test_video.mp4')
        
        # Create test frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2[40:60, 40:60] = 255  # Add white square
        
        motion_detected, motion_pct = processor.detect_motion(frame1, frame2)
        
        self.assertTrue(motion_detected)
        self.assertGreater(motion_pct, 0)
    
    @patch('handball_analysis.video_processor.cv2.VideoCapture')
    def test_release(self, mock_capture_class):
        """Test video capture release."""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture_class.return_value = mock_capture
        
        processor = VideoProcessor('test_video.mp4')
        processor.load_video()
        processor.release()
        
        mock_capture.release.assert_called_once()
        self.assertIsNone(processor.capture)


if __name__ == '__main__':
    unittest.main()
