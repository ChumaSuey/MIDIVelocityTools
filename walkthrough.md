# MIDI Tools Collection

A collection of Python scripts designed to help you manipulate the velocity (volume) of your MIDI files. These tools are perfect for preparing MIDI files for DAWs like FL Studio, ensuring consistent and usable dynamic ranges.

## 1. MIDI Normalizer (Velocity Amplifier)

**Purpose**: Increases the volume of a "quiet" MIDI file so that the loudest note hits the maximum velocity (127). All other notes are scaled proportionally to preserve dynamics.

### Usage
```bash
python MIDINormalizer.py <input_file.mid> [output_file.mid]
```

### Examples
*   **Normalize a file** (saves as `input_normalized.mid`):
    ```bash
    python MIDINormalizer.py my_song.mid
    ```
*   **Specify output name**:
    ```bash
    python MIDINormalizer.py quiet_song.mid loud_song.mid
    ```

---

## 2. MIDI Equalizer (Velocity Scaler)

**Purpose**: Scales the velocity of a MIDI file by a specific percentage. This is ideal for "hot" MIDI files (where everything is 127) that need to be lowered (e.g., to 80%) to prevent clipping or harshness in digital synths.

### Usage
```bash
python MIDIEqualizer.py <input_file.mid> [output_file.mid] [-l LEVEL]
```

*   `-l` or `--level`: Target percentage (integer, default is 80).

### Examples
*   **Scale to 80% (Standard)**:
    ```bash
    python MIDIEqualizer.py my_song.mid
    ```
*   **Scale to 60% (Softer)**:
    ```bash
    python MIDIEqualizer.py my_song.mid -l 60
    ```

## Installation & Setup

1.  Ensure you have Python installed.
2.  Install dependencies:
    ```bash
    pip install pretty_midi
    ```
3.  Navigate to the project folder:
    ```bash
    cd c:/Users/luism/PycharmProjects/MIDINormalizer
    ```
