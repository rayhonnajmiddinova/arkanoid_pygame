"""Loads sound effects and music, but never crashes if audio is unavailable."""
from __future__ import annotations
import pygame
import settings as cfg

_sounds = {}
_ok = False


def init() -> None:
    """ Tries to start the mixer and load assets. Silently degrades on failure. """
    global _ok
    try:
        pygame.mixer.init()
    except pygame.error:
        _ok = False
        return
    _ok = True
    for name in ("hit", "bonus", "laser"):
        try:
            _sounds[name] = pygame.mixer.Sound(str(cfg.ASSETS_DIR / f"{name}.mp3"))
        except (pygame.error, FileNotFoundError):
            _sounds[name] = None
    try:
        pygame.mixer.music.load(str(cfg.ASSETS_DIR / "music.mp3"))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass


def play(name: str) -> None:
    if _ok and _sounds.get(name):
        _sounds[name].play()