"""PCM WAV builder for demo background music."""

from __future__ import annotations

import math
import struct


_CATEGORY_PROFILES: dict[str, dict] = {
    "sports": {"base": 220, "pulse": 2.0, "harmonic": 1.4, "gain": 0.42},
    "drama": {"base": 130, "pulse": 0.4, "harmonic": 0.8, "gain": 0.35},
    "epic": {"base": 165, "pulse": 0.6, "harmonic": 1.6, "gain": 0.48},
    "corporate": {"base": 196, "pulse": 0.5, "harmonic": 1.0, "gain": 0.32},
    "technology": {"base": 440, "pulse": 4.0, "harmonic": 2.0, "gain": 0.38},
    "suspense": {"base": 90, "pulse": 0.25, "harmonic": 0.6, "gain": 0.4},
    "documentary": {"base": 174, "pulse": 0.35, "harmonic": 1.1, "gain": 0.3},
}


def build_music_wav(
    duration_seconds: float,
    *,
    category: str = "documentary",
    loop: bool = True,
    fade_in: float = 2.0,
    fade_out: float = 3.0,
    bpm: int = 72,
    sample_rate: int = 44100,
) -> bytes:
    duration = max(10.0, min(duration_seconds, 300.0))
    profile = _CATEGORY_PROFILES.get(category, _CATEGORY_PROFILES["documentary"])
    n_samples = int(sample_rate * duration)
    beat_period = 60.0 / max(bpm, 40)

    samples: list[float] = []
    for i in range(n_samples):
        t = i / sample_rate
        beat = 0.5 + 0.5 * math.sin(2 * math.pi * t / beat_period)
        base = profile["base"]
        harmonic = base * profile["harmonic"]
        pulse = profile["pulse"]
        pad = math.sin(2 * math.pi * base * t) * 0.5
        pad += math.sin(2 * math.pi * harmonic * t) * 0.25
        rhythm = math.sin(2 * math.pi * base * pulse * t) * beat * 0.35
        val = profile["gain"] * (pad + rhythm)

        if loop:
            loop_pos = (t % duration) / duration
            seam = 1.0 - 0.15 * abs(math.sin(math.pi * loop_pos))
            val *= seam

        fade = 1.0
        if fade_in > 0:
            fade = min(fade, t / fade_in)
        if fade_out > 0:
            fade = min(fade, (duration - t) / fade_out)
        val *= max(0.0, fade)
        samples.append(max(-1.0, min(1.0, val)))

    pcm = [int(s * 32767) for s in samples]
    data = struct.pack(f"<{len(pcm)}h", *pcm)
    byte_rate = sample_rate * 2
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + len(data),
        b"WAVE",
        b"fmt ",
        16,
        1,
        1,
        sample_rate,
        byte_rate,
        2,
        16,
        b"data",
        len(data),
    )
    return header + data
