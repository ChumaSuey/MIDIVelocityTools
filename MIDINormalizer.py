import mido
import pretty_midi
import argparse
import sys
import os

def normalize_midi(input_file, output_file=None, target_velocity=127, ignore_muted=True, velocity_threshold=0):
    """
    Normalizes the velocity of a MIDI file so the loudest note hits target_velocity.
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

    muted_channels = set()
    if ignore_muted:
        cc7_values = {}
        for track in midi_data.tracks:
            for msg in track:
                if msg.type == 'control_change' and msg.control == 7:
                    cc7_values.setdefault(msg.channel, []).append(msg.value)
        
        for channel, values in cc7_values.items():
            if values and max(values) == 0:
                muted_channels.add(channel)
                log(f"Skipping muted channel: {channel + 1}")

    global_max = 0
    for track in midi_data.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > velocity_threshold:
                if msg.channel not in muted_channels:
                    if msg.velocity > global_max:
                        global_max = msg.velocity

    log("-" * 40)
    log(f"Global Max Velocity Found: {global_max}")
    log("-" * 40)

    if global_max == 0:
        log("Warning: No valid notes found above threshold. No normalization applied.")
        scale_factor = 1.0
    else:
        scale_factor = target_velocity / float(global_max)

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

                if msg.channel not in muted_channels and msg.velocity > velocity_threshold:
                    new_velocity = int(round(msg.velocity * scale_factor))
                    msg.velocity = min(127, max(1, new_velocity))
                
                if msg.velocity > new_max:
                    new_max = msg.velocity

        if notes_count > 0:
            log(f"Track: {track_name}")
            log(f"  - Notes: {notes_count}")
            log(f"  - Max Velocity: {old_max} -> {new_max}")
            log(f"  - Status: Normalized")
            log("-" * 40)

    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_normalized{ext}"

    try:
        midi_data.save(output_file)
        log(f"Successfully saved normalized MIDI to: {output_file}")
    except Exception as e:
        log(f"Error saving MIDI file: {e}")

    return logs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize MIDI velocity.")
    parser.add_argument("input_file", help="Path to the input MIDI file")
    parser.add_argument("output_file", nargs="?", help="Path to the output MIDI file (optional)")
    parser.add_argument("--target_velocity", type=int, default=127, help="Target maximum velocity (default: 127)")
    parser.add_argument("--ignore_muted", type=bool, default=True, help="Ignore muted channels (default: True)")
    parser.add_argument("--velocity_threshold", type=int, default=0, help="Ignore notes at or below this velocity (default: 0)")
    
    args = parser.parse_args()
    
    results = normalize_midi(args.input_file, args.output_file, args.target_velocity, args.ignore_muted, args.velocity_threshold)
    for line in results:
        print(line)