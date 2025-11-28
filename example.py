#!/usr/bin/env python3
"""
Example script demonstrating how to use the Handball Video Analysis library.
"""

import sys
import os
import numpy as np
import cv2

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from handball_analysis import VideoProcessor, PlayerDetector, GameStatistics


def create_sample_video(output_path='sample_video.mp4', duration=2):
    """
    Create a simple sample video for testing purposes.
    
    Args:
        output_path (str): Path where to save the video
        duration (int): Duration in seconds
    """
    print(f"Creating sample video: {output_path}")
    
    # Video parameters
    fps = 30
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Generate frames with moving objects
    for i in range(fps * duration):
        # Create a blank frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (50, 50, 50)  # Gray background
        
        # Add moving circles (simulating players)
        for j in range(3):
            x = int((width // 4) + (i * 5 + j * 100) % (width // 2))
            y = int(height // 2 + 50 * np.sin(i / 10 + j))
            cv2.circle(frame, (x, y), 20, (0, 255, 0), -1)
        
        out.write(frame)
    
    out.release()
    print(f"Sample video created: {output_path}")
    return output_path


def analyze_sample_video():
    """Analyze a sample video to demonstrate the library functionality."""
    # Create sample video
    video_path = create_sample_video()
    
    try:
        print("\n" + "="*60)
        print("Running Handball Video Analysis Example")
        print("="*60)
        
        # Initialize components
        processor = VideoProcessor(video_path)
        detector = PlayerDetector()
        stats = GameStatistics()
        
        # Load video
        metadata = processor.load_video()
        stats.set_total_frames(metadata['frame_count'])
        
        print(f"\nVideo Metadata:")
        print(f"  Resolution: {metadata['width']}x{metadata['height']}")
        print(f"  FPS: {metadata['fps']}")
        print(f"  Frame Count: {metadata['frame_count']}")
        print(f"  Duration: {metadata['duration']:.2f} seconds")
        
        # Process frames
        print(f"\nProcessing frames...")
        prev_frame = None
        
        for frame_num, frame in processor.extract_frames(step=5):
            # Detect motion
            if prev_frame is not None:
                motion_detected, motion_pct = processor.detect_motion(prev_frame, frame)
                stats.update_motion_stats(motion_detected, motion_pct)
            
            # Detect players
            players = detector.detect_players(frame)
            stats.update_player_stats(len(players))
            
            prev_frame = frame
        
        # Display results
        stats.print_summary()
        
        # Clean up
        processor.release()
        
        print("\nExample completed successfully!")
        print("="*60)
        
    finally:
        # Clean up sample video
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"\nCleaned up sample video: {video_path}")


if __name__ == '__main__':
    print("Handball Video Analysis - Example Usage\n")
    analyze_sample_video()
