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

from handball_analysis import (
    VideoProcessor,
    PlayerDetector,
    GameStatistics,
    PlayerTracker,
    EventDetector
)


def analyze_video(video_path, output_path=None, frame_step=5, enable_advanced_tracking=True):
    """
    Analyze a handball video.

    Args:
        video_path (str): Path to the video file
        output_path (str): Path to save analysis results (optional)
        frame_step (int): Process every Nth frame
        enable_advanced_tracking (bool): Enable player tracking and event detection

    Returns:
        dict: Analysis statistics
    """
    print(f"Analyzing video: {video_path}")
    print(f"Processing every {frame_step} frame(s)...")
    if enable_advanced_tracking:
        print("Advanced player tracking and event detection: ENABLED")

    # Initialize components
    processor = VideoProcessor(video_path)
    detector = PlayerDetector()
    stats = GameStatistics()

    # Advanced tracking components
    tracker = PlayerTracker() if enable_advanced_tracking else None
    event_detector = EventDetector() if enable_advanced_tracking else None

    try:
        # Load video and get metadata
        metadata = processor.load_video()
        stats.set_total_frames(metadata['frame_count'])

        print(f"\nVideo Information:")
        print(f"  Resolution: {metadata['width']}x{metadata['height']}")
        print(f"  FPS: {metadata['fps']}")
        print(f"  Frame Count: {metadata['frame_count']}")
        print(f"  Duration: {metadata['duration']:.2f} seconds")

        # Define goal regions (approximate positions, can be adjusted)
        # Format: (x1, y1, x2, y2) - top-left and bottom-right corners
        goal_regions = [
            (0, metadata['height'] // 3, 100, 2 * metadata['height'] // 3),  # Left goal
            (metadata['width'] - 100, metadata['height'] // 3, metadata['width'], 2 * metadata['height'] // 3)  # Right goal
        ]

        # Process frames
        prev_frame = None
        frame_count = 0
        prev_possession = None
        prev_player_positions = {}

        for frame_num, frame in processor.extract_frames(step=frame_step):
            frame_count += 1

            # Detect motion
            if prev_frame is not None:
                motion_detected, motion_pct = processor.detect_motion(prev_frame, frame)
                stats.update_motion_stats(motion_detected, motion_pct)

            # Detect players
            player_boxes = detector.detect_players(frame)
            stats.update_player_stats(len(player_boxes))

            if enable_advanced_tracking and tracker and event_detector:
                # Track individual players
                tracked_players = tracker.update(player_boxes)

                # Detect ball
                ball_pos = event_detector.detect_ball(frame)

                if ball_pos:
                    event_detector.ball_tracker.update(ball_pos)

                # Detect possession
                current_possession = event_detector.detect_possession(ball_pos, tracked_players)

                if current_possession is not None:
                    stats.update_player_possession(current_possession)

                # Detect pass
                if prev_possession is not None and current_possession is not None:
                    ball_movement = event_detector.ball_tracker.get_movement()
                    pass_event = event_detector.detect_pass(prev_possession, current_possession, ball_movement)

                    if pass_event:
                        stats.record_event(pass_event)

                    # Detect possession change
                    if prev_possession != current_possession:
                        stats.record_event({
                            'type': 'possession_change',
                            'from_player': prev_possession,
                            'to_player': current_possession,
                            'frame': frame_num
                        })

                # Detect shot
                if current_possession is not None:
                    ball_velocity = event_detector.ball_tracker.get_velocity()
                    shot_event = event_detector.detect_shot(current_possession, ball_velocity, goal_regions)

                    if shot_event:
                        shot_event['frame'] = frame_num
                        stats.record_event(shot_event)

                # Detect goal
                goal_event = event_detector.detect_goal(
                    ball_pos,
                    goal_regions,
                    event_detector.ball_tracker.get_velocity()
                )

                if goal_event:
                    goal_event['frame'] = frame_num
                    if current_possession is not None:
                        goal_event['player'] = current_possession
                    stats.record_event(goal_event)

                # Track player movement
                for player_id, (x, y, w, h) in tracked_players.items():
                    current_pos = (x + w // 2, y + h // 2)

                    if player_id in prev_player_positions:
                        prev_pos = prev_player_positions[player_id]
                        movement = event_detector.analyze_player_movement(player_id, current_pos, prev_pos)

                        if movement:
                            stats.update_player_movement(
                                player_id,
                                movement['distance'],
                                movement['speed']
                            )

                    prev_player_positions[player_id] = current_pos

                prev_possession = current_possession

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
        description='Analyze handball game videos with player tracking and statistics'
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
    parser.add_argument(
        '--no-tracking',
        action='store_true',
        help='Disable advanced player tracking and event detection (faster but less detailed)'
    )

    args = parser.parse_args()

    # Check if video file exists
    if not os.path.isfile(args.video):
        print(f"Error: Video file not found: {args.video}")
        return 1

    try:
        analyze_video(
            args.video,
            args.output,
            args.step,
            enable_advanced_tracking=not args.no_tracking
        )
        return 0
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
