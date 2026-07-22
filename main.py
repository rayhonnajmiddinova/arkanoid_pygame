"""Entry point: sets up pygame and routes between screens."""
from __future__ import annotations
import pygame
import settings as cfg
from game import audio
from screens.game_screen import run as game_screen


def _message_screen(screen, clock, title, subtitle, color):
    """ Shows a full-screen message until the player presses a key. Returns the key action. """
    big = pygame.font.SysFont("consolas", 56, bold=True)
    small = pygame.font.SysFont("consolas", 22)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
                return "continue"
        screen.fill(cfg.BLACK)
        t = big.render(title, True, color)
        s = small.render(subtitle, True, cfg.WHITE)
        screen.blit(t, t.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 30)))
        screen.blit(s, s.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 30)))
        pygame.display.flip()
        clock.tick(cfg.FPS)


def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Arkanoid")
    clock = pygame.time.Clock()
    audio.init()

    if _message_screen(screen, clock, "ARKANOID",
                       "Press any key to start  -  Esc to quit", cfg.CYAN) == "quit":
        pygame.quit()
        return

    level = 1
    while True:
        result = game_screen(screen, clock, level)

        if result == "quit":
            break
        if result == "win":
            action = _message_screen(screen, clock, "YOU WIN!",
                                     "Press any key to play again  -  Esc to quit", cfg.GREEN)
        else:  # lose
            action = _message_screen(screen, clock, "GAME OVER",
                                     "Press any key to retry  -  Esc to quit", cfg.RED)
        if action == "quit":
            break
        level = 1  # single level for now; increment here when more levels exist

    pygame.quit()


if __name__ == "__main__":
    main()