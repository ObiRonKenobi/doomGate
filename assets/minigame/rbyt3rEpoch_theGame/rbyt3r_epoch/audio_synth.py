"""Tiny procedural SFX (WAV → pygame.mixer.Sound). No asset files."""

from __future__ import annotations

import math
import random
import struct
from dataclasses import dataclass
from typing import Optional

import pygame


def _wav_bytes_mono16(pcm: bytes, sample_rate: int) -> bytes:
    n = len(pcm)
    chunk_size = 36 + n
    buf = bytearray()
    buf += b"RIFF" + struct.pack("<I", chunk_size) + b"WAVE"
    buf += b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16)
    buf += b"data" + struct.pack("<I", n) + pcm
    return bytes(buf)


def _pew_pcm(freq: float, duration: float, sample_rate: int, vol: float) -> bytes:
    n = int(sample_rate * duration)
    out = bytearray()
    for i in range(n):
        t = i / sample_rate
        env = math.exp(-t * (42.0 / max(duration, 0.02)))
        s = env * math.sin(2 * math.pi * freq * t)
        v = int(max(-32767, min(32767, s * vol * 22000)))
        out.extend(struct.pack("<h", v))
    return bytes(out)


def _swoosh_pcm(sample_rate: int) -> bytes:
    dur = 0.052
    n = int(sample_rate * dur)
    out = bytearray()
    for i in range(n):
        t = i / sample_rate
        f = 180.0 + 920.0 * (t / dur)
        env = math.exp(-t * 38.0)
        s = env * math.sin(2 * math.pi * f * t)
        v = int(max(-32767, min(32767, s * 9000)))
        out.extend(struct.pack("<h", v))
    return bytes(out)


def _explosion_pcm(sample_rate: int, duration: float, vol: float) -> bytes:
    """Chiptune-ish: square chirp + noise burst (retro 'FM' explosion feel)."""
    n = int(sample_rate * duration)
    out = bytearray()
    phase = 0.0
    rng = random.Random()
    for i in range(n):
        t = i / sample_rate
        env = (1.0 - t / duration) ** 1.35
        f = 280.0 * (1.0 - t / duration) + 38.0
        phase += 2 * math.pi * f / sample_rate
        sq = 1.0 if (phase % (2 * math.pi)) < math.pi else -1.0
        noise = rng.uniform(-1.0, 1.0)
        mix = env * (0.5 * sq + 0.48 * noise)
        v = int(max(-32767, min(32767, mix * vol * 12000)))
        out.extend(struct.pack("<h", v))
    return bytes(out)


def _sound_from_pcm(pcm: bytes, sample_rate: int) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(buffer=_wav_bytes_mono16(pcm, sample_rate))


def _doof_pcm(sample_rate: int) -> bytes:
    """Short impact thump when a player round connects."""
    dur = 0.058
    n = int(sample_rate * dur)
    out = bytearray()
    for i in range(n):
        t = i / sample_rate
        env = math.exp(-t * 36.0)
        f = 108.0 * math.exp(-t * 48.0) + 52.0
        s = env * math.sin(2 * math.pi * f * t)
        v = int(max(-32767, min(32767, s * 12500)))
        out.extend(struct.pack("<h", v))
    return bytes(out)


def _death_scream_pcm(sample_rate: int) -> bytes:
    """Over-the-top 8-bit 'scream': wide pitch sweep, heavy vibrato, harsh square + noise."""
    dur = 0.88
    n = int(sample_rate * dur)
    out = bytearray()
    phase = 0.0
    rng = random.Random(7)
    for i in range(n):
        t = i / sample_rate
        u = t / dur
        if u < 0.28:
            f = 220.0 + 1180.0 * (u / 0.28) ** 0.85
        elif u < 0.52:
            f = 1400.0 + 180.0 * math.sin((u - 0.28) * 38.0)
        else:
            f = 1200.0 - 1050.0 * min(1.0, (u - 0.52) / 0.48)
        f = max(70.0, f)
        vibrato = 1.0 + 0.14 * math.sin(t * math.pi * 52.0) + 0.06 * math.sin(t * math.pi * 91.0)
        f *= vibrato
        phase += 2 * math.pi * f / sample_rate
        duty = 0.38 + 0.12 * math.sin(t * math.pi * 24.0)
        sq = 1.0 if (phase % (2 * math.pi)) < math.pi * duty else -1.0
        noise = rng.uniform(-0.38, 0.38)
        env = math.sin(min(1.0, u * 1.15) * math.pi) ** 0.5
        mix = env * (0.72 * sq + noise)
        v = int(max(-32767, min(32767, mix * 13200)))
        out.extend(struct.pack("<h", v))
    return bytes(out)


def _warning_pcm(sample_rate: int) -> bytes:
    """Quick two-tone alert when the player is tagged by hostile fire."""
    dur = 0.2
    n = int(sample_rate * dur)
    out = bytearray()
    for i in range(n):
        t = i / sample_rate
        flip = int(t * 11.0) % 2
        f = 780.0 if flip else 560.0
        env = 0.5 + 0.5 * math.sin(t * math.pi * 12.0)
        s = env * math.sin(2 * math.pi * f * t)
        v = int(max(-32767, min(32767, s * 15000)))
        out.extend(struct.pack("<h", v))
    return bytes(out)


@dataclass
class Rbyt3rSounds:
    pew_light: pygame.mixer.Sound
    pew_mid: pygame.mixer.Sound
    pew_heavy: pygame.mixer.Sound
    pew_shotgun: pygame.mixer.Sound
    pew_plasma: pygame.mixer.Sound
    pew_bfg: pygame.mixer.Sound
    swoosh: pygame.mixer.Sound
    boom: pygame.mixer.Sound
    doof: pygame.mixer.Sound
    warning: pygame.mixer.Sound
    death_scream: pygame.mixer.Sound


def try_load_sounds(sample_rate: int = 22050) -> Optional[Rbyt3rSounds]:
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init(frequency=sample_rate, size=-16, channels=1, buffer=256)
    except Exception:
        return None
    try:
        sr = sample_rate
        return Rbyt3rSounds(
            pew_light=_sound_from_pcm(_pew_pcm(1550, 0.045, sr, 0.32), sr),
            pew_mid=_sound_from_pcm(_pew_pcm(1180, 0.055, sr, 0.34), sr),
            pew_heavy=_sound_from_pcm(_pew_pcm(820, 0.07, sr, 0.36), sr),
            pew_shotgun=_sound_from_pcm(_pew_pcm(420, 0.09, sr, 0.42), sr),
            pew_plasma=_sound_from_pcm(_pew_pcm(220, 0.11, sr, 0.38), sr),
            pew_bfg=_sound_from_pcm(_pew_pcm(95, 0.16, sr, 0.45), sr),
            swoosh=_sound_from_pcm(_swoosh_pcm(sr), sr),
            boom=_sound_from_pcm(_explosion_pcm(sr, 0.26, 0.55), sr),
            doof=_sound_from_pcm(_doof_pcm(sr), sr),
            warning=_sound_from_pcm(_warning_pcm(sr), sr),
            death_scream=_sound_from_pcm(_death_scream_pcm(sr), sr),
        )
    except Exception:
        return None
