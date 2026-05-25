# brain-audio/brain_audio/fingerprint.py

import numpy as np
import soundfile as sf
from pathlib import Path

# ─────────────────────────────────────────
# FINGERPRINT CONSTANTS
# Why 18500 Hz? Human hearing drops sharply above 15-16kHz with age.
# 18500 Hz is inaudible to most adults but detectable via FFT.
# Amplitude 0.0008 is ~0.08% of max signal — imperceptible but measurable.
# ─────────────────────────────────────────
FINGERPRINT_HZ = 18_500
FINGERPRINT_AMPLITUDE = 0.0008


def embed(wav_path: str, profile: str = "default") -> None:
    """
    Embed an inaudible tone fingerprint into a WAV file.

    WHAT HAPPENS HERE (signal processing perspective):
      1. Load audio → numpy array (time domain)
      2. Generate a pure sine wave at FINGERPRINT_HZ (also time domain)
      3. Add the two arrays together (superposition principle)
      4. Write back to disk

    The sine wave formula:
      y(t) = A * sin(2π * f * t)
      where:
        A = amplitude (how loud)
        f = frequency in Hz (18500)
        t = time axis in seconds
    """
    audio, sample_rate = sf.read(wav_path)

    # Build the time axis: one value per sample
    # e.g. 3 seconds at 44100 Hz = 132300 values
    num_samples = len(audio)
    t = np.linspace(0, num_samples / sample_rate, num_samples)

    # Generate the fingerprint tone (pure sine wave)
    tone = FINGERPRINT_AMPLITUDE * np.sin(2 * np.pi * FINGERPRINT_HZ * t)

    # Handle stereo: audio shape is (samples, 2) — tone needs to match
    if audio.ndim == 2:
        tone = np.stack([tone, tone], axis=1)

    # Superposition: mix fingerprint into audio
    fingerprinted = audio + tone

    # Clamp to [-1.0, 1.0] — digital audio cannot exceed this range
    fingerprinted = np.clip(fingerprinted, -1.0, 1.0)

    sf.write(wav_path, fingerprinted, sample_rate)
    print(f"[fingerprint:embed] {FINGERPRINT_HZ}Hz @ profile={profile} → {Path(wav_path).name}")


def detect(wav_path: str) -> dict:
    """
    Detect whether a WAV file contains a brain-audio fingerprint using local SNR.

    WHAT HAPPENS HERE (FFT perspective):
      1. Load audio → numpy array (time domain)
      2. Run FFT → converts to frequency domain
      3. Isolate neighbor bins, skipping the target_bin's spectral leakage shoulders
      4. Calculate the local noise floor and SNR ratio
      5. If snr_ratio > 3.0 → fingerprint present
    """
    audio, sample_rate = sf.read(wav_path)

    # Use mono for analysis — stereo is just two channels, we only need one
    if audio.ndim == 2:
        audio = audio.mean(axis=1)

    # FFT: time domain → frequency domain
    fft_result = np.fft.rfft(audio)

    # rfftfreq: tells us what Hz each FFT bin corresponds to
    frequencies = np.fft.rfftfreq(len(audio), d=1 / sample_rate)

    # Normalize magnitudes by signal length
    magnitudes = np.abs(fft_result) / len(audio)

    # Find the bin closest to our fingerprint frequency
    target_bin = np.argmin(np.abs(frequencies - FINGERPRINT_HZ))
    signal_strength = float(magnitudes[target_bin])

    # Step 1: Grab 10 neighbor bins on each side, leaving a 1-bin guard band to skip leakage shoulders
    neighbors = np.concatenate([
        magnitudes[target_bin - 11 : target_bin - 1], 
        magnitudes[target_bin + 2 : target_bin + 12]
    ])

    # Step 2: Calculate their average (the clean local noise floor)
    noise_floor = float(np.mean(neighbors))

    # Step 3: Divide signal_strength by noise floor → snr_ratio (safeguarded against zero division)
    snr_ratio = signal_strength / noise_floor if noise_floor > 0 else 0.0

    # Step 4: Verify if the sharp frequency spike is at least 3x higher than its local environment
    detected = snr_ratio > 3.0

    return {
        "detected": detected,
        "confidence": round(snr_ratio, 2),
        "noise_floor": round(noise_floor, 6),
        "signal_strength": round(signal_strength, 6),
        "frequency_hz": round(float(frequencies[target_bin]), 2),
        "source": "brain-audio" if detected else "unknown"
    }