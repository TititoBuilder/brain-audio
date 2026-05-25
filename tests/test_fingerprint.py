# tests/test_fingerprint.py
#
# PURPOSE: Prove the fingerprint works end-to-end
# and VISUALIZE the FFT so you can see the spike with your own eyes.

import numpy as np
import soundfile as sf
import sys
from pathlib import Path

# Add brain-audio to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from brain_audio.fingerprint import embed, detect, FINGERPRINT_HZ

# ─────────────────────────────────────────
# STEP 1: Generate a fake "TTS output" WAV
# (white noise simulates real speech closely enough)
# ─────────────────────────────────────────
SAMPLE_RATE = 44_100   # Kokoro's default sample rate
DURATION    = 3        # seconds
OUTPUT_PATH = "test_audio.wav"

print("=" * 50)
print("STEP 1 — Generating synthetic audio")
print("=" * 50)

samples = DURATION * SAMPLE_RATE
noise = np.random.uniform(-0.005, 0.005, samples).astype(np.float32)
sf.write(OUTPUT_PATH, noise, SAMPLE_RATE)
print(f"Created: {OUTPUT_PATH}  ({samples} samples @ {SAMPLE_RATE}Hz)\n")


# ─────────────────────────────────────────
# STEP 2: Detect BEFORE embedding
# Expected: detected = False
# ─────────────────────────────────────────
print("=" * 50)
print("STEP 2 — Detection BEFORE fingerprint")
print("=" * 50)
result_before = detect(OUTPUT_PATH)
print(f"Detected:   {result_before['detected']}")
print(f"Confidence: {result_before['confidence']}")
print(f"Source:     {result_before['source']}\n")


# ─────────────────────────────────────────
# STEP 3: Embed the fingerprint
# ─────────────────────────────────────────
print("=" * 50)
print("STEP 3 — Embedding fingerprint")
print("=" * 50)
embed(OUTPUT_PATH, profile="soccer")
print()


# ─────────────────────────────────────────
# STEP 4: Detect AFTER embedding
# Expected: detected = True
# ─────────────────────────────────────────
print("=" * 50)
print("STEP 4 — Detection AFTER fingerprint")
print("=" * 50)
result_after = detect(OUTPUT_PATH)
print(f"Detected:   {result_after['detected']}")
print(f"Confidence: {result_after['confidence']}")
print(f"Source:     {result_after['source']}\n")


# ─────────────────────────────────────────
# STEP 5: VISUALIZE the FFT spike
# This is the proof — you will SEE the fingerprint
# ─────────────────────────────────────────
print("=" * 50)
print("STEP 5 — FFT visualization (text-based)")
print("=" * 50)

audio, sr = sf.read(OUTPUT_PATH)
fft_result  = np.fft.rfft(audio)
frequencies = np.fft.rfftfreq(len(audio), d=1 / sr)
magnitudes  = np.abs(fft_result) / len(audio)

# Show energy in the 17,000–20,000 Hz range
# You should see ONE clear spike at 18,500 Hz
print(f"{'Frequency (Hz)':<18} {'Magnitude':<12} {'Signal'}")
print("-" * 45)

mask = (frequencies >= 17_000) & (frequencies <= 20_000)
freq_slice = frequencies[mask]
mag_slice  = magnitudes[mask]

# Sample every 50 bins so output is readable
for freq, mag in zip(freq_slice[::50], mag_slice[::50]):
    bar    = "█" * int(mag * 50_000)
    marker = " ← FINGERPRINT" if abs(freq - FINGERPRINT_HZ) < 100 else ""
    print(f"{freq:<18.1f} {mag:<12.6f} {bar}{marker}")

print("\n✓ Test complete")