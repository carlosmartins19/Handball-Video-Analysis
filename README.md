# Handball Video Analysis

A Python-based video analysis system for handball games. This tool processes handball game videos to detect players, track motion, and generate game statistics.

## Features

- **Video Processing**: Load and process handball game videos frame by frame
- **Player Detection & Tracking**: Detect and track individual players using background subtraction and centroid tracking
- **Motion Analysis**: Analyze motion patterns throughout the game
- **Event Detection**: Automatically detect game events including:
  - Goals scored
  - Shots taken
  - Passes (successful and unsuccessful)
  - Ball possession
  - Possession changes
- **Comprehensive Statistics**: Generate detailed statistics including:
  - **General**: Motion detection rates, player counts, frames analyzed
  - **Team Stats**: Total goals, shots, passes, bad passes, possession changes
  - **Per-Player Stats**:
    - Goals scored
    - Shots taken
    - Passes made and received
    - Bad passes
    - Possession time
    - Distance covered
    - Average movement speed

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/carlosmartins19/Handball-Video-Analysis.git
cd Handball-Video-Analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Analyze a handball video:

```bash
python main.py path/to/your/video.mp4
```

### Advanced Options

Save analysis results to a JSON file:

```bash
python main.py path/to/your/video.mp4 -o results.json
```

Process every Nth frame (for faster analysis):

```bash
python main.py path/to/your/video.mp4 --step 10
```

Disable advanced tracking for faster processing:

```bash
python main.py path/to/your/video.mp4 --no-tracking
```

### Command Line Arguments

- `video`: Path to the video file to analyze (required)
- `-o, --output`: Path to save analysis results in JSON format (optional)
- `-s, --step`: Process every Nth frame (default: 5, lower values = more accurate but slower)
- `--no-tracking`: Disable advanced player tracking and event detection (faster but less detailed)

## Project Structure

```
Handball-Video-Analysis/
├── src/
│   └── handball_analysis/
│       ├── __init__.py
│       ├── video_processor.py    # Video loading and processing
│       ├── player_detector.py    # Player detection using background subtraction
│       ├── player_tracker.py     # Individual player tracking across frames
│       ├── event_detector.py     # Event detection (goals, passes, shots)
│       └── statistics.py         # Statistics collection and analysis
├── tests/
│   ├── test_video_processor.py
│   └── test_statistics.py
├── main.py                       # Main application entry point
├── example.py                    # Example usage script
├── requirements.txt              # Python dependencies
└── README.md
```

## API Usage

You can also use the library programmatically in your own Python scripts:

### Basic Usage (Player Detection Only)

```python
from handball_analysis import VideoProcessor, PlayerDetector, GameStatistics

# Initialize components
processor = VideoProcessor('game.mp4')
detector = PlayerDetector()
stats = GameStatistics()

# Load video
metadata = processor.load_video()
stats.set_total_frames(metadata['frame_count'])

# Process frames
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

# Get results
summary = stats.get_summary()
stats.print_summary()

# Clean up
processor.release()
```

### Advanced Usage (With Player Tracking and Events)

```python
from handball_analysis import (
    VideoProcessor, PlayerDetector, GameStatistics,
    PlayerTracker, EventDetector
)

# Initialize components
processor = VideoProcessor('game.mp4')
detector = PlayerDetector()
tracker = PlayerTracker()
event_detector = EventDetector()
stats = GameStatistics()

# Load video
metadata = processor.load_video()
stats.set_total_frames(metadata['frame_count'])

prev_frame = None
prev_possession = None

for frame_num, frame in processor.extract_frames(step=5):
    # Detect and track players
    player_boxes = detector.detect_players(frame)
    tracked_players = tracker.update(player_boxes)

    # Detect ball and events
    ball_pos = event_detector.detect_ball(frame)
    if ball_pos:
        event_detector.ball_tracker.update(ball_pos)

    # Detect possession
    possession = event_detector.detect_possession(ball_pos, tracked_players)
    if possession:
        stats.update_player_possession(possession)

    # Detect passes
    if prev_possession and possession and prev_possession != possession:
        ball_movement = event_detector.ball_tracker.get_movement()
        pass_event = event_detector.detect_pass(prev_possession, possession, ball_movement)
        if pass_event:
            stats.record_event(pass_event)

    prev_possession = possession
    prev_frame = frame

# Print comprehensive statistics
stats.print_summary()
processor.release()
```

## Running the Example

Try out the included example that creates a sample video and analyzes it:

```bash
python example.py
```

This will demonstrate the library's capabilities by:
1. Creating a sample video with moving objects
2. Analyzing the video
3. Displaying statistics
4. Cleaning up temporary files

## Running Tests

Run the test suite:

```bash
python -m pytest tests/
```

Or run tests individually:

```bash
python tests/test_video_processor.py
python tests/test_statistics.py
```

## Example Output

```
Analyzing video: handball_game.mp4
Processing every 5 frame(s)...
Advanced player tracking and event detection: ENABLED

Video Information:
  Resolution: 1920x1080
  FPS: 30
  Frame Count: 900
  Duration: 30.00 seconds

Progress: 100.0%

======================================================================
Handball Game Analysis Summary
======================================================================

--- General Statistics ---
Total Frames: 900
Frames Analyzed: 180
Frames with Motion: 165
Motion Detection Rate: 91.67%
Average Motion Percentage: 12.34%
Total Player Detections: 1250
Average Players per Frame: 6.94

--- Team Statistics ---
Total Goals: 5
Total Shots: 23
Total Passes: 87
Bad Passes: 12
Possession Changes: 45

--- Player Statistics ---

player_0:
  Goals: 2
  Shots: 8
  Passes Made: 15
  Passes Received: 18
  Bad Passes: 3
  Possession Frames: 45
  Distance Covered: 1250.50 pixels
  Average Speed: 15.25 pixels/frame

player_1:
  Goals: 1
  Shots: 5
  Passes Made: 20
  Passes Received: 15
  Bad Passes: 2
  Possession Frames: 38
  Distance Covered: 1100.75 pixels
  Average Speed: 13.50 pixels/frame

[Additional players...]

======================================================================
```

## Technology Stack

- **OpenCV**: Video processing and computer vision
- **NumPy**: Numerical computations
- **Python**: Core programming language

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Author

Carlos Martins (@carlosmartins19)
