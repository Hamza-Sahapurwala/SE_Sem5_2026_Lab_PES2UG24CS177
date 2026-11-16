import array
import math
import random
import pygame

SAMPLE_RATE = 44100


def _make_sound(freq_start, freq_end, duration, volume=0.4, noise=False):
    """Build a short 16-bit mono sound: a square wave sweeping from
    freq_start to freq_end (or white noise), fading out over its length."""
    n = int(SAMPLE_RATE * duration)
    samples = array.array("h")
    phase = 0.0
    for i in range(n):
        t = i / n
        freq = freq_start + (freq_end - freq_start) * t
        phase += 2 * math.pi * freq / SAMPLE_RATE
        if noise:
            value = random.uniform(-1, 1)
        else:
            value = 1.0 if math.sin(phase) >= 0 else -1.0
        samples.append(int(value * (1 - t) * volume * 32767))
    return pygame.mixer.Sound(buffer=samples.tobytes())


class SoundEffects:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            # Re-init the mixer so the sample format matches what we generate
            pygame.mixer.quit()
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)
            self.sounds = {
                "fire": _make_sound(880, 220, 0.12),
                "explosion": _make_sound(0, 0, 0.25, noise=True),
                "game_over": _make_sound(440, 110, 0.9),
            }
            self.enabled = True
        except pygame.error as e:
            # No audio device available: the game still runs, just silently
            print("Sound disabled:", e)

    def play(self, name):
        if self.enabled:
            self.sounds[name].play()