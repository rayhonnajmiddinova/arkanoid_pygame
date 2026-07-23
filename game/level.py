from __future__ import annotations
import settings as cfg
from game.entities import Brick

def load_level(level_number):
    path = cfg.LEVELS_DIR / f"level{level_number}.txt"
    with path.open(encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    rows = len(lines)
    cols = max(len(line.split()) for line in lines)
    bricks = []
    for r, line in enumerate(lines):
        for c, token in enumerate(line.split()):
            if token == '.':
                continue
            if token.isdigit():
                hp = int(token)
                if hp in (0,1,2):
                    bricks.append(Brick(c, r, hp))
    wall_rows = (cfg.HEIGHT - cfg.TOP_OFFSET) // cfg.BRICK_HEIGHT + 2
    for c in range(cfg.FIELD_COLS):
        bricks.append(Brick(c, -1, -1))
    for r in range(-1, wall_rows):
        bricks.append(Brick(-1, r, -1))
        bricks.append(Brick(cfg.FIELD_COLS, r, -1))
    return bricks, rows, cols
