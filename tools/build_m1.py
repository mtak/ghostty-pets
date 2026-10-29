"""Build the M1 static Ghostty sprite proof from an editable RGBA PNG."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "pets" / "corgi" / "m1-silhouette.png"
GENERATOR_VERSION = "m1.1"
INSET = 12


def read_sprite(path: Path) -> tuple[int, int, list[tuple[int, int, int]], list[int]]:
    with Image.open(path) as image:
        if image.format != "PNG" or image.mode != "RGBA":
            raise ValueError("M1 source must be an RGBA PNG")
        width, height = image.size
        if not (1 <= width <= 64 and 1 <= height <= 64):
            raise ValueError("M1 sprite dimensions must be 1..64 pixels")
        palette: list[tuple[int, int, int]] = []
        indices: list[int] = []
        for red, green, blue, alpha in image.get_flattened_data():
            if alpha not in (0, 255):
                raise ValueError("M1 sprite alpha must be fully transparent or opaque")
            if alpha == 0:
                indices.append(0)
                continue
            color = (red, green, blue)
            if color not in palette:
                if len(palette) == 15:
                    raise ValueError("M1 sprite may contain at most 15 opaque colors")
                palette.append(color)
            indices.append(palette.index(color) + 1)
    return width, height, palette, indices


def pack_nibbles(indices: list[int]) -> list[int]:
    packed: list[int] = []
    for start in range(0, len(indices), 8):
        word = 0
        for shift, index in enumerate(indices[start : start + 8]):
            word |= index << (4 * shift)
        packed.append(word)
    return packed


def generate(source: Path, scale: int) -> str:
    if scale not in (1, 2):
        raise ValueError("M1 scale must be 1 or 2")
    width, height, palette, indices = read_sprite(source)
    packed = pack_nibbles(indices)
    fingerprint = hashlib.sha256(source.read_bytes()).hexdigest()
    words = ",\n    ".join(f"0x{word:08x}u" for word in packed)
    colors = ["vec3(0.0)"] + [
        f"vec3({red}.0, {green}.0, {blue}.0) / 255.0"
        for red, green, blue in palette
    ]
    colors += ["vec3(0.0)"] * (16 - len(colors))
    color_source = ",\n    ".join(colors)
    return f"""// Ghostty Pets M1 static sprite proof
// Generator: {GENERATOR_VERSION}; source SHA-256: {fingerprint}
// Source: assets/pets/corgi/m1-silhouette.png; scale: {scale}x
const int SPRITE_WIDTH = {width};
const int SPRITE_HEIGHT = {height};
const int SPRITE_SCALE = {scale};
const int SPRITE_INSET = {INSET};
const uint SPRITE_DATA[{len(packed)}] = uint[{len(packed)}](
    {words}
);
const vec3 SPRITE_PALETTE[16] = vec3[16](
    {color_source}
);

void mainImage(out vec4 fragColor, in vec2 fragCoord) {{
    // Pixel centers avoid interpolation between terminal texels.
    vec2 uv = (floor(fragCoord) + vec2(0.5)) / iResolution.xy;
    vec4 terminal = texture(iChannel0, uv);
    ivec2 sizePx = ivec2(SPRITE_WIDTH, SPRITE_HEIGHT) * SPRITE_SCALE;
    // Ghostty fragment Y increases upward from the bottom of the surface.
    ivec2 origin = ivec2(int(iResolution.x) - SPRITE_INSET - sizePx.x, SPRITE_INSET);
    ivec2 screenPx = ivec2(floor(fragCoord));
    if (origin.x < 0 || origin.y < 0 ||
        screenPx.x < origin.x || screenPx.y < origin.y ||
        screenPx.x >= origin.x + sizePx.x || screenPx.y >= origin.y + sizePx.y) {{
        fragColor = terminal;
        return;
    }}

    ivec2 sourcePx = (screenPx - origin) / SPRITE_SCALE;
    // PNG rows run top-down, opposite to fragment Y.
    int linear = (SPRITE_HEIGHT - 1 - sourcePx.y) * SPRITE_WIDTH + sourcePx.x;
    uint word = SPRITE_DATA[linear / 8];
    uint index = (word >> uint(4 * (linear % 8))) & 15u;
    fragColor = index == 0u
        ? terminal
        : vec4(SPRITE_PALETTE[int(index)], terminal.a);
}}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", type=int, choices=(1, 2), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    shader = generate(SOURCE, args.scale)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(shader, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
