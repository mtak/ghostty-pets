"""Render offline M4 source-art previews; these are not Ghostty screenshots."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

if __package__:
    from .build_m4 import DEFAULT_PET, DEFAULT_SCENE, ROOT
    from .m3_model import load_pet
    from .m4_model import evaluate, layer_state, load_scene
else:
    from build_m4 import DEFAULT_PET, DEFAULT_SCENE, ROOT
    from m3_model import load_pet
    from m4_model import evaluate, layer_state, load_scene


OUTPUT = ROOT / "docs/evidence/m4"


def scene_at(time_s: float, background: tuple[int, int, int], focused: bool = True) -> Image.Image:
    pet = load_pet(DEFAULT_PET)
    scene = load_scene(DEFAULT_SCENE, pet)
    pose = evaluate(scene, pet, time_s, 0, focused)
    image = Image.new("RGBA", (scene.width, scene.height), (*background, 255))
    for layer in scene.layers:
        state = layer_state(layer, time_s, focused, pose.object_x)
        if not state.visible:
            continue
        with Image.open(layer.file) as sheet:
            frame = sheet.crop((state.frame * layer.width, 0, (state.frame + 1) * layer.width, layer.height))
        image.alpha_composite(frame, (round(state.x), scene.height - round(state.y) - layer.height))
    clip = next(clip for clip in pet.clips if clip.name == pose.clip)
    with Image.open(pet.sheet) as sheet:
        frame = sheet.crop((pose.frame * pet.frame_width, clip.row * pet.frame_height,
                            (pose.frame + 1) * pet.frame_width, (clip.row + 1) * pet.frame_height))
    if pose.face == "left":
        frame = frame.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    pet_x = scene.home_x + round(pose.x) - pet.anchor_x
    bottom = scene.ground_y - (pet.frame_height - 1 - pet.anchor_y)
    image.alpha_composite(frame, (pet_x, scene.height - bottom - pet.frame_height))
    return image


def montage() -> Image.Image:
    samples = (
        (1.2, (30, 30, 46), "walk left · dark"),
        (26.6, (30, 30, 46), "ball play · dark"),
        (32.5, (247, 243, 232), "falling leaf · light"),
        (45.5, (247, 243, 232), "butterfly · light"),
    )
    scale = 4
    panel_width, panel_height = 110 * scale, 45 * scale
    result = Image.new("RGB", (panel_width * 2, (panel_height + 18) * 2), (24, 23, 31))
    draw = ImageDraw.Draw(result)
    for index, (time_s, background, label) in enumerate(samples):
        x = index % 2 * panel_width
        y = index // 2 * (panel_height + 18)
        draw.text((x + 4, y + 3), label, fill=(245, 236, 216), font=ImageFont.load_default())
        panel = scene_at(time_s, background).convert("RGB").resize((panel_width, panel_height), Image.Resampling.NEAREST)
        result.paste(panel, (x, y + 18))
    return result


def contact_sheet() -> Image.Image:
    pet = load_pet(DEFAULT_PET)
    scale = 5
    width = pet.frame_width * 6 * scale
    row_height = pet.frame_height * scale + 16
    result = Image.new("RGB", (width, row_height * len(pet.clips)), (30, 30, 46))
    draw = ImageDraw.Draw(result)
    with Image.open(pet.sheet) as sheet:
        for row, clip in enumerate(pet.clips):
            draw.text((4, row * row_height + 2), clip.name, fill=(245, 236, 216), font=ImageFont.load_default())
            for frame in range(len(clip.durations_ms)):
                crop = sheet.crop((frame * pet.frame_width, clip.row * pet.frame_height,
                                   (frame + 1) * pet.frame_width, (clip.row + 1) * pet.frame_height))
                tile = crop.resize((pet.frame_width * scale, pet.frame_height * scale), Image.Resampling.NEAREST)
                result.paste(tile, (frame * pet.frame_width * scale, row * row_height + 16), tile)
    return result


def focus_preview() -> Image.Image:
    scale = 5
    width, height = 110 * scale, 45 * scale
    result = Image.new("RGB", (width * 2, height + 18), (24, 23, 31))
    draw = ImageDraw.Draw(result)
    for index, (focused, label) in enumerate(((True, "focused: breathing"), (False, "unfocused: upright doze"))):
        x = index * width
        draw.text((x + 4, 3), label, fill=(245, 236, 216), font=ImageFont.load_default())
        panel = scene_at(12.5, (30, 30, 46), focused).convert("RGB").resize((width, height), Image.Resampling.NEAREST)
        result.paste(panel, (x, 18))
    return result


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    montage().save(OUTPUT / "source-preview.png")
    contact_sheet().save(OUTPUT / "animation-contact-sheet.png")
    focus_preview().save(OUTPUT / "focus-preview.png")


if __name__ == "__main__":
    main()
