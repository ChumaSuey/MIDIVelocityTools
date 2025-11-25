import pretty_midi
import argparse
import sys
import os

def equalize_midi(input_file, output_file=None, level=80):
    """
    Scales the velocity of a MIDI file by a percentage (default 80%).
    Returns a list of strings containing the process log.
    """
    logs = []
    def log(msg):
        logs.append(msg)
        # print(msg) # Optional: print to stdout as well if needed
    try:
        midi_data = pretty_midi.PrettyMIDI(input_file)
    except Exception as e:
        log(f"Error loading MIDI file: {e}")
        return logs

    scale_factor = level / 100.0
    log("-" * 40)
    log(f"Target Level: {level}% (Factor: {scale_factor:.2f})")
    log("-" * 40)

    for instrument in midi_data.instruments:
        # Determine instrument name
        inst_name = instrument.name
        if not inst_name or inst_name.strip() == "":
            try:
                inst_name = pretty_midi.program_to_instrument_name(instrument.program)
            except:
                inst_name = f"Unknown Instrument (Program {instrument.program})"
        
        # Calculate stats before processing
        notes_count = len(instrument.notes)
        if notes_count == 0:
            continue

        old_max = 0
        for note in instrument.notes:
            if note.velocity > old_max:
                old_max = note.velocity
        
        # Apply scaling
        new_max = 0
        for note in instrument.notes:
            new_velocity = int(note.velocity * scale_factor)
            # Clamp to 127, min 1 to keep note active
            note.velocity = min(127, max(1, new_velocity))
            if note.velocity > new_max:
                new_max = note.velocity

        log(f"Instrument: {inst_name}")
        log(f"  - Notes: {notes_count}")
        log(f"  - Max Velocity: {old_max} -> {new_max}")
        log(f"  - Status: Scaled")
        log("-" * 40)

    # Determine output filename
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_equalized{ext}"

    try:
        midi_data.write(output_file)
        log(f"Successfully saved equalized MIDI to: {output_file}")
    except Exception as e:
        log(f"Error saving MIDI file: {e}")
    
    return logs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scale MIDI velocity by a percentage.")
    parser.add_argument("input_file", help="Path to the input MIDI file")
    parser.add_argument("output_file", nargs="?", help="Path to the output MIDI file (optional)")
    parser.add_argument("-l", "--level", type=int, default=80, help="Target velocity percentage (default: 80)")
    
    args = parser.parse_args()
    
    logs = equalize_midi(args.input_file, args.output_file, args.level)
    for line in logs:
        print(line)
