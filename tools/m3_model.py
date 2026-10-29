"""Validated M3 source model and pure timeline evaluator.

The evaluator mirrors the generated shader and lets tests probe arbitrary times.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class Clip:
    name: str
    row: int
    durations_ms: tuple[int, ...]
    loop: bool
    speed: float


@dataclass(frozen=True)
class Phase:
    clip: str
    duration_ms: int
    from_x: int
    to_x: int
    face: str


@dataclass(frozen=True)
class Episode:
    name: str
    weight: int
    phases: tuple[Phase, ...]


@dataclass(frozen=True)
class Pet:
    name: str
    sheet: Path
    frame_width: int
    frame_height: int
    anchor_x: int
    anchor_y: int
    clips: tuple[Clip, ...]
    palette: tuple[tuple[int, int, int], ...]
    pixels: tuple[int, ...]


@dataclass(frozen=True)
class Scene:
    name: str
    width: int
    height: int
    ground_y: int
    home_x: int
    inset: int
    seed: int
    slot_ms: int
    episodes: tuple[Episode, ...]


@dataclass(frozen=True)
class Pose:
    mode: str
    episode: str
    clip: str
    frame: int
    x: float
    face: str
    opacity: float


def _object(path: Path, version: int = 1) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(value, dict) or type(value.get("schema_version")) is not int
            or value["schema_version"] != version):
        raise ValueError(f"{path}: expected schema_version {version} object")
    return value


def _positive_int(value: object, label: str, maximum: int = 1_000_000) -> int:
    if type(value) is not int or not 0 < value <= maximum:
        raise ValueError(f"{label} must be an integer in 1..{maximum}")
    return value


def _pair(value: object, label: str) -> tuple[int, int]:
    if not isinstance(value, list) or len(value) != 2 or any(type(x) is not int for x in value):
        raise ValueError(f"{label} must be a pair of integers")
    return value[0], value[1]


def load_pet(path: Path) -> Pet:
    data = _object(path)
    name = data.get("id")
    if not isinstance(name, str) or not name:
        raise ValueError("pet id is required")
    sheet_name = data.get("sheet")
    if not isinstance(sheet_name, str) or Path(sheet_name).name != sheet_name:
        raise ValueError("pet sheet must be a local PNG filename")
    sheet = path.parent / sheet_name
    width, height = _pair(data.get("frame_size"), "frame_size")
    if not (1 <= width <= 64 and 1 <= height <= 64):
        raise ValueError("frame_size must be 1..64 pixels per axis")
    anchor_x, anchor_y = _pair(data.get("anchor"), "anchor")
    if not (0 <= anchor_x < width and 0 <= anchor_y < height):
        raise ValueError("anchor must lie within a frame")
    definitions = data.get("clips")
    if not isinstance(definitions, dict) or not 1 <= len(definitions) <= 32:
        raise ValueError("clips must contain 1..32 entries")
    clips: list[Clip] = []
    used_rows: set[int] = set()
    for clip_name, item in definitions.items():
        if not isinstance(clip_name, str) or not clip_name or not isinstance(item, dict):
            raise ValueError("invalid clip definition")
        row = item.get("row")
        if type(row) is not int or row < 0 or row in used_rows:
            raise ValueError(f"{clip_name}: row must be unique and nonnegative")
        used_rows.add(row)
        durations = item.get("durations_ms")
        if not isinstance(durations, list) or not 1 <= len(durations) <= 8:
            raise ValueError(f"{clip_name}: 1..8 frame durations required")
        durations = tuple(_positive_int(x, f"{clip_name} duration", 60_000) for x in durations)
        loop = item.get("loop")
        if type(loop) is not bool:
            raise ValueError(f"{clip_name}: loop must be boolean")
        speed = item.get("speed", 1.0)
        if type(speed) not in (int, float) or not 0.1 <= speed <= 4.0:
            raise ValueError(f"{clip_name}: speed must be 0.1..4")
        clips.append(Clip(clip_name, row, durations, loop, float(speed)))
    with Image.open(sheet) as image:
        if image.format != "PNG" or image.mode != "RGBA":
            raise ValueError("sheet must be an RGBA PNG")
        if image.width % width or image.height % height:
            raise ValueError("sheet geometry must align to frame size")
        if image.width > 512 or image.height > 1024:
            raise ValueError("sheet exceeds bounded dimensions")
        columns, rows = image.width // width, image.height // height
        if rows <= max(used_rows) or any(len(c.durations_ms) > columns for c in clips):
            raise ValueError("clip frames extend beyond sprite sheet")
        rgba = image.load()
        palette: list[tuple[int, int, int]] = []
        pixels: list[int] = []
        for clip in clips:
            for frame in range(len(clip.durations_ms)):
                for y in range(height):
                    for x in range(width):
                        red, green, blue, alpha = rgba[frame * width + x, clip.row * height + y]
                        if alpha not in (0, 255):
                            raise ValueError("sheet alpha must be binary")
                        if alpha == 0:
                            pixels.append(0)
                            continue
                        color = (red, green, blue)
                        if color not in palette:
                            if len(palette) >= 15:
                                raise ValueError("sheet exceeds 15 opaque colors")
                            palette.append(color)
                        pixels.append(palette.index(color) + 1)
    return Pet(name, sheet, width, height, anchor_x, anchor_y, tuple(clips), tuple(palette), tuple(pixels))


def load_scene(path: Path, pet: Pet) -> Scene:
    data = _object(path, version=2)
    name = data.get("id")
    if not isinstance(name, str) or not name:
        raise ValueError("scene id is required")
    width, height = _pair(data.get("canvas"), "canvas")
    if not (1 <= width <= 256 and 1 <= height <= 128):
        raise ValueError("canvas must be within 256x128")
    ground_y = data.get("ground_y")
    home_x = data.get("home_x")
    inset = data.get("inset")
    seed = data.get("seed")
    if any(type(x) is not int for x in (ground_y, home_x, inset, seed)):
        raise ValueError("scene anchors, inset and seed must be integers")
    if not (0 <= ground_y < height and 0 <= home_x < width and 0 <= inset <= 128 and 0 <= seed <= 2**31 - 1):
        raise ValueError("scene anchors, inset or seed out of range")
    slot_ms = _positive_int(data.get("slot_ms"), "slot_ms", 120_000)
    if "quiet_ms" in data or "sleep_ms" in data:
        raise ValueError("cursor activity thresholds are unsupported in scene schema 2")
    definitions = data.get("episodes")
    if not isinstance(definitions, list) or not 1 <= len(definitions) <= 32:
        raise ValueError("episodes must contain 1..32 entries")
    clips = {clip.name for clip in pet.clips}
    if not {"idle", "sleep", "wake"} <= clips:
        raise ValueError("idle, sleep and wake clips are required")
    episodes: list[Episode] = []
    names: set[str] = set()
    for item in definitions:
        if not isinstance(item, dict):
            raise ValueError("invalid episode")
        episode_name = item.get("id")
        if not isinstance(episode_name, str) or not episode_name or episode_name in names:
            raise ValueError("episode id must be unique")
        names.add(episode_name)
        if "mode" in item:
            raise ValueError(f"{episode_name}: cursor activity modes are unsupported")
        weight = _positive_int(item.get("weight"), "episode weight", 100)
        phase_items = item.get("phases")
        if not isinstance(phase_items, list) or not 1 <= len(phase_items) <= 16:
            raise ValueError(f"{episode_name}: 1..16 phases required")
        phases: list[Phase] = []
        total = 0
        previous_x = 0
        for phase_item in phase_items:
            if not isinstance(phase_item, dict):
                raise ValueError("invalid phase")
            clip, face = phase_item.get("clip"), phase_item.get("face")
            if clip not in clips or face not in ("left", "right"):
                raise ValueError(f"{episode_name}: invalid clip or face")
            duration = _positive_int(phase_item.get("duration_ms"), "phase duration", slot_ms)
            from_x, to_x = phase_item.get("from_x"), phase_item.get("to_x")
            if type(from_x) is not int or type(to_x) is not int or from_x != previous_x:
                raise ValueError(f"{episode_name}: discontinuous phase position")
            for x in (from_x, to_x):
                left = home_x + x - pet.anchor_x
                bottom = ground_y - (pet.frame_height - 1 - pet.anchor_y)
                if not (0 <= left and left + pet.frame_width <= width and 0 <= bottom and bottom + pet.frame_height <= height):
                    raise ValueError(f"{episode_name}: sprite leaves scene canvas")
            phases.append(Phase(clip, duration, from_x, to_x, face))
            previous_x = to_x
            total += duration
        if previous_x != 0 or total > slot_ms:
            raise ValueError(f"{episode_name}: episode must return home within slot")
        episodes.append(Episode(episode_name, weight, tuple(phases)))
    return Scene(name, width, height, ground_y, home_x, inset, seed, slot_ms, tuple(episodes))


def _hash_slot(slot: int, seed: int) -> int:
    x = ((slot & 0xFFFFFFFF) ^ seed) & 0xFFFFFFFF
    x ^= x >> 16
    x = (x * 0x7FEB352D) & 0xFFFFFFFF
    x ^= x >> 15
    x = (x * 0x846CA68B) & 0xFFFFFFFF
    return x ^ (x >> 16)


def select_episode(scene: Scene, slot: int) -> Episode:
    choice = _hash_slot(slot, scene.seed) % sum(e.weight for e in scene.episodes)
    for episode in scene.episodes:
        if choice < episode.weight:
            return episode
        choice -= episode.weight
    raise AssertionError("unreachable episode selection")


def select_frame(clip: Clip, elapsed_ms: float) -> int:
    total = sum(clip.durations_ms)
    t = max(0, int(elapsed_ms * clip.speed))
    if clip.loop:
        t %= total
    else:
        t = min(t, total - 1)
    for index, duration in enumerate(clip.durations_ms):
        if t < duration:
            return index
        t -= duration
    raise AssertionError("unreachable frame selection")


def evaluate(scene: Scene, pet: Pet, time_s: float, cursor_change_s: float, focus_s: float, focused: bool) -> Pose:
    clips = {clip.name: clip for clip in pet.clips}
    if not focused:
        return Pose("sleeping", "sleep", "sleep", select_frame(clips["sleep"], time_s * 1000), 0, "right", 1)
    # Cursor changes are deliberately absent from behavior evaluation.
    # The parameter remains in the public test signature to prove invariance.
    focus_age_ms = max(0.0, (time_s - focus_s) * 1000)
    fade = 1.0 if focus_s <= 0 else min(1.0, focus_age_ms / 650.0)
    if focus_s > 0 and focus_age_ms < 650:
        return Pose("active", "wake", "wake", select_frame(clips["wake"], focus_age_ms), 0, "right", fade)
    absolute_ms = max(0.0, time_s * 1000)
    slot = int(absolute_ms // scene.slot_ms)
    local_ms = absolute_ms - slot * scene.slot_ms
    if slot * scene.slot_ms < focus_s * 1000:
        return Pose("active", "refocus-rest", "idle", select_frame(clips["idle"], local_ms), 0, "right", fade)
    episode = select_episode(scene, slot)
    for phase in episode.phases:
        if local_ms < phase.duration_ms:
            t = local_ms / phase.duration_ms
            eased = t * t * (3 - 2 * t)
            x = phase.from_x + (phase.to_x - phase.from_x) * eased
            return Pose("active", episode.name, phase.clip, select_frame(clips[phase.clip], local_ms), x, phase.face, fade)
        local_ms -= phase.duration_ms
    return Pose("active", episode.name, "idle", select_frame(clips["idle"], local_ms), 0, "right", fade)
