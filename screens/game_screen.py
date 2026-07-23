"""The main gameplay screen: one level, run until win / lose / quit."""
from __future__ import annotations
import random

import pygame
import settings as cfg
from game import audio
from game.entities import Paddle, Ball, Bonus, Laser, Particle
from game.level import load_level


def _bounce_off_rect(ball: Ball, rect: pygame.Rect) -> None:
    """ Reflects the ball off the nearest face of the given rect. """
    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top
    min_overlap = min(overlap_bottom, overlap_left, overlap_right, overlap_top)

    if min_overlap == overlap_top and ball.vy > 0:
        ball.rect.bottom = rect.top
        ball.vy *= -1
    elif min_overlap == overlap_bottom and ball.vy < 0:
        ball.rect.top = rect.bottom
        ball.vy *= -1
    elif min_overlap == overlap_left and ball.vx > 0:
        ball.rect.right = rect.left
        ball.vx *= -1
    elif min_overlap == overlap_right and ball.vx < 0:   # FIXED: was ball.vy < 0
        ball.rect.left = rect.right
        ball.vx *= -1


def _enforce_min_vy(ball: Ball) -> None:
    """ Keeps some vertical motion so the ball never gets stuck horizontal. """
    if abs(ball.vy) < cfg.MIN_BALL_SPEED_Y:
        ball.vy = cfg.MIN_BALL_SPEED_Y if ball.vy >= 0 else -cfg.MIN_BALL_SPEED_Y


def _spawn_particles(particles: list, x: int, y: int, color) -> None:
    if len(particles) >= cfg.MAX_PARTICLES:
        return
    for _ in range(cfg.PARTICLE_COUNT):
        particles.append(Particle(x, y, color))


def _new_ball_on_paddle(paddle: Paddle) -> Ball:
    ball = Ball(paddle.rect.centerx, paddle.rect.top - cfg.BALL_RADIUS)
    ball.vx = random.choice((-cfg.BALL_SPEED_X, cfg.BALL_SPEED_X))
    ball.vy = cfg.BALL_SPEED_Y
    return ball


def apply_bonus(bonus: Bonus, paddle: Paddle, balls: list, lives: int) -> int:
    """
    Applies a collected power-up's effect.
    Returns the (possibly updated) number of lives.
    """
    kind = bonus.kind

    if kind == "extend":
        paddle.apply_extend()

    elif kind == "laser":
        paddle.apply_laser()

    elif kind == "extra_life":
        lives += 1

    elif kind == "multiball" and balls:
        src = balls[0]
        for _ in range(cfg.MULTIBALL_EXTRA):
            nb = Ball(src.rect.centerx, src.rect.centery)
            nb.stuck = False
            nb.vx = random.choice((-cfg.BALL_SPEED_X, cfg.BALL_SPEED_X))
            nb.vy = -abs(src.vy)
            balls.append(nb)

    # --- New power-ups -------------------------------------------------
    elif kind == "paddle_shrink":
        paddle.apply_shrink()

    elif kind == "ball_speed_up":
        for b in balls:
            b.scale_speed(cfg.BALL_SPEED_FACTOR)

    elif kind == "ball_speed_down":
        for b in balls:
            b.scale_speed(cfg.BALL_SLOW_FACTOR)

    return lives


