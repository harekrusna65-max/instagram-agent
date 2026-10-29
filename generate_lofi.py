import math
import wave
import struct
import random

sr = 44100
duration = 18.0
num_samples = int(sr * duration)

# Ambient Lofi Progression (F#m7 - Dmaj7 - A - E/G#)
# Frequencies
chords = [
    [185.0, 220.0, 277.18, 369.99], # F#m7
    [146.83, 185.0, 220.0, 293.66], # Dmaj7
    [220.0, 277.18, 329.63, 440.0], # A
    [207.65, 246.94, 329.63, 415.3] # E
]

samples = [0.0] * num_samples
chord_dur = 4.5

# 1. Warm guitar/rhodes arpeggio
for i in range(int(math.ceil(duration / chord_dur))):
    c = chords[i % len(chords)]
    st = i * chord_dur
    for n_idx, freq in enumerate(c):
        note_st = st + (n_idx * 0.45)
        s_idx = int(note_st * sr)
        e_idx = min(num_samples, s_idx + int(6.0 * sr))
        for j in range(s_idx, e_idx):
            t = (j - s_idx) / sr
            # Warm acoustic guitar / electric piano timbre
            decay = math.exp(-t * 0.95)
            # Gentle chorus/vibrato
            vibrato = math.sin(2 * math.pi * 3.5 * t) * 0.003
            val = (
                math.sin(2 * math.pi * freq * (1 + vibrato) * t) * 0.65 +
                math.sin(4 * math.pi * freq * t) * 0.20 +
                math.sin(6 * math.pi * freq * t) * 0.08
            ) * decay * 0.22
            samples[j] += val

# 2. Add subtle warm vinyl crackle & soft lofi tape noise
for j in range(num_samples):
    # Soft vinyl crackle
    if random.random() < 0.0007:
        samples[j] += random.uniform(-0.15, 0.15)
    # Low-pass warmth
    samples[j] += random.gauss(0, 0.003)

# 3. Soft sub bass kick on each chord
for i in range(int(math.ceil(duration / chord_dur))):
    st = i * chord_dur
    s_idx = int(st * sr)
    e_idx = min(num_samples, s_idx + int(1.2 * sr))
    for j in range(s_idx, e_idx):
        t = (j - s_idx) / sr
        # 55Hz sub drop
        bass_freq = 55.0 * math.exp(-t * 3.0)
        samples[j] += math.sin(2 * math.pi * bass_freq * t) * math.exp(-t * 2.5) * 0.25

# Normalize
max_v = max(abs(s) for s in samples) or 1.0
with wave.open("assets/music/aesthetic_lofi_vibe.wav", "w") as f:
    f.setnchannels(2)
    f.setsampwidth(2)
    f.setframerate(sr)
    raw = bytearray()
    for s in samples:
        norm = int((s / max_v) * 28000)
        norm = max(-32767, min(32767, norm))
        raw.extend(struct.pack("<hh", norm, norm))
    f.writeframes(raw)

print("Aesthetic Lofi Vibe track created successfully at assets/music/aesthetic_lofi_vibe.wav!")
