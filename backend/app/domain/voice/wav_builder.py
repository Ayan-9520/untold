"""Minimal PCM WAV builder for demo narration audio."""

from __future__ import annotations

import math
import struct


def build_demo_wav(
    duration_seconds: float,
    *,
    sample_rate: int = 22050,
    pitch: float = 1.0,
    emotion: str = "neutral",
) -> bytes:
    duration = max(1.0, min(duration_seconds, 300.0))
    n_samples = int(sample_rate * duration)
    base_freq = 180.0 * max(0.5, min(pitch, 2.0))

    emotion_gain = {
        "neutral": 0.35,
        "warm": 0.4,
        "dramatic": 0.5,
        "energetic": 0.55,
        "calm": 0.25,
        "authoritative": 0.45,
    }.get(emotion, 0.35)

    samples: list[int] = []
    for i in range(n_samples):
        t = i / sample_rate
        mod = 0.5 + 0.5 * math.sin(2 * math.pi * 0.8 * t)
        freq = base_freq * (1.0 + 0.05 * math.sin(2 * math.pi * 0.3 * t))
        val = emotion_gain * mod * math.sin(2 * math.pi * freq * t)
        # gentle fade in/out
        fade = min(1.0, t / 0.15, (duration - t) / 0.15)
        val *= fade
        samples.append(int(max(-1.0, min(1.0, val)) * 32767))

    data = struct.pack(f"<{len(samples)}h", *samples)
    byte_rate = sample_rate * 2
    block_align = 2
    data_size = len(data)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        1,
        sample_rate,
        byte_rate,
        block_align,
        16,
        b"data",
        data_size,
    )
    return header + data
