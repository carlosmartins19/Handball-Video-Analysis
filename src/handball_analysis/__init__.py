"""
Handball Video Analysis Package

A Python package for analyzing handball game videos.
"""

__version__ = "0.2.0"

from .video_processor import VideoProcessor
from .player_detector import PlayerDetector
from .statistics import GameStatistics
from .player_tracker import PlayerTracker
from .event_detector import EventDetector

__all__ = [
    'VideoProcessor',
    'PlayerDetector',
    'GameStatistics',
    'PlayerTracker',
    'EventDetector'
]
