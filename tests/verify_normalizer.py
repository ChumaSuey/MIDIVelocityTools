import pretty_midi
import os
import sys
from MIDINormalizer import normalize_midi

def create_test_midi(filename="test_quiet.mid"):
    """Creates a MIDI file with low velocity notes."""
    pm = pretty_midi.PrettyMIDI()
    inst = pretty_midi.Instrument(program=0)
    # Add a note with velocity 64 (half volume)
    note = pretty_midi.Note(velocity=64, pitch=60, start=0, end=1)
    inst.notes.append(note)
    pm.instruments.append(inst)
    pm.write(filename)
    print(f"Created {filename} with max velocity 64.")
    return filename

def verify_normalization(input_file):
    """Runs normalization and checks the output."""
    normalize_midi(input_file)
    
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_normalized{ext}"
    
    if not os.path.exists(output_file):
        print(f"FAILURE: Output file {output_file} not found.")
        return False
        
    pm = pretty_midi.PrettyMIDI(output_file)
    max_vel = 0
    for inst in pm.instruments:
        for note in inst.notes:
            if note.velocity > max_vel:
                max_vel = note.velocity
                
    print(f"Normalized max velocity: {max_vel}")
    
    if max_vel == 127:
        print("SUCCESS: Max velocity is 127.")
        return True
    else:
        print(f"FAILURE: Expected 127, got {max_vel}.")
        return False

if __name__ == "__main__":
    test_file = create_test_midi()
    success = verify_normalization(test_file)
    
    # Cleanup
    try:
        os.remove(test_file)
        base, ext = os.path.splitext(test_file)
        output_file = f"{base}_normalized{ext}"
        if os.path.exists(output_file):
            os.remove(output_file)
    except Exception as e:
        print(f"Error cleaning up: {e}")

    if not success:
        sys.exit(1)
