#!/usr/bin/env python3
"""
Handball Video Analysis - Main Application

Analyze handball game videos to extract statistics and detect players.
"""

import argparse
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from handball_analysis import VideoProcessor, PlayerDetector, GameStatistics


def analyze_video(video_path, output_path=None, frame_step=5):
    """
    Analyze a handball video.
    
    Args:
        video_path (str): Path to the video file
        output_path (str): Path to save analysis results (optional)
        frame_step (int): Process every Nth frame
    
    Returns:
        dict: Analysis statistics
    """
    print(f"Analyzing video: {video_path}")
    print(f"Processing every {frame_step} frame(s)...")
    
    # Initialize components
    processor = VideoProcessor(video_path)
    detector = PlayerDetector()
    stats = GameStatistics()
    
    try:
        # Load video and get metadata
        metadata = processor.load_video()
        stats.set_total_frames(metadata['frame_count'])
        
        print(f"\nVideo Information:")
        print(f"  Resolution: {metadata['width']}x{metadata['height']}")
        print(f"  FPS: {metadata['fps']}")
        print(f"  Frame Count: {metadata['frame_count']}")
        print(f"  Duration: {metadata['duration']:.2f} seconds")
        
        # Process frames
        prev_frame = None
        frame_count = 0
        
        for frame_num, frame in processor.extract_frames(step=frame_step):
            frame_count += 1
            
            # Detect motion
            if prev_frame is not None:
                motion_detected, motion_pct = processor.detect_motion(prev_frame, frame)
                stats.update_motion_stats(motion_detected, motion_pct)
            
            # Detect players
            players = detector.detect_players(frame)
            stats.update_player_stats(len(players))
            
            prev_frame = frame
            
            # Progress indicator
            if frame_count % 10 == 0:
                progress = (frame_num / metadata['frame_count']) * 100
                print(f"\rProgress: {progress:.1f}%", end='', flush=True)
        
        print("\rProgress: 100.0%")
        
        # Print summary
        stats.print_summary()
        
        # Save results if output path specified
        if output_path:
            import json
            summary = stats.get_summary()
            summary['video_metadata'] = metadata
            
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"Results saved to: {output_path}")
        
        return stats.get_summary()
        
    finally:
        processor.release()


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='Analyze handball game videos'
    )
    parser.add_argument(
        'video',
        help='Path to the video file to analyze'
    )
    parser.add_argument(
        '-o', '--output',
        help='Path to save analysis results (JSON format)',
        default=None
    )
    parser.add_argument(
        '-s', '--step',
        type=int,
        default=5,
        help='Process every Nth frame (default: 5)'
    )
    
    args = parser.parse_args()
    
    # Check if video file exists
    if not os.path.isfile(args.video):
        print(f"Error: Video file not found: {args.video}")
        return 1
    
    try:
        analyze_video(args.video, args.output, args.step)
        return 0
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
