import librosa
import numpy as np

def load_audio(file_path):
    """
    Load an audio file.
    Returns:
        y: audio time series
        sr: sampling rate
        duration: duration in seconds
    """
    try:
        y, sr = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        return y, sr, duration
    except Exception as e:
        raise RuntimeError(f"Failed to load audio: {e}")

def detect_beats(y, sr):
    """
    Detect beats in the audio.
    Returns:
        tempo: estimated tempo
        beat_times: array of timestamps for beats
    """
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return tempo, beat_times

def detect_onsets(y, sr):
    """
    Detect onsets (note starts) in the audio.
    Returns:
        onset_times: array of timestamps for onsets
    """
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    return onset_times
