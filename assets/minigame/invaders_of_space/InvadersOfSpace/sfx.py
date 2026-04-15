"""
Tiny procedural arcade SFX for Invaders of Space (no external asset files).
Uses 16-bit mono PCM → pygame.mixer.Sound.
"""

from __future__ import annotations

import array
import math
from typing import List

import pygame


SR = 22050


def _clamp16(x: float) -> int:
    return max(-32767, min(32767, int(x)))


def _to_sound(samples: List[int]) -> pygame.mixer.Sound:
    buf = array.array("h", samples)
    return pygame.mixer.Sound(buffer=buf.tobytes())


def make_pew() -> pygame.mixer.Sound:
    """Short bright 'pew' — rising chirp + quick decay."""
    dur = 0.07
    n = int(SR * dur)
    out: List[int] = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 35.0)
        f0, f1 = 900.0, 2200.0
        f = f0 + (f1 - f0) * (i / max(1, n - 1))
        s = math.sin(2.0 * math.pi * f * t)
        # slight square-ish harmonics
        s = 0.65 * s + 0.35 * math.copysign(1.0, s)
        out.append(_clamp16(5200.0 * env * s))
    return _to_sound(out)


def make_doop() -> pygame.mixer.Sound:
    """Soft 'doop' when fleet bounces — pitch drops, mellow."""
    dur = 0.14
    n = int(SR * dur)
    out: List[int] = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 18.0)
        f = 200.0 - 90.0 * (i / max(1, n - 1))
        s = math.sin(2.0 * math.pi * f * t)
        out.append(_clamp16(4800.0 * env * s))
    return _to_sound(out)


def make_explosion() -> pygame.mixer.Sound:
    """Noisy burst with decay — game over / ship destroyed."""
    dur = 0.42
    n = int(SR * dur)
    out: List[int] = []

    def det_noise(i: int) -> float:
        x = (i * 1103515245 + 12345) & 0x7FFFFFFF
        return (x / float(0x7FFFFFFF)) * 2.0 - 1.0

    for i in range(n):
        t = i / SR
        env = math.exp(-t * 7.0)
        n0 = det_noise(i)
        rumble = 0.35 * math.sin(2.0 * math.pi * 55.0 * t)
        s = 0.65 * n0 + rumble
        out.append(_clamp16(9000.0 * env * s))
    return _to_sound(out)


def make_midi_explode() -> pygame.mixer.Sound:
    """Alien kill: 'midi-ish' 8-bit chord hit + tiny noise burst."""
    dur = 0.16
    n = int(SR * dur)
    out: List[int] = []

    def det_noise(i: int) -> float:
        x = (i * 1103515245 + 12345) & 0x7FFFFFFF
        return (x / float(0x7FFFFFFF)) * 2.0 - 1.0

    # Minor-ish stab: A4 + C5 + E5
    freqs = (440.0, 523.25, 659.25)
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 18.0)
        s = 0.0
        for f in freqs:
            s0 = math.sin(2.0 * math.pi * f * t)
            s += 0.55 * math.copysign(1.0, s0) + 0.45 * s0
        s /= len(freqs)
        click = det_noise(i) * math.exp(-t * 55.0)
        out.append(_clamp16((7200.0 * env * s) + (2600.0 * click)))
    return _to_sound(out)


def make_anger_cry() -> pygame.mixer.Sound:
    """Life lost: short angry 'raaagh' — descending formant-y tone."""
    dur = 0.28
    n = int(SR * dur)
    out: List[int] = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 9.5)
        f = 420.0 - 260.0 * (i / max(1, n - 1))
        base = math.sin(2.0 * math.pi * f * t)
        harm = 0.55 * math.sin(2.0 * math.pi * (f * 2.02) * t)
        grit = 0.22 * math.copysign(1.0, base)
        s = 0.55 * base + 0.35 * harm + grit
        out.append(_clamp16(8200.0 * env * s))
    return _to_sound(out)
