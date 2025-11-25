# MIDI Normalizer & Equalizer GUI Walkthrough

I have created a GUI for your MIDI Normalizer and Equalizer tools. This allows you to easily select files and apply normalization or equalization with custom settings.

## Files Created/Modified

- **`GUI.py`**: The new graphical user interface. Includes a fix for `TclError` by dynamically locating Tcl/Tk libraries.
- **`MIDINormalizer.py`**: Refactored to return logs and accept a target velocity.
- **`MIDIEqualizer.py`**: Refactored to return logs.

## How to Use the GUI

1.  **Run the GUI**:
    Open your terminal or IDE and run the `GUI.py` file:
    ```bash
    python GUI.py
    ```

2.  **Select a MIDI File**:
    - Click the **Browse** button to select a `.mid` or `.midi` file from your computer.
    - The path will appear in the "Input MIDI" field.

3.  **Optional: Output Name**:
    - If you want to specify a custom output filename, enter it in the "Output Name" field.
    - If left blank, the tool will automatically generate a name (e.g., `filename_normalized.mid`).

4.  **Normalize**:
    - Adjust the "Normalize Target Velocity" if desired (default is 127).
    - Click the **Normalize** button.
    - The logs and statistics (notes count, velocity changes) will appear in the "Logs & Stats" area.

5.  **Equalize**:
    - Adjust the "Equalize Level (%)" if desired (default is 80%).
    - Click the **Equalize** button.
    - The logs and statistics will appear in the "Logs & Stats" area.

## Features

- **Portable**: Automatically detects Tcl/Tk libraries to prevent errors on Windows.
- **Threaded Processing**: The GUI remains responsive while processing large MIDI files.
- **Visual Feedback**: You can see exactly what changes were made to each instrument.
- **Customizable**: You can fine-tune the normalization target and equalization level.

Enjoy your new MIDI tools!
