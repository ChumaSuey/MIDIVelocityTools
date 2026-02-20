# MIDI Velocity Tools

A simple yet powerful set of tools to manage MIDI note velocities. This project includes a **Normalizer** to maximize the volume of your MIDI files and an **Equalizer** to scale velocities by a percentage.

## Features

### 🎹 MIDI Normalizer

Scales all note velocities so the loudest note in the file reaches a target value (default: 127).

- **Muted Channel Filtering**: Automatically detects tracks with Volume (CC7) set to 0 and ignores them for the global maximum calculation. This ensures silent tracks with high-velocity data don't prevent your active tracks from being normalized.
- **Phantom Note Filtering**: Allows setting a minimum velocity threshold to ignore transients or noise during the normalization process.
- **Batch Processing Support**: Designed to work with the provided CLI scripts and GUI.

### 🛠️ MIDI Fixes (Sanitize)

A utility to "clean" MIDI files by re-writing them from scratch. This forces a fresh assignment of channels and tracks, which can resolve:

- **Channel Conflicts**: When multiple instruments accidentally share the same MIDI channel.
- **Uninitialized State**: When tracks rely on previous state instead of explicit events.
- **Corrupted Headers**: General file structure issues.

## Project Structure

- `MIDINormalizer.py`: Core logic for MIDI normalization.
- `MIDIEqualizer.py`: Core logic for MIDI velocity scaling.
- `MIDIFixes.py`: Logic for sanitizing and fixing MIDI channel assignments.
- `GUI.py`: Graphical user interface for all tools (now with Dark Mode!).
- `tests/`: Verification scripts for automated testing.
- `tests_MIDIs/`: Sample MIDI files for testing and demonstration.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ChumaSuey/MIDIVelocityTools.git
   ```

2. Install the required dependencies:

   ```bash
   pip install pretty_midi sv-ttk
   ```

## Usage

### Using the GUI (Recommended)

Launch the graphical interface:

```bash
python GUI.py
```

- **Modern Dark Theme**: The GUI now features a sleek "Sun Valley" dark theme.
- **Normalize**: select your file and hitting "Normalize".
- **Equalize**: Scale velocity (Default is now **70%**).
- **Sanitize**: Click "Sanitize / Fix Channels" to repair problematic MIDI files.

### Using the CLI

You can also run the scripts directly:

**Normalize:**

```bash
python MIDINormalizer.py input.mid [output.mid]
```

**Equalize:**

```bash
python MIDIEqualizer.py input.mid [output.mid] --level 70
```

**Sanitize:**

```bash
python MIDIFixes.py input.mid [output.mid]
```

## Requirements

- Python 3.x
- `pretty_midi` library

## Credits

Built with love for MIDI enthusiasts. 🎹✨
