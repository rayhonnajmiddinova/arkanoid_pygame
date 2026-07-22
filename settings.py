"""settings.py – static config for in-game variables.

No logic here.
Feel free to experiment with variables.
"""

from pathlib import Path

# --- Paths -------------------------------------------------------------------
# Relative paths to resolve file names
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LEVELS_DIR = BASE_DIR / "levels"

# --- Screen, Timer -----------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# --- Playing Field -----------------------------------------------------------
BRICK_WIDTH, BRICK_HEIGHT = 60, 20
TOP_OFFSET = 60  # Top Offset for UI status bar
FIELD_LEFT = 40  # Left Offset for bricks

# Calculation of the playing field rows and cols
FIELD_COLS = (WIDTH - 2 * FIELD_LEFT) // BRICK_WIDTH
FIELD_RIGHT = FIELD_LEFT + FIELD_COLS * BRICK_WIDTH

# --- Paddle, Ball ------------------------------------------------------------
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 12
PADDLE_SPEED = 7

BALL_RADIUS = 8
BALL_SPEED_X = 4
BALL_SPEED_Y = -5
SLIDE_FACTOR = 0.8
MAX_BALL_SPEED_X = 8

# --- Bonuses -----------------------------------------------------------------
BONUS_PROBABILITY = 0.3  # Chance that destroyed brick will drop a bonus
BONUS_TYPES = ["extend", "multiball", "laser", "extra_life",
               "paddle_shrink", "ball_speed_up", "ball_speed_down"]

# --- Visual Effects ----------------------------------------------------------
TRAIL_LENGTH = 6  # Ball's Motion Trail Length
PARTICLE_COUNT = 10  # Particles in brick's burst
PARTICLE_LIFETIME = (12, 24)  # Min/max frames for the particle to live
PARTICLE_SPEED = (1.5, 4.0)  # Min/max particle speed
PARTICLE_GRAVITY = 0.15  # Particle's acceleration
MAX_PARTICLES = 200  # Max particles number

# --- Colors ------------------------------------------------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (60, 60, 60)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PADDLE_COLOR = CYAN
BALL_COLOR = WHITE

# Brick Color and HP
BRICK_COLORS = {
    2: ORANGE,
    1: RED,
    0: GRAY,        # Indestructible brick
    -1: DARK_GRAY,  # Indestructible Level Boundaries
}

# --- Gameplay additions (added to complete the game) -------------------------
LIVES = 3
MIN_BALL_SPEED_Y = 3            # ball never travels purely horizontally
EXTENDED_PADDLE_WIDTH = 160     # width while "extend" bonus is active
POWERUP_FRAMES = 600            # duration of extend / laser (10s @ 60fps)
MULTIBALL_EXTRA = 2            # extra balls spawned by "multiball"

BONUS_FALL_SPEED = 3
BONUS_W, BONUS_H = 26, 14
BONUS_COLORS = {
    "extend":          GREEN,
    "multiball":       CYAN,
    "laser":           MAGENTA,
    "extra_life":      YELLOW,
    "paddle_shrink":   RED,
    "ball_speed_up":   ORANGE,
    "ball_speed_down": WHITE,
}
BONUS_LETTER = {
    "extend": "E", "multiball": "M", "laser": "L", "extra_life": "+",
    "paddle_shrink": "S", "ball_speed_up": "F", "ball_speed_down": "D",
}

LASER_SPEED = 9
LASER_COOLDOWN = 12             # frames between shots
LASER_W, LASER_H = 4, 14

# --- New power-ups (homework) ------------------------------------------------
SHRUNK_PADDLE_WIDTH = 60        # width while "paddle_shrink" is active
BALL_SPEED_FACTOR = 1.30        # multiplier for "ball_speed_up"
BALL_SLOW_FACTOR = 0.75         # multiplier for "ball_speed_down"
BALL_SPEED_MIN = 2              # ball never slower than this
BALL_SPEED_MAX = 12             # ball never faster than this