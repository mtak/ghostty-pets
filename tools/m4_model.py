"""Validated layered M4 scene model and pure pet/object timeline evaluator."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

if __package__:
    from .m3_model import Pet, _hash_slot, _pair, _positive_int, select_frame
else:
    from m3_model import Pet, _hash_slot, _pair, _positive_int, select_frame


@dataclass(frozen=True)
class Layer:
    name: str
    file: Path
    width: int
    height: int
    durations_ms: tuple[int, ...]
    motion: str
    start: tuple[int, int]
    end: tuple[int, int]
    period_ms: int
    active_ms: int
    phase_ms: int


@dataclass(frozen=True)
class Phase4:
    clip: str
    duration_ms: int
    from_x: int
    to_x: int
    face: str
    object_from_x: int
    object_to_x: int


@dataclass(frozen=True)
class Episode4:
    name: str
    weight: int
    phases: tuple[Phase4, ...]


@dataclass(frozen=True)
class Scene4:
    name: str
    width: int
    height: int
    ground_y: int
    home_x: int
    inset: int
    seed: int
    slot_ms: int
    layers: tuple[Layer, ...]
    interactive_index: int
    palette: tuple[tuple[int, int, int], ...]
    pixels: tuple[int, ...]
    episodes: tuple[Episode4, ...]


@dataclass(frozen=True)
class Pose4:
    mode: str
    episode: str
    clip: str
    frame: int
    x: float
    face: str
    object_x: float
    opacity: float


@dataclass(frozen=True)
class LayerState:
    visible: bool
    x: float
    y: float
    frame: int


def _position(value: object, width: int, height: int, canvas: tuple[int, int], label: str) -> tuple[int, int]:
    x, y = _pair(value, label)
    if not (0 <= x and x + width <= canvas[0] and 0 <= y and y + height <= canvas[1]):
        raise ValueError(f"{label} leaves scene canvas")
    return x, y


def load_scene(path: Path, pet: Pet) -> Scene4:
    data = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or type(data.get("schema_version")) is not int
            or data["schema_version"] != 3):
        raise ValueError("M4 scene requires schema_version 3")
    name = data.get("id")
    if not isinstance(name, str) or not name:
        raise ValueError("scene id is required")
    canvas = _pair(data.get("canvas"), "canvas")
    width, height = canvas
    if not (1 <= width <= 256 and 1 <= height <= 128):
        raise ValueError("canvas must be within 256x128")
    ground_y, home_x, inset, seed = (data.get(key) for key in ("ground_y", "home_x", "inset", "seed"))
    if any(type(x) is not int for x in (ground_y, home_x, inset, seed)):
        raise ValueError("scene anchors, inset and seed must be integers")
    if not (0 <= ground_y < height and 0 <= home_x < width and 0 <= inset <= 128 and 0 <= seed <= 2**31 - 1):
        raise ValueError("scene anchors, inset or seed out of range")
    slot_ms = _positive_int(data.get("slot_ms"), "slot_ms", 120_000)
    if any(key in data for key in ("mode", "quiet_ms", "sleep_ms")):
        raise ValueError("cursor activity settings are unsupported")
    definitions = data.get("layers")
    if not isinstance(definitions, list) or not 1 <= len(definitions) <= 12:
        raise ValueError("layers must contain 1..12 entries")
    layers: list[Layer] = []
    names: set[str] = set()
    interactive_index = -1
    palette: list[tuple[int, int, int]] = []
    pixels: list[int] = []
    for item in definitions:
        if not isinstance(item, dict):
            raise ValueError("invalid layer")
        layer_name = item.get("id")
        if not isinstance(layer_name, str) or not layer_name or layer_name in names:
            raise ValueError("layer id must be unique")
        names.add(layer_name)
        filename = item.get("file")
        if not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith(".png"):
            raise ValueError(f"{layer_name}: file must be a local PNG filename")
        file = path.parent / filename
        frame_width, frame_height = _pair(item.get("frame_size"), f"{layer_name} frame_size")
        if not (1 <= frame_width <= 128 and 1 <= frame_height <= 64):
            raise ValueError(f"{layer_name}: frame_size out of bounds")
        durations = item.get("durations_ms")
        if not isinstance(durations, list) or not 1 <= len(durations) <= 8:
            raise ValueError(f"{layer_name}: 1..8 durations required")
        durations = tuple(_positive_int(x, f"{layer_name} duration", 60_000) for x in durations)
        motion = item.get("motion")
        if motion not in ("static", "loop", "path", "interactive"):
            raise ValueError(f"{layer_name}: unknown motion")
        if motion == "static" and len(durations) != 1:
            raise ValueError(f"{layer_name}: static layer must have one frame")
        if motion in ("loop", "path") and len(durations) < 2:
            raise ValueError(f"{layer_name}: animated layer needs multiple frames")
        if motion == "interactive":
            if interactive_index >= 0:
                raise ValueError("scene schema 3 allows one interactive layer")
            interactive_index = len(layers)
        if motion == "path":
            start = _position(item.get("from"), frame_width, frame_height, canvas, f"{layer_name} from")
            end = _position(item.get("to"), frame_width, frame_height, canvas, f"{layer_name} to")
            period_ms = _positive_int(item.get("period_ms"), f"{layer_name} period_ms", 3_600_000)
            active_ms = _positive_int(item.get("active_ms"), f"{layer_name} active_ms", period_ms)
            if active_ms >= period_ms:
                raise ValueError(f"{layer_name}: active_ms must be less than period_ms")
            phase_ms = item.get("phase_ms", 0)
            if type(phase_ms) is not int or not 0 <= phase_ms < period_ms:
                raise ValueError(f"{layer_name}: phase_ms out of range")
        else:
            start = _position(item.get("position"), frame_width, frame_height, canvas, f"{layer_name} position")
            end = start
            period_ms = active_ms = phase_ms = 0
        with Image.open(file) as image:
            if image.format != "PNG" or image.mode != "RGBA":
                raise ValueError(f"{layer_name}: source must be an RGBA PNG")
            if image.size != (frame_width * len(durations), frame_height):
                raise ValueError(f"{layer_name}: PNG geometry does not match metadata")
            rgba = image.load()
            for frame in range(len(durations)):
                for y in range(frame_height):
                    for x in range(frame_width):
                        red, green, blue, alpha = rgba[frame * frame_width + x, y]
                        if alpha not in (0, 255):
                            raise ValueError(f"{layer_name}: alpha must be binary")
                        if alpha == 0:
                            pixels.append(0)
                            continue
                        color = (red, green, blue)
                        if color not in palette:
                            if len(palette) >= 15:
                                raise ValueError("environment exceeds 15 opaque colors")
                            palette.append(color)
                        pixels.append(palette.index(color) + 1)
        if len(pixels) > 16_384:
            raise ValueError("environment sprite data exceeds 16384 pixels")
        layers.append(Layer(layer_name, file, frame_width, frame_height, durations, motion,
                            start, end, period_ms, active_ms, phase_ms))
    clips = {clip.name for clip in pet.clips}
    if not {"idle", "sleep", "wake"} <= clips:
        raise ValueError("idle, sleep and wake clips are required")
    episodes_data = data.get("episodes")
    if not isinstance(episodes_data, list) or not 1 <= len(episodes_data) <= 32:
        raise ValueError("episodes must contain 1..32 entries")
    episodes: list[Episode4] = []
    episode_names: set[str] = set()
    for item in episodes_data:
        if not isinstance(item, dict):
            raise ValueError("invalid episode")
        episode_name = item.get("id")
        if not isinstance(episode_name, str) or not episode_name or episode_name in episode_names:
            raise ValueError("episode id must be unique")
        episode_names.add(episode_name)
        if "mode" in item:
            raise ValueError("cursor activity modes are unsupported")
        weight = _positive_int(item.get("weight"), "episode weight", 100)
        phase_data = item.get("phases")
        if not isinstance(phase_data, list) or not 1 <= len(phase_data) <= 16:
            raise ValueError(f"{episode_name}: 1..16 phases required")
        phases: list[Phase4] = []
        total = previous_pet = previous_object = 0
        for phase_item in phase_data:
            if not isinstance(phase_item, dict):
                raise ValueError("invalid phase")
            clip, face = phase_item.get("clip"), phase_item.get("face")
            if clip not in clips or face not in ("left", "right"):
                raise ValueError(f"{episode_name}: invalid clip or face")
            duration = _positive_int(phase_item.get("duration_ms"), "phase duration", slot_ms)
            from_x, to_x = phase_item.get("from_x"), phase_item.get("to_x")
            object_from = phase_item.get("object_from_x", 0)
            object_to = phase_item.get("object_to_x", 0)
            if (any(type(x) is not int for x in (from_x, to_x, object_from, object_to))
                    or from_x != previous_pet or object_from != previous_object):
                raise ValueError(f"{episode_name}: discontinuous pet/object position")
            if interactive_index < 0 and (object_from or object_to):
                raise ValueError("object motion requires an interactive layer")
            for x in (from_x, to_x):
                left = home_x + x - pet.anchor_x
                bottom = ground_y - (pet.frame_height - 1 - pet.anchor_y)
                if not (0 <= left and left + pet.frame_width <= width and 0 <= bottom and bottom + pet.frame_height <= height):
                    raise ValueError(f"{episode_name}: pet leaves scene canvas")
            if interactive_index >= 0:
                layer = layers[interactive_index]
                for x in (object_from, object_to):
                    if not 0 <= layer.start[0] + x <= width - layer.width:
                        raise ValueError(f"{episode_name}: interactive object leaves scene canvas")
            phases.append(Phase4(clip, duration, from_x, to_x, face, object_from, object_to))
            previous_pet, previous_object = to_x, object_to
            total += duration
        if previous_pet != 0 or previous_object != 0 or total > slot_ms:
            raise ValueError(f"{episode_name}: pet and object must return home within slot")
        episodes.append(Episode4(episode_name, weight, tuple(phases)))
    return Scene4(name, width, height, ground_y, home_x, inset, seed, slot_ms,
                  tuple(layers), interactive_index, tuple(palette), tuple(pixels), tuple(episodes))


def select_episode(scene: Scene4, slot: int) -> Episode4:
    choice = _hash_slot(slot, scene.seed) % sum(e.weight for e in scene.episodes)
    for episode in scene.episodes:
        if choice < episode.weight:
            return episode
        choice -= episode.weight
    raise AssertionError("unreachable episode selection")


def layer_state(layer: Layer, time_s: float, focused: bool, object_x: float = 0.0) -> LayerState:
    x, y = layer.start
    frame_ms = 0.0
    if layer.motion == "loop":
        frame_ms = time_s * 1000 if focused else 0.0
    elif layer.motion == "path":
        if not focused:
            return LayerState(False, x, y, 0)
        cycle = (time_s * 1000 + layer.phase_ms) % layer.period_ms
        if cycle >= layer.active_ms:
            return LayerState(False, x, y, 0)
        t = cycle / layer.active_ms
        eased = t * t * (3 - 2 * t)
        x = x + (layer.end[0] - x) * eased
        y = y + (layer.end[1] - y) * eased
        frame_ms = cycle
    elif layer.motion == "interactive":
        x += object_x
        frame_ms = abs(object_x) * 160
    t = int(max(0.0, frame_ms)) % sum(layer.durations_ms)
    for frame, duration in enumerate(layer.durations_ms):
        if t < duration:
            return LayerState(True, x, y, frame)
        t -= duration
    raise AssertionError("unreachable layer frame")


def evaluate(scene: Scene4, pet: Pet, time_s: float, focus_s: float, focused: bool) -> Pose4:
    clips = {clip.name: clip for clip in pet.clips}
    if not focused:
        return Pose4("sleeping", "sleep", "sleep", select_frame(clips["sleep"], time_s * 1000), 0, "right", 0, 1)
    focus_age_ms = max(0.0, (time_s - focus_s) * 1000)
    fade = 1.0 if focus_s <= 0 else min(1.0, focus_age_ms / 650.0)
    if focus_s > 0 and focus_age_ms < 650:
        return Pose4("active", "wake", "wake", select_frame(clips["wake"], focus_age_ms), 0, "right", 0, fade)
    absolute_ms = max(0.0, time_s * 1000)
    slot = int(absolute_ms // scene.slot_ms)
    local_ms = absolute_ms - slot * scene.slot_ms
    if slot * scene.slot_ms < focus_s * 1000:
        return Pose4("active", "refocus-rest", "idle", select_frame(clips["idle"], local_ms), 0, "right", 0, fade)
    episode = select_episode(scene, slot)
    for phase in episode.phases:
        if local_ms < phase.duration_ms:
            t = local_ms / phase.duration_ms
            eased = t * t * (3 - 2 * t)
            x = phase.from_x + (phase.to_x - phase.from_x) * eased
            object_x = phase.object_from_x + (phase.object_to_x - phase.object_from_x) * eased
            return Pose4("active", episode.name, phase.clip, select_frame(clips[phase.clip], local_ms),
                         x, phase.face, object_x, fade)
        local_ms -= phase.duration_ms
    return Pose4("active", episode.name, "idle", select_frame(clips["idle"], local_ms), 0, "right", 0, fade)
