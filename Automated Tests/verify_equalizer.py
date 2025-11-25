import pretty_midi
import os
import sys
from MIDIEqualizer import equalize_midi

def create_test_midi(filename, velocity=127):
    midi = pretty_midi.PrettyMIDI()
    inst = pretty_midi.Instrument(program=0, name="Test Piano")
    note = pretty_midi.Note(velocity=velocity, pitch=60, start=0, end=1)
    inst.notes.append(note)
    midi.instruments.append(inst)
    midi.write(filename)
    print(f"Created {filename} with max velocity {velocity}.")

def verify():
    input_file = "test_loud.mid"
    output_file = "test_loud_equalized.mid"
    
    # Create a loud file
    create_test_midi(input_file, 127)
    
    # Run equalizer (default 80%)
    print("Running MIDIEqualizer...")
    equalize_midi(input_file, output_file, level=80)
    
    # Check result
    if not os.path.exists(output_file):
        print("FAILURE: Output file not found.")
        return

    midi = pretty_midi.PrettyMIDI(output_file)
    max_vel = 0
    for inst in midi.instruments:
        for note in inst.notes:
            if note.velocity > max_vel:
                max_vel = note.velocity
    
    print(f"Equalized max velocity: {max_vel}")
    
    # Expected: 127 * 0.8 = 101.6 -> 101
    if max_vel == 101:
        print("SUCCESS: Max velocity is 101 (approx 80% of 127).")
    else:
        print(f"FAILURE: Expected 101, got {max_vel}.")

    # Cleanup
    try:
        os.remove(input_file)
        os.remove(output_file)
    except:
        pass

if __name__ == "__main__":
    verify()
