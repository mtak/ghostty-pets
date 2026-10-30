"""Draw editable, pixel-exact M4 corgi and backyard PNG source sheets."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PET_DIR = ROOT / "assets/pets/corgi"
SCENE_DIR = ROOT / "assets/environments/backyard"

# A small fixed palette keeps fur readable on dark and light terminals.
O = (42, 35, 42, 255)       # outline
K = (51, 46, 54, 255)       # black fur
KH = (87, 79, 82, 255)      # black-fur highlight
T = (206, 132, 72, 255)     # tan
TH = (232, 170, 99, 255)    # tan highlight
TS = (151, 91, 59, 255)     # tan shadow
W = (250, 233, 198, 255)    # white fur
WS = (207, 197, 176, 255)   # white-fur shadow
E = (17, 20, 27, 255)       # eye and nose
P = (220, 105, 112, 255)    # tongue

# Backyard palette is separate from the pet palette in compiled GLSL.
WOOD = (164, 106, 67, 255)
WOOD_LIGHT = (204, 150, 91, 255)
ROOF = (154, 72, 63, 255)
ROOF_LIGHT = (199, 100, 72, 255)
GRASS = (74, 140, 80, 255)
GRASS_LIGHT = (108, 178, 93, 255)
GRASS_DARK = (49, 105, 66, 255)
LEAF = (122, 169, 84, 255)
FLOWER = (246, 217, 122, 255)
BLUE = (112, 181, 197, 255)
BALL = (218, 110, 91, 255)


def _image(width: int, height: int) -> Image.Image:
    return Image.new("RGBA", (width, height), (0, 0, 0, 0))


def _standing(frame: int, pose: str) -> Image.Image:
    image = _image(28, 24)
    d = ImageDraw.Draw(image)
    bob = (0, -1, 0, 1, 0, -1)[frame % 6] if pose == "walk" else (1 if pose == "breathe" and frame == 1 else 0)
    tail_y = 10 + (frame % 2 if pose in ("walk", "happy", "play") else 0)
    d.rectangle((1, tail_y, 5, tail_y + 2), fill=O)
    d.rectangle((2, tail_y, 5, tail_y + 1), fill=K)
    d.rectangle((4, 9 + bob, 20, 18 + bob), fill=O)
    d.rectangle((5, 10 + bob, 19, 17 + bob), fill=T)
    d.rectangle((6, 10 + bob, 16, 13 + bob), fill=K)
    d.rectangle((7, 10 + bob, 14, 11 + bob), fill=KH)
    d.rectangle((10, 16 + bob, 18, 17 + bob), fill=W)
    d.rectangle((6, 14 + bob, 9, 16 + bob), fill=TH)
    # Short legs alternate in the walk, while other poses keep their paws planted.
    leg_shift = ((frame % 3) - 1) if pose == "walk" else 0
    d.rectangle((5 + leg_shift, 18 + bob, 8 + leg_shift, 22), fill=O)
    d.rectangle((6 + leg_shift, 18 + bob, 7 + leg_shift, 21), fill=T)
    d.rectangle((5 + leg_shift, 22, 8 + leg_shift, 22), fill=W)
    d.rectangle((16 - leg_shift, 18 + bob, 19 - leg_shift, 22), fill=O)
    d.rectangle((17 - leg_shift, 18 + bob, 18 - leg_shift, 21), fill=W)
    d.rectangle((16 - leg_shift, 22, 20 - leg_shift, 22), fill=W)
    head_shift = -1 if pose == "look" and frame == 2 else 0
    head_bob = -1 if pose == "play" and frame in (1, 3) else 0
    hy = 7 + bob + head_shift + head_bob
    d.polygon(((18, hy + 1), (24, hy), (27, hy + 3), (27, hy + 9), (21, hy + 10), (17, hy + 7)), fill=O)
    d.rectangle((19, hy + 2, 25, hy + 8), fill=T)
    d.rectangle((20, hy + 2, 24, hy + 3), fill=TH)
    d.polygon(((19, hy + 2), (19, hy - 5), (22, hy - 4), (23, hy + 2)), fill=O)
    d.polygon(((20, hy + 1), (20, hy - 3), (21, hy - 3), (22, hy + 1)), fill=TH)
    d.polygon(((23, hy + 1), (24, hy - 6), (26, hy - 4), (26, hy + 2)), fill=O)
    d.polygon(((24, hy + 1), (25, hy - 3), (25, hy + 1)), fill=TH)
    d.rectangle((22, hy + 3, 23, hy + 7), fill=W)
    d.rectangle((23, hy + 7, 27, hy + 9), fill=W)
    d.rectangle((19, hy + 8, 22, hy + 10), fill=W)
    d.point((27, hy + 7), fill=E)
    closed = pose == "blink" and frame in (1, 2)
    if closed:
        d.line((23, hy + 5, 24, hy + 5), fill=E)
    else:
        eye_x = 24 if pose == "look" and frame == 1 else 23
        d.point((eye_x, hy + 5), fill=E)
    if pose in ("happy", "play"):
        d.rectangle((25, hy + 10, 26, hy + 11 + frame % 2), fill=P)
    return image


def _sitting(frame: int, pose: str) -> Image.Image:
    image = _standing(frame, "idle")
    d = ImageDraw.Draw(image)
    d.rectangle((3, 14, 18, 23), fill=(0, 0, 0, 0))
    d.rectangle((4, 13, 18, 21), fill=O)
    d.rectangle((5, 14, 17, 20), fill=T)
    d.rectangle((5, 14, 14, 16), fill=K)
    d.rectangle((8, 18, 16, 20), fill=W)
    d.rectangle((4, 21, 11, 22), fill=O)
    d.rectangle((15, 20, 19, 22), fill=W)
    if pose == "scratch":
        # A hind paw comes up toward the cheek on alternating frames.
        d.rectangle((15, 13 - frame % 2, 17, 17), fill=O)
        d.rectangle((16, 13 - frame % 2, 17, 15), fill=W)
    return image


def _sleeping(frame: int) -> Image.Image:
    image = _image(28, 24)
    d = ImageDraw.Draw(image)
    raise_y = 1 if frame == 1 else 0
    d.rectangle((3, 16 - raise_y, 22, 21), fill=O)
    d.rectangle((4, 17 - raise_y, 21, 20), fill=T)
    d.rectangle((5, 16 - raise_y, 15, 18 - raise_y), fill=K)
    d.rectangle((7, 20, 18, 21), fill=W)
    d.rectangle((20, 15 - raise_y, 27, 21), fill=O)
    d.rectangle((21, 16 - raise_y, 26, 20), fill=T)
    d.rectangle((23, 19, 27, 21), fill=W)
    d.rectangle((21, 13 - raise_y, 24, 16), fill=O)
    d.line((23, 18, 24, 18), fill=E)
    d.point((27, 19), fill=E)
    return image


def _stretching(frame: int) -> Image.Image:
    image = _standing(frame, "idle")
    d = ImageDraw.Draw(image)
    d.rectangle((16, 15, 27, 23), fill=(0, 0, 0, 0))
    d.rectangle((17, 15, 23, 18 + frame % 2), fill=T)
    d.rectangle((22, 17, 27, 19), fill=W)
    d.rectangle((23, 19, 26, 22), fill=O)
    d.rectangle((23, 22, 27, 22), fill=W)
    return image


def corgi_frame(pose: str, frame: int) -> Image.Image:
    if pose == "sleep":
        return _sleeping(frame)
    if pose == "sit":
        return _standing(0, "idle") if frame == 0 else _sitting(frame, "sit")
    if pose == "stand":
        return _sitting(0, "sit") if frame == 0 else _standing(frame, "idle")
    if pose == "wake":
        return _sleeping(frame) if frame == 0 else (_sitting(frame, "sit") if frame == 1 else _standing(frame, "idle"))
    if pose == "stretch":
        return _stretching(frame)
    if pose == "scratch":
        return _sitting(frame, "scratch")
    return _standing(frame, pose)


PET_ROWS = (
    ("idle", 4), ("breathe", 4), ("look", 4), ("stand", 4),
    ("walk", 6), ("play", 4), ("sit", 4), ("stretch", 4),
    ("sleep", 4), ("wake", 4), ("scratch", 4), ("happy", 4),
    ("blink", 4),
)


def pet_sheet() -> Image.Image:
    sheet = _image(28 * 6, 24 * len(PET_ROWS))
    for row, (pose, count) in enumerate(PET_ROWS):
        for frame in range(count):
            sheet.alpha_composite(corgi_frame(pose, frame), (frame * 28, row * 24))
    return sheet


def ground() -> Image.Image:
    image = _image(110, 7)
    d = ImageDraw.Draw(image)
    for x in range(0, 110, 3):
        d.line((x, 3 + (x % 4 == 0), x + 2, 3), fill=GRASS)
        d.point((x + 1, 2 if x % 5 == 0 else 4), fill=GRASS_LIGHT)
    for x in range(2, 110, 9):
        d.line((x, 5, x + 5, 5), fill=GRASS_DARK)
    return image


def tree_trunk() -> Image.Image:
    image = _image(14, 26)
    d = ImageDraw.Draw(image)
    d.rectangle((5, 3, 9, 25), fill=O)
    d.rectangle((6, 4, 8, 24), fill=WOOD)
    d.line((7, 5, 7, 22), fill=WOOD_LIGHT)
    d.line((5, 9, 1, 5), fill=O, width=2)
    d.line((9, 11, 13, 7), fill=O, width=2)
    return image


def tree_canopy() -> Image.Image:
    sheet = _image(26 * 2, 18)
    for frame in range(2):
        image = _image(26, 18)
        d = ImageDraw.Draw(image)
        shift = frame
        d.ellipse((2 + shift, 4, 16 + shift, 17), fill=GRASS_DARK)
        d.ellipse((9 + shift, 0, 24 + shift, 16), fill=GRASS_DARK)
        d.ellipse((3 + shift, 2, 21 + shift, 15), fill=GRASS)
        d.rectangle((7 + shift, 5, 18 + shift, 8), fill=LEAF)
        d.point((20 + shift, 5), fill=GRASS_LIGHT)
        d.point((5 + shift, 10), fill=GRASS_LIGHT)
        sheet.alpha_composite(image, (frame * 26, 0))
    return sheet


def doghouse() -> Image.Image:
    image = _image(31, 26)
    d = ImageDraw.Draw(image)
    d.polygon(((0, 11), (15, 0), (30, 11), (27, 14), (15, 5), (3, 14)), fill=O)
    d.polygon(((2, 11), (15, 2), (28, 11), (26, 12), (15, 4), (4, 12)), fill=ROOF)
    d.line((5, 9, 15, 2, 25, 9), fill=ROOF_LIGHT)
    d.rectangle((4, 13, 26, 25), fill=O)
    d.rectangle((5, 14, 25, 24), fill=WOOD)
    for y in (17, 21):
        d.line((5, y, 25, y), fill=WOOD_LIGHT)
    d.ellipse((11, 16, 20, 26), fill=O)
    d.ellipse((12, 17, 19, 26), fill=K)
    d.rectangle((14, 17, 16, 22), fill=WOOD)
    return image


def flowers() -> Image.Image:
    sheet = _image(20 * 2, 9)
    for frame in range(2):
        image = _image(20, 9)
        d = ImageDraw.Draw(image)
        for x, color in ((3, FLOWER), (10, W), (17, P)):
            shift = frame if x != 10 else -frame
            d.line((x, 8, x + shift, 4), fill=GRASS_DARK)
            d.rectangle((x - 1 + shift, 2, x + 1 + shift, 4), fill=color)
            d.point((x + shift, 3), fill=WOOD)
        sheet.alpha_composite(image, (frame * 20, 0))
    return sheet


def leaf() -> Image.Image:
    sheet = _image(4 * 3, 4)
    for frame in range(3):
        image = _image(4, 4)
        d = ImageDraw.Draw(image)
        d.polygon(((1, 0), (3, 1 + frame % 2), (2, 3), (0, 2)), fill=LEAF)
        d.point((1, 2), fill=GRASS_DARK)
        sheet.alpha_composite(image, (frame * 4, 0))
    return sheet


def butterfly() -> Image.Image:
    sheet = _image(8 * 4, 6)
    for frame in range(4):
        image = _image(8, 6)
        d = ImageDraw.Draw(image)
        wing = 0 if frame % 2 else 1
        d.polygon(((3, 3), (0, 1 - wing), (1, 4), (3, 4)), fill=BLUE)
        d.polygon(((4, 3), (7, 1 - wing), (6, 4), (4, 4)), fill=FLOWER)
        d.line((3, 2, 4, 5), fill=O)
        sheet.alpha_composite(image, (frame * 8, 0))
    return sheet


def ball() -> Image.Image:
    sheet = _image(6 * 4, 6)
    for frame in range(4):
        image = _image(6, 6)
        d = ImageDraw.Draw(image)
        d.ellipse((0, 0, 5, 5), fill=O)
        d.ellipse((1, 1, 4, 4), fill=BALL)
        d.line((1 + frame % 3, 1, 2 + frame % 3, 4), fill=W)
        sheet.alpha_composite(image, (frame * 6, 0))
    return sheet


def outputs() -> dict[Path, Image.Image]:
    return {
        PET_DIR / "corgi-v1.png": pet_sheet(),
        SCENE_DIR / "ground.png": ground(),
        SCENE_DIR / "tree-trunk.png": tree_trunk(),
        SCENE_DIR / "tree-canopy.png": tree_canopy(),
        SCENE_DIR / "doghouse.png": doghouse(),
        SCENE_DIR / "flowers.png": flowers(),
        SCENE_DIR / "leaf.png": leaf(),
        SCENE_DIR / "butterfly.png": butterfly(),
        SCENE_DIR / "ball.png": ball(),
    }


def main() -> None:
    for path, image in outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)


if __name__ == "__main__":
    main()
