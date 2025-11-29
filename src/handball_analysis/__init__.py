"""
Handball Video Analysis Package

A Python package for analyzing handball game videos.
"""

__version__ = "0.1.0"

from .video_processor import VideoProcessor
from .player_detector import PlayerDetector
from .statistics import GameStatistics

__all__ = ['VideoProcessor', 'PlayerDetector', 'GameStatistics']