def run(screen: pygame.Surface, clock: pygame.time.Clock, level: int,
        max_frames: int | None = None, autoplay: bool = False) -> str:
    """
    Runs one level. Returns "win", "lose" or "quit".
    max_frames / autoplay exist only for automated testing.
    """
    font = pygame.font.SysFont("consolas", 20)
    bonus_font = pygame.font.SysFont("consolas", 12, bold=True)
    big_font = pygame.font.SysFont("consolas", 48, bold=True)

    bricks, _rows, _cols = load_level(level)
    paddle = Paddle()
    balls = [_new_ball_on_paddle(paddle)]
    bonuses: list[Bonus] = []
    lasers: list[Laser] = []
    particles: list[Particle] = []

    score = 0
    lives = cfg.LIVES
    frames = 0

    while True:
        frames += 1
        screen.fill(cfg.BLACK)

        # ---- Input -------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for b in balls:
                    b.launch()
        keys = pygame.key.get_pressed()
        paddle.move(keys)
        paddle.update()

        if autoplay and balls:                        # test helper only
            paddle.rect.centerx = balls[0].rect.centerx
            for b in balls:
                b.launch()

        # ---- Fire lasers -------------------------------------------------
        if keys[pygame.K_SPACE] or autoplay:
            shots = paddle.try_fire()
            if shots:
                lasers.extend(shots)
                audio.play("laser")

        # ---- Balls: stick, move, collide --------------------------------
        for ball in balls[:]:
            if ball.stuck:
                ball.rect.midbottom = paddle.rect.midtop
                continue

            ball.update()

            # brick / wall collision (walls are bricks with hp == -1)
            for brick in bricks:
                if ball.rect.colliderect(brick.rect):
                    _bounce_off_rect(ball, brick.rect)
                    if brick.destructible:
                        destroyed = brick.hit()
                        audio.play("hit")
                        if destroyed:
                            score += 10
                            _spawn_particles(particles, brick.rect.centerx,
                                             brick.rect.centery, cfg.WHITE)
                            if random.random() < cfg.BONUS_PROBABILITY:
                                kind = random.choice(cfg.BONUS_TYPES)
                                bonuses.append(Bonus(brick.rect.centerx,
                                                     brick.rect.centery, kind))
                            bricks.remove(brick)
                    break

            # paddle collision
            if ball.vy > 0 and ball.rect.colliderect(paddle.rect):
                _bounce_off_rect(ball, paddle.rect)
                offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
                ball.vx = max(-cfg.MAX_BALL_SPEED_X,
                              min(cfg.MAX_BALL_SPEED_X, offset * cfg.MAX_BALL_SPEED_X))
                ball.vx += paddle.vx * cfg.SLIDE_FACTOR
                _enforce_min_vy(ball)

            # fell off the bottom
            if ball.rect.top > cfg.HEIGHT:
                balls.remove(ball)

        if not balls:
            lives -= 1
            if lives <= 0:
                return "lose"
            balls = [_new_ball_on_paddle(paddle)]

        # ---- Lasers ------------------------------------------------------
        for laser in lasers[:]:
            laser.update()
            if laser.rect.bottom < 0:
                lasers.remove(laser)
                continue
            for brick in bricks:
                if brick.destructible and laser.rect.colliderect(brick.rect):
                    if brick.hit():
                        score += 10
                        _spawn_particles(particles, brick.rect.centerx,
                                         brick.rect.centery, cfg.WHITE)
                        bricks.remove(brick)
                    audio.play("hit")
                    if laser in lasers:
                        lasers.remove(laser)
                    break

        # ---- Bonuses -----------------------------------------------------
        for bonus in bonuses[:]:
            bonus.update()
            if bonus.rect.top > cfg.HEIGHT:
                bonuses.remove(bonus)
                continue
            if bonus.rect.colliderect(paddle.rect):
                audio.play("bonus")
                lives = apply_bonus(bonus, paddle, balls, lives)
                bonuses.remove(bonus)

        # ---- Particles ---------------------------------------------------
        for p in particles[:]:
            p.update()
            if not p.alive:
                particles.remove(p)

        # ---- Win check ---------------------------------------------------
        if not any(b.destructible for b in bricks):
            return "win"

        # ---- Draw --------------------------------------------------------
        for brick in bricks:
            brick.draw(screen)
        for p in particles:
            p.draw(screen)
        for bonus in bonuses:
            bonus.draw(screen, bonus_font)
        for laser in lasers:
            laser.draw(screen)
        for ball in balls:
            ball.draw(screen)
        paddle.draw(screen)

        # HUD
        pygame.draw.line(screen, cfg.DARK_GRAY, (0, cfg.TOP_OFFSET),
                         (cfg.WIDTH, cfg.TOP_OFFSET), 1)
        screen.blit(font.render(f"SCORE {score}", True, cfg.WHITE), (cfg.FIELD_LEFT, 18))
        lives_surf = font.render(f"LIVES {lives}", True, cfg.WHITE)
        screen.blit(lives_surf, (cfg.WIDTH - cfg.FIELD_LEFT - lives_surf.get_width(), 18))
        lvl_surf = font.render(f"LVL {level}", True, cfg.GRAY)
        screen.blit(lvl_surf, (cfg.WIDTH // 2 - lvl_surf.get_width() // 2, 18))

        if any(b.stuck for b in balls):
            hint = big_font.render("PRESS SPACE", True, cfg.GRAY)
            screen.blit(hint, hint.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2)))

        pygame.display.flip()
        clock.tick(cfg.FPS)

        if max_frames and frames >= max_frames:
            return "timeout"
