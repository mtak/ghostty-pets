"""Pure reference for M5's bounded integer-scale layout selection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Layout:
    mode: str
    scale: int
    origin: tuple[int, int]
    size: tuple[int, int]


def select_layout(
    resolution: tuple[int, int],
    max_scale: int,
    scene_size: tuple[int, int],
    pet_size: tuple[int, int],
    inset: int,
) -> Layout | None:
    """Select complete scene first, then stationary pet, else transparent fallback."""
    width, height = resolution
    if width < 0 or height < 0 or max_scale not in (1, 2, 3) or inset < 0:
        raise ValueError("invalid resolution, preset scale, or inset")
    for mode, (art_width, art_height) in (("full", scene_size), ("pet-only", pet_size)):
        if art_width <= 0 or art_height <= 0:
            raise ValueError("art dimensions must be positive")
        for scale in range(max_scale, 0, -1):
            pixel_width, pixel_height = art_width * scale, art_height * scale
            if width >= pixel_width + 2 * inset and height >= pixel_height + 2 * inset:
                return Layout(mode, scale, (width - inset - pixel_width, inset),
                              (pixel_width, pixel_height))
    return None
