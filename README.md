# MIDI Velocity Tools

A simple yet powerful set of tools to manage MIDI note velocities. This project includes a **Normalizer** to maximize the volume of your MIDI files and an **Equalizer** to scale velocities by a percentage.

## Features

### 🎹 MIDI Normalizer

Scales all note velocities so the loudest note in the file reaches a target value (default: 127).

- **Muted Channel Filtering**: Automatically detects tracks with Volume (CC7) set to 0 and ignores them for the global maximum calculation. This ensures silent tracks with high-velocity data don't prevent your active tracks from being normalized.
- **Phantom Note Filtering**: Allows setting a minimum velocity threshold to ignore transients or noise during the normalization process.

### 🎚️ MIDI Equalizer

Scales all note velocities by a fixed percentage (e.g., 80% of original volume). Useful for balancing tracks or bringing down the overall volume of a MIDI file.

### 🖥️ User-Friendly GUI

Includes a Python-based graphical interface for easy file processing without using the command line.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ChumaSuey/MIDIVelocityTools.git
   ```

2. Install the required dependencies:

   ```bash
   pip install pretty_midi
   ```

## Usage

### Using the GUI (Recommended)

Launch the graphical interface:

```bash
python GUI.py
```

- Select your MIDI file.
- Choose between **Normalize** or **Equalize**.
- Adjust advanced options like "Ignore Muted Channels" or "Velocity Threshold" as needed.

### Using the CLI

You can also run the scripts directly:

**Normalize:**

```bash
python MIDINormalizer.py input.mid [output.mid]
```

**Equalize:**

```bash
python MIDIEqualizer.py input.mid [output.mid] --level 80
```

## Requirements

- Python 3.x
- `pretty_midi` library

## Credits

Built with love for MIDI enthusiasts. 🎹✨
