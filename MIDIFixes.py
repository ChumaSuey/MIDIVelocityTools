import pretty_midi
import argparse
import sys
import os

def fix_midi(input_file, output_file=None):
    """
    Sanitizes a MIDI file by re-creating it from scratch.
    This fixes issues where instruments might have conflicting channels or
    uninitialized states by forcing valid channel assignments during the rewrite.
    
    Returns a list of strings containing the process log.
    """
    logs = []
    def log(msg):
        logs.append(msg)
        # print(msg) # Optional: print to stdout as well if needed

    try:
        source_midi = pretty_midi.PrettyMIDI(input_file)
    except Exception as e:
        log(f"Error loading MIDI file: {e}")
        return logs

    # Create a new, clean MIDI object
    target_midi = pretty_midi.PrettyMIDI()

    log(f"Processing: {input_file}")
    log("-" * 40)

    # Check for potential channel overflow (standard MIDI has 16 channels)
    # Drums usually take channel 10 (index 9).
    count_melodic = sum(1 for i in source_midi.instruments if not i.is_drum)
    count_drums = sum(1 for i in source_midi.instruments if i.is_drum)
    
    if count_melodic + count_drums > 16:
        log(f"WARNING: This MIDI has {count_melodic + count_drums} instruments.")
        log("Standard MIDI only supports 16 channels.")
        log("Some instruments will inevitably share channels, which may cause audio conflicts.")
        log("The script will assign them sequentially, circling back to used channels if necessary.")
        log("-" * 40)

    for i, source_inst in enumerate(source_midi.instruments):
        # Create a new instrument with the same properties
        # We explicitly do NOT carry over 'channel' metadata if it exists in a way that pretty_midi exposes (it usually doesn't directly),
        # instead letting pretty_midi assign fresh channels upon write().
        
        target_inst = pretty_midi.Instrument(
            program=source_inst.program,
            is_drum=source_inst.is_drum,
            name=source_inst.name
        )

        # Copy all notes
        for note in source_inst.notes:
            target_inst.notes.append(pretty_midi.Note(
                velocity=note.velocity,
                pitch=note.pitch,
                start=note.start,
                end=note.end
            ))

        # Copy pitch bends
        for bend in source_inst.pitch_bends:
            target_inst.pitch_bends.append(pretty_midi.PitchBend(
                pitch=bend.pitch,
                time=bend.time
            ))
            
        # Copy control changes 
        # (Be careful here: if the source had bad CCs causing issues, copying them might keep the issue.
        # But usually we want to keep volume/pan. For strict sanitization, we might want to filter,
        # but for general 'fix channel' logic, copying is safer to preserve intent.)
        for cc in source_inst.control_changes:
            target_inst.control_changes.append(pretty_midi.ControlChange(
                number=cc.number,
                value=cc.value,
                time=cc.time
            ))

        target_midi.instruments.append(target_inst)
        
        inst_name = source_inst.name
        if not inst_name or inst_name.strip() == "":
            try:
                inst_name = pretty_midi.program_to_instrument_name(source_inst.program)
            except:
                inst_name = f"Unknown Instrument {source_inst.program}"
                
        log(f"Processed Track {i+1}: {inst_name} ({len(source_inst.notes)} notes)")

    # Determine output filename
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_fixed{ext}"

    try:
        # write() automatically handles channel assignment
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
    
    logs = fix_midi(args.input_file, args.output_file)
    for line in logs:
        print(line)
