import numpy as np
import scipy.io.wavfile as wav
import librosa
import os

# Create a dummy WAV file
sample_rate = 44100
duration = 1.0
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
y = 0.5 * np.sin(2 * np.pi * 440 * t)
wav_path = "test_audio.wav"
wav.write(wav_path, sample_rate, (y * 32767).astype(np.int16))

print(f"Created {wav_path}")

try:
    print("Attempting to load with librosa...")
    y_load, sr_load = librosa.load(wav_path, sr=None)
    print(f"Success! Loaded {len(y_load)} samples at {sr_load} Hz")
except Exception as e:
    print(f"Failed to load WAV: {e}")
finally:
    if os.path.exists(wav_path):
        os.remove(wav_path)
