import pretty_midi
import argparse
import sys
import os

def fix_midi(input_file, output_file=None):
    """
    Sanitizes channel assignments via sequential track rebuild logic.
    Explicitly copies core time signature, key signature, and lyrics metadata.
    """
    logs = []
    def log(msg):
        logs.append(msg)

    try:
        source_midi = pretty_midi.PrettyMIDI(input_file)
    except Exception as e:
        log(f"Error loading MIDI file: {e}")
        return logs

    target_midi = pretty_midi.PrettyMIDI()

    log(f"Processing: {input_file}")
    log("-" * 40)

    count_melodic = sum(1 for i in source_midi.instruments if not i.is_drum)
    count_drums = sum(1 for i in source_midi.instruments if i.is_drum)
    
    if count_melodic + count_drums > 16:
        log(f"WARNING: This MIDI has {count_melodic + count_drums} instruments, which exceeds the standard 16-channel limit.")

    for i, source_inst in enumerate(source_midi.instruments):
        target_inst = pretty_midi.Instrument(
            program=source_inst.program, 
            is_drum=source_inst.is_drum, 
            name=source_inst.name
        )
        target_inst.notes = source_inst.notes
        target_inst.pitch_bends = source_inst.pitch_bends
        target_inst.control_changes = source_inst.control_changes
        target_midi.instruments.append(target_inst)
        
        inst_name = source_inst.name
        if not inst_name or inst_name.strip() == "":
            try:
                inst_name = pretty_midi.program_to_instrument_name(source_inst.program)
            except:
                inst_name = f"Unknown Instrument {source_inst.program}"
                
        log(f"Processed Track {i+1}: {inst_name} ({len(source_inst.notes)} notes)")

    target_midi.key_signature_changes = source_midi.key_signature_changes
    target_midi.time_signature_changes = source_midi.time_signature_changes
    target_midi.lyrics = source_midi.lyrics

    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_fixed{ext}"

    try:
        target_midi.write(output_file)
        log("-" * 40)
        log(f"Successfully saved fixed MIDI to: {output_file}")
    except Exception as e:
        log(f"Error saving MIDI file: {e}")
    
    return logs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sanitize and fix MIDI file channel assignments.")
    parser.add_argument("input_file", help="Path to the input MIDI file")
    parser.add_argument("output_file", nargs="?", help="Path to the output MIDI file (optional)")
    
    args = parser.parse_args()
    
    results = fix_midi(args.input_file, args.output_file)
    for line in results:
        print(line)