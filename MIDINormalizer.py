import pretty_midi
import argparse
import sys
import os

def normalize_midi(input_file, output_file=None, target_velocity=127, ignore_muted=True, velocity_threshold=0):
    """
    Normalizes the velocity of a MIDI file so the loudest note hits target_velocity (default 127).
    ignore_muted: If True, skips instruments where all Volume (CC7) events are 0.
    velocity_threshold: Notes with velocity <= this value are ignored for max calculation (phantom note filtering).
    Returns a list of strings containing the process log.
    """
    logs = []
    def log(msg):
        logs.append(msg)
        # print(msg) # Optional: print to stdout as well if needed, but we'll handle it in main
    try:
        midi_data = pretty_midi.PrettyMIDI(input_file)
    except Exception as e:
        log(f"Error loading MIDI file: {e}")
        return logs

    # Find the global maximum velocity
    max_velocity = 0
    
    for instrument in midi_data.instruments:
        # Determine instrument name for logging
        inst_name = instrument.name
        if not inst_name or inst_name.strip() == "":
            try:
                inst_name = pretty_midi.program_to_instrument_name(instrument.program)
            except:
                inst_name = f"Unknown Instrument (Program {instrument.program})"

        # Check for muted instrument
        if ignore_muted:
            cc7_events = [cc for cc in instrument.control_changes if cc.number == 7]
            # If there are volume events and the maximum volume is 0, consider it muted
            if cc7_events and max(cc.value for cc in cc7_events) == 0:
                log(f"Skipping muted instrument for max velocity calc: {inst_name}")
                continue

        for note in instrument.notes:
            if note.velocity <= velocity_threshold:
                continue
            if note.velocity > max_velocity:
                max_velocity = note.velocity

    if max_velocity == 0:
        log("Warning: Max velocity is 0. Is the MIDI file empty?")
        return logs
    
    if max_velocity == target_velocity:
        log(f"MIDI file is already normalized (max velocity is {target_velocity}).")
        # We can still save it if the user wants, or just return
        # For now, let's proceed to save a copy anyway to be consistent
        scale_factor = 1.0
    else:
        scale_factor = target_velocity / max_velocity
        log(f"Max velocity found: {max_velocity}. Scaling by {scale_factor:.2f} to target {target_velocity}...")

    # Apply scaling and report
    log("-" * 40)
    log(f"Global scaling factor: {scale_factor:.3f}")
    log("-" * 40)

    for instrument in midi_data.instruments:
        # Determine instrument name
        inst_name = instrument.name
        if not inst_name or inst_name.strip() == "":
            try:
                inst_name = pretty_midi.program_to_instrument_name(instrument.program)
            except:
                inst_name = f"Unknown Instrument (Program {instrument.program})"
        
        # Calculate stats before normalization
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
            # Clamp to 127
            note.velocity = min(127, max(1, new_velocity))
            if note.velocity > new_max:
                new_max = note.velocity

        log(f"Instrument: {inst_name}")
        log(f"  - Notes: {notes_count}")
        log(f"  - Max Velocity: {old_max} -> {new_max}")
        log(f"  - Status: Normalized")
        log("-" * 40)

    # Determine output filename
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_normalized{ext}"

    try:
        midi_data.write(output_file)
        log(f"Successfully saved normalized MIDI to: {output_file}")
    except Exception as e:
        log(f"Error saving MIDI file: {e}")
    
    return logs

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python MIDINormalizer.py <input_midi_file> [output_midi_file]")
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        # Check for optional target velocity arg if we wanted to be fancy, but keeping it simple for now
        # CLI usage doesn't expose the new flags yet directly, assuming default behavior or simple expansion if needed later
        logs = normalize_midi(input_path, output_path)
        for line in logs:
            print(line)
