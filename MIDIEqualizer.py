import mido
import pretty_midi
import argparse
import sys
import os

def equalize_midi(input_file, output_file=None, level=80):
    """
    Scales the velocity of a MIDI file by a percentage (default 80%).
    Processes losslessly via mido and returns a list of log strings.
    """
    logs = []
    def log(msg):
        logs.append(msg)

    try:
        midi_data = mido.MidiFile(input_file)
    except Exception as e:
        log(f"Error loading MIDI file: {e}")
        return logs

    scale_factor = level / 100.0
    log("-" * 40)
    log(f"Target Level: {level}% (Factor: {scale_factor:.2f})")
    log("-" * 40)

    for i, track in enumerate(midi_data.tracks):
        track_name = None
        programs = set()
        notes_count = 0
        old_max = 0
        new_max = 0

        for msg in track:
            if msg.type == 'track_name':
                track_name = msg.name
            elif msg.type == 'program_change':
                programs.add(msg.program)

        if not track_name:
            if programs:
                program_names = []
                for p in sorted(programs):
                    try:
                        program_names.append(pretty_midi.program_to_instrument_name(p))
                    except:
                        program_names.append(f"Instrument {p}")
                track_name = f"Track {i} (" + ", ".join(program_names) + ")"
            else:
                track_name = f"Track {i}"

        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                notes_count += 1
                if msg.velocity > old_max:
                    old_max = msg.velocity

                new_velocity = int(round(msg.velocity * scale_factor))
                msg.velocity = min(127, max(1, new_velocity))

                if msg.velocity > new_max:
                    new_max = msg.velocity

        if notes_count > 0:
            log(f"Track: {track_name}")
            log(f"  - Notes: {notes_count}")
            log(f"  - Max Velocity: {old_max} -> {new_max}")
            log(f"  - Status: Scaled")
            log("-" * 40)

    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_equalized{ext}"

    try:
        midi_data.save(output_file)
        log(f"Successfully saved equalized MIDI to: {output_file}")
    except Exception as e:
        log(f"Error saving MIDI file: {e}")

    return logs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scale MIDI velocity by a percentage.")
    parser.add_argument("input_file", help="Path to the input MIDI file")
    parser.add_argument("output_file", nargs="?", help="Path to the output MIDI file (optional)")
    parser.add_argument("--level", type=float, default=80.0, help="Scaling percentage (default: 80.0)")
    
    args = parser.parse_argument_values() if hasattr(parser, 'parse_argument_values') else parser.parse_args()
    
    results = equalize_midi(args.input_file, args.output_file, args.level)
    for line in results:
        print(line)