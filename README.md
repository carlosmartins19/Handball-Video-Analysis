# Handball Video Analysis

A Python-based video analysis system for handball games. This tool processes handball game videos to detect players, track motion, and generate game statistics.

## Features

- **Video Processing**: Load and process handball game videos frame by frame
- **Player Detection**: Detect and track players using background subtraction and motion detection
- **Motion Analysis**: Analyze motion patterns throughout the game
- **Game Statistics**: Generate comprehensive statistics including:
  - Motion detection rates
  - Average motion percentages
  - Player detection counts
  - Frames analyzed

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

### Command Line Arguments

- `video`: Path to the video file to analyze (required)
- `-o, --output`: Path to save analysis results in JSON format (optional)
- `-s, --step`: Process every Nth frame (default: 5, lower values = more accurate but slower)

## Project Structure

```
Handball-Video-Analysis/
├── src/
│   └── handball_analysis/
│       ├── __init__.py
│       ├── video_processor.py    # Video loading and processing
│       ├── player_detector.py    # Player detection and tracking
│       └── statistics.py         # Statistics collection and analysis
├── tests/
│   ├── test_video_processor.py
│   └── test_statistics.py
├── main.py                       # Main application entry point
├── requirements.txt              # Python dependencies
└── README.md
```

## API Usage

You can also use the library programmatically in your own Python scripts:

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

Video Information:
  Resolution: 1920x1080
  FPS: 30
  Frame Count: 900
  Duration: 30.00 seconds

Progress: 100.0%

==================================================
Handball Game Analysis Summary
==================================================
Total Frames: 900
Frames Analyzed: 180
Frames with Motion: 165
Motion Detection Rate: 91.67%
Average Motion Percentage: 12.34%
Total Player Detections: 1250
Average Players per Frame: 6.94
==================================================
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
