import sys
import os
import pretty_midi

# Add parent directory to sys.path to allow importing from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MIDINormalizer import normalize_midi

def create_test_midi(filename):
    midi = pretty_midi.PrettyMIDI()
    
    # Track 1: Normal Instrument (Piano)
    # Velocity 60. Should be the target for normalization if others are ignored.
    piano = pretty_midi.Instrument(program=0, name="Piano")
    piano.notes.append(pretty_midi.Note(velocity=60, pitch=60, start=0, end=1))
    midi.instruments.append(piano)
    
    # Track 2: Muted Instrument (Strings)
    # Velocity 127 (LOUD), but Volume 0.
    strings = pretty_midi.Instrument(program=40, name="Strings (Muted)")
    strings.notes.append(pretty_midi.Note(velocity=127, pitch=72, start=0, end=1))
    # CC7 = Volume. Set to 0.
    strings.control_changes.append(pretty_midi.ControlChange(number=7, value=0, time=0))
    midi.instruments.append(strings)
    
    # Track 3: Phantom Noise (Drums)
    # Velocity 5. Should be ignored by threshold.
    drums = pretty_midi.Instrument(program=0, is_drum=True, name="Phantom Noise")
    drums.notes.append(pretty_midi.Note(velocity=5, pitch=36, start=0, end=1))
    midi.instruments.append(drums)
    
    midi.write(filename)
    print(f"Created test MIDI: {filename}")

def verify():
    input_file = "test_phantom.mid"
    output_file = "test_phantom_normalized.mid"
    
    create_test_midi(input_file)
    
    print("\n--- Running Normalization (Ignore Muted=True, Threshold=10) ---")
    # We expect max velocity to be 60 (Piano), ignoring Strings (127) and Drums (5).
    # Target 127. Scale factor should be 127/60 ~= 2.11
    
    logs = normalize_midi(input_file, output_file, target_velocity=127, ignore_muted=True, velocity_threshold=10)
    
    for log in logs:
        print(log)
        
    # Check results
    res_midi = pretty_midi.PrettyMIDI(output_file)
    
    piano_vel = res_midi.instruments[0].notes[0].velocity
    strings_vel = res_midi.instruments[1].notes[0].velocity
    
    print("\n--- Verification Results ---")
    print(f"Piano Velocity (Expected ~127): {piano_vel}")
    print(f"Strings Velocity (Expected 127 due to scaling, but key is it didn't prevent Piano scaling): {strings_vel}")
    
    if piano_vel >= 126:
        print("SUCCESS: Piano was normalized correctly (Muted/Phantom tracks were ignored for Max Velocity calculation).")
    else:
        print("FAILURE: Piano was NOT normalized correctly. Likely the Muted Strings (Vel 127) were considered the max.")

    # Clean up
    try:
        os.remove(input_file)
        os.remove(output_file)
    except:
        pass

if __name__ == "__main__":
    verify()
