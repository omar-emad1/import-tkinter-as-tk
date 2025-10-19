# RMS Mouse Recorder

A simple, stylish GUI tool to record and play back mouse events on Windows, with configurable repeat/playback options and keyboard hotkey triggers.

## Features

- **Record mouse clicks/positions**
- **Playback with multiple repeat modes:**  
  - Play once
  - Repeat a chosen number of times
  - Repeat for a set duration (seconds)
  - Repeat until manually stopped
- **Keyboard hotkeys**  
  - `F9` to start/stop recording
  - `F10` to start/stop playback
- **Save & load sessions** to `.rms` files
- **Modern UI** built with Tkinter

## Quick Start

1. **Clone the repo:**  
   `git clone https://github.com/omar-emad1/import-tkinter-as-tk.git`

2. **Install requirements:**  
   `pip install -r requirements.txt`

3. **Run the app:**  
   `python import-tkinter-as-tk.py`

## Usage

- Click **Record** or press `F9` to start/stop recording your mouse activity.
- Click **Play** or press `F10` to play back recorded clicks.
- Set playback options:
  - Once
  - X times
  - For Y seconds
  - Until manually stopped
- Save recordings to `.rms` files for future use, or load previous sessions.

## Dependencies

- `tkinter` (built-in on most Python installations)
- `pynput`
- `pickle`

See [requirements.txt](requirements.txt).

## License

MIT (see LICENSE)
