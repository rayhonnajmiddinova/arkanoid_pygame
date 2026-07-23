from __future__ import annotations
import random

import pygame
import settings as cfg


class Paddle:
    """ Our main player, Paddle, moves only horizontally. """

    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, cfg.PADDLE_WIDTH, cfg.PADDLE_HEIGHT)
        self.rect.midbottom = (cfg.WIDTH // 2, cfg.HEIGHT - 20)
        self.speed = cfg.PADDLE_SPEED
        self.vx = 0
        self.extended_timer = 0
        self.laser_timer = 0
        self._cooldown = 0

    @property
    def laser(self) -> bool:
        return self.laser_timer > 0

    def move(self, keys) -> None:
        """ Moves the Paddle if the key is pressed. """
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vx = self.speed
        self.rect.x += self.vx
        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT
        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT

    def update(self) -> None:
        """ Ticks power-up timers each frame. """
        if self._cooldown > 0:
            self._cooldown -= 1
        if self.extended_timer > 0:
            self.extended_timer -= 1
            if self.extended_timer == 0:
                self._resize(cfg.PADDLE_WIDTH)
        if self.laser_timer > 0:
            self.laser_timer -= 1

    def _resize(self, width: int) -> None:
        center = self.rect.center
        self.rect.width = width
        self.rect.center = center
        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT
        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT

    def apply_extend(self) -> None:
        self._resize(cfg.EXTENDED_PADDLE_WIDTH)
        self.extended_timer = cfg.POWERUP_FRAMES

    def apply_shrink(self) -> None:
        """ Paddle Shrink power-up: makes the paddle narrower for a while. """
        self._resize(cfg.SHRUNK_PADDLE_WIDTH)
        self.extended_timer = cfg.POWERUP_FRAMES

    def apply_laser(self) -> None:
        self.laser_timer = cfg.POWERUP_FRAMES

    def try_fire(self):
        """ Fires two lasers from the paddle edges if laser is active and off cooldown. """
        if not self.laser or self._cooldown > 0:
            return []
        self._cooldown = cfg.LASER_COOLDOWN
        top = self.rect.top
        return [Laser(self.rect.left + 8, top), Laser(self.rect.right - 8, top)]

    def draw(self, screen: pygame.Surface) -> None:
        """ Renders the Paddle on the screen. """
        color = cfg.MAGENTA if self.laser else cfg.PADDLE_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=5)


class Brick:
    """
        Class for Game's brick.

        HP = -1: Level Boundary (indestructible)
        HP = 0: Indestructible
        HP = 1, 2: One / Two hit
    """

    def __init__(self, col: int, row: int, hp: int) -> None:
        self.hp = hp
        self.color = cfg.BRICK_COLORS[hp]
        self.rect = pygame.Rect(
            cfg.FIELD_LEFT + col * cfg.BRICK_WIDTH,
            cfg.TOP_OFFSET + row * cfg.BRICK_HEIGHT,
            cfg.BRICK_WIDTH,
            cfg.BRICK_HEIGHT,
        )

    @property
    def destructible(self) -> bool:
        return self.hp > 0

    def draw(self, screen: pygame.Surface) -> None:
        """ Renders a Brick in a certain row and col. """
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, cfg.DARK_GRAY, self.rect, 2)

    def hit(self) -> bool:
        """ Damages the brick. Returns True if it was destroyed this hit. """
        if self.hp > 0:
            self.hp -= 1
            if self.hp > 0:
                self.color = cfg.BRICK_COLORS[self.hp]
                return False
            return True
        return False


class Ball:
    """ Ball Actor class. """

    def __init__(self, x: int, y: int) -> None:
        self.radius = cfg.BALL_RADIUS
        self.rect = pygame.Rect(
            x - self.radius, y - self.radius, 2 * self.radius, 2 * self.radius
        )
        self.vx = cfg.BALL_SPEED_X
        self.vy = cfg.BALL_SPEED_Y
        self.stuck = True
        self.trail = []

    def launch(self) -> None:
        self.stuck = False

    def update(self) -> None:
        """ Updates the Ball's position for each frame. """
        if self.stuck:
            return
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.trail.append(self.rect.center)
        if len(self.trail) > cfg.TRAIL_LENGTH:
            self.trail.pop(0)

    def scale_speed(self, factor: float) -> None:
        """ Ball Speed Up / Down power-ups: scales velocity, kept within limits. """
        for axis in ("vx", "vy"):
            v = getattr(self, axis) * factor
            sign = -1 if v < 0 else 1
            speed = min(cfg.BALL_SPEED_MAX, max(cfg.BALL_SPEED_MIN, abs(v)))
            setattr(self, axis, sign * speed)

    def draw(self, screen: pygame.Surface) -> None:
        """ Renders the Ball and its motion trail. """
        for i, pos in enumerate(self.trail):
            fade = int(cfg.BALL_RADIUS * (i + 1) / (len(self.trail) + 1))
            if fade > 0:
                pygame.draw.circle(screen, cfg.GRAY, pos, fade)
        pygame.draw.circle(screen, cfg.BALL_COLOR, self.rect.center, self.radius)


class Bonus:
    """ A power-up capsule that falls from a destroyed brick. """

    def __init__(self, x: int, y: int, kind: str) -> None:
        self.kind = kind
        self.rect = pygame.Rect(0, 0, cfg.BONUS_W, cfg.BONUS_H)
        self.rect.center = (x, y)

    def update(self) -> None:
        self.rect.y += cfg.BONUS_FALL_SPEED

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        color = cfg.BONUS_COLORS[self.kind]
        pygame.draw.rect(screen, color, self.rect, border_radius=4)
        label = font.render(cfg.BONUS_LETTER[self.kind], True, cfg.BLACK)
        screen.blit(label, label.get_rect(center=self.rect.center))


class Laser:
    """ A projectile fired upward by the paddle. """

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(0, 0, cfg.LASER_W, cfg.LASER_H)
        self.rect.midbottom = (x, y)

    def update(self) -> None:
        self.rect.y -= cfg.LASER_SPEED

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, cfg.MAGENTA, self.rect)


class Particle:
    """ A short-lived spark from a brick burst. """

    def __init__(self, x: int, y: int, color) -> None:
        speed = random.uniform(*cfg.PARTICLE_SPEED)
        self.x = float(x)
        self.y = float(y)
        self.vx = speed * random.uniform(-1, 1)
        self.vy = speed * random.uniform(-1, 1)
        self.life = random.randint(*cfg.PARTICLE_LIFETIME)
        self.color = color

    def update(self) -> None:
        self.vy += cfg.PARTICLE_GRAVITY
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    @property
    def alive(self) -> bool:
        return self.life > 0

    def draw(self, screen: pygame.Surface) -> None:
        r = max(1, self.life // 6)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), r)