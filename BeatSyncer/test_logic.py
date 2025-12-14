import numpy as np
import os
from analyzer import detect_beats
from exporters import export_to_csv_markers, export_to_edl

def test_logic():
    # Create a dummy audio signal (sine wave)
    sr = 22050
    duration = 5.0
    t = np.linspace(0, duration, int(sr * duration))
    # Create a beat every 0.5 seconds (120 BPM)
    y = np.sin(2 * np.pi * 440 * t)
    # Add pulses
    for i in range(0, int(duration * 2)):
        idx = int(i * 0.5 * sr)
        y[idx:idx+1000] += 5.0 # Strong pulse

    print("Running beat detection on synthetic signal...")
    tempo, beats = detect_beats(y, sr)
    print(f"Detected Tempo: {tempo}")
    print(f"Detected {len(beats)} beats.")

    if len(beats) > 0:
        print("Testing Export...")
        export_to_csv_markers(beats, "test_markers.csv")
        export_to_edl(beats, "test_edl.edl")
        
        if os.path.exists("test_markers.csv") and os.path.exists("test_edl.edl"):
            print("Export successful.")
            # Clean up
            os.remove("test_markers.csv")
            os.remove("test_edl.edl")
        else:
            print("Export failed: Files not created.")
    else:
        print("No beats detected in synthetic data.")

if __name__ == "__main__":
    test_logic()
