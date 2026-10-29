"""Regenerate the deliberately rough M3 animation fixture PNG."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/pets/corgi/m3-placeholder.png"
COUNTS = (2, 3, 2, 2, 3, 3, 2, 2, 2, 2)
BLACK = (42, 36, 42, 255)
TAN = (218, 154, 91, 255)
CREAM = (250, 227, 184, 255)
EYE = (21, 23, 29, 255)
BLUSH = (229, 124, 119, 255)


def make() -> Image.Image:
    sheet = Image.new("RGBA", (48, 120), (0, 0, 0, 0))
    for row, count in enumerate(COUNTS):
        for frame in range(count):
            tile = Image.new("RGBA", (16, 12), (0, 0, 0, 0))
            draw = ImageDraw.Draw(tile)
            body_y = 8 if row == 8 else (6 if row == 7 else 5)
            if (row, frame) in ((1, 1), (3, 1), (4, 1), (5, 1), (6, 0), (7, 1)):
                body_y = 4
            if (row, frame) in ((8, 1), (9, 0)):
                body_y = 7
            draw.rectangle((2, body_y, 11, 9), fill=BLACK)
            draw.rectangle((3, body_y, 10, 9), fill=TAN)
            if body_y <= 6:
                draw.rectangle((5, body_y + 2, 8, 8), fill=CREAM)
            if row == 8:
                draw.rectangle((10, 7, 14, 9), fill=TAN)
                draw.line((12, 8, 13, 8), fill=EYE)
            else:
                head_y = 2 if (row, frame) in ((2, 1), (5, 1), (7, 1)) else (5 if (row, frame) == (9, 0) else 3)
                draw.rectangle((10, head_y, 14, 7), fill=TAN)
                draw.rectangle((11, head_y - 2, 12, head_y), fill=TAN)
                draw.rectangle((13, head_y - 2, 14, head_y), fill=TAN)
                draw.rectangle((12, head_y + 2, 14, max(6, head_y + 2)), fill=CREAM)
                if (row, frame) != (0, 1):
                    draw.point((13, head_y + 1), fill=EYE)
                draw.point((15, head_y + 3), fill=BLACK)
            if row in (3, 4, 5, 7, 9):
                step = frame % 2 if row == 4 else 0
                draw.rectangle((4 + step, 9, 5 + step, 11), fill=BLACK)
                draw.rectangle((9 - step, 9, 10 - step, 11), fill=BLACK)
            elif row == 8:
                draw.rectangle((5, 10, 10, 10), fill=BLACK)
            else:
                draw.rectangle((4, 9, 6, 10), fill=BLACK)
                draw.rectangle((9, 9, 11, 10), fill=BLACK)
            draw.rectangle((1, body_y + 1, 2, body_y + 2), fill=BLACK)
            if row == 5:
                draw.point((14, 1 if frame == 1 else 2), fill=BLUSH)
            sheet.alpha_composite(tile, (frame * 16, row * 12))
    return sheet


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    make().save(OUTPUT)
