"""Compile the M4 corgi and layered backyard into standalone Ghostty GLSL."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

if __package__:
    from .build_m3 import _array, _pack
    from .m3_model import Pet, load_pet
    from .m4_model import Scene4, load_scene
else:
    from build_m3 import _array, _pack
    from m3_model import Pet, load_pet
    from m4_model import Scene4, load_scene


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PET = ROOT / "assets/pets/corgi/corgi-v1.json"
DEFAULT_SCENE = ROOT / "assets/environments/backyard/backyard-v1.json"


def _palette(colors: tuple[tuple[int, int, int], ...]) -> list[str]:
    result = ["vec3(0.0)"] + [f"vec3({r}.0, {g}.0, {b}.0) / 255.0" for r, g, b in colors]
    return result + ["vec3(0.0)"] * (16 - len(result))


def _definitions(pet: Pet, scene: Scene4, scale: int) -> str:
    clip_ids = {clip.name: i for i, clip in enumerate(pet.clips)}
    clip_starts: list[int] = []
    clip_counts: list[int] = []
    pet_durations: list[int] = []
    pet_loops: list[int] = []
    pet_speeds: list[float] = []
    pet_frame_starts: list[int] = []
    unique_pet_pixels: list[int] = []
    pet_frame_locations: dict[tuple[int, ...], int] = {}
    source_cursor = 0
    frame_area = pet.frame_width * pet.frame_height
    for clip in pet.clips:
        clip_starts.append(len(pet_durations))
        clip_counts.append(len(clip.durations_ms))
        pet_durations.extend(clip.durations_ms)
        pet_loops.append(int(clip.loop))
        pet_speeds.append(clip.speed)
        for _ in clip.durations_ms:
            block = pet.pixels[source_cursor:source_cursor + frame_area]
            source_cursor += frame_area
            if block not in pet_frame_locations:
                pet_frame_locations[block] = len(unique_pet_pixels)
                unique_pet_pixels.extend(block)
            pet_frame_starts.append(pet_frame_locations[block])

    episode_starts: list[int] = []
    episode_counts: list[int] = []
    phase_durations: list[int] = []
    phase_clips: list[int] = []
    phase_from: list[int] = []
    phase_to: list[int] = []
    phase_flip: list[int] = []
    phase_object_from: list[int] = []
    phase_object_to: list[int] = []
    cumulative: list[int] = []
    weight = 0
    for episode in scene.episodes:
        episode_starts.append(len(phase_durations))
        episode_counts.append(len(episode.phases))
        weight += episode.weight
        cumulative.append(weight)
        for phase in episode.phases:
            phase_durations.append(phase.duration_ms)
            phase_clips.append(clip_ids[phase.clip])
            phase_from.append(phase.from_x)
            phase_to.append(phase.to_x)
            phase_flip.append(int(phase.face == "left"))
            phase_object_from.append(phase.object_from_x)
            phase_object_to.append(phase.object_to_x)

    layer_widths: list[int] = []
    layer_heights: list[int] = []
    layer_motion: list[int] = []
    layer_x0: list[int] = []
    layer_y0: list[int] = []
    layer_x1: list[int] = []
    layer_y1: list[int] = []
    layer_period: list[int] = []
    layer_active: list[int] = []
    layer_phase: list[int] = []
    layer_frame_first: list[int] = []
    layer_frame_count: list[int] = []
    env_durations: list[int] = []
    env_frame_starts: list[int] = []
    pixel_start = 0
    motion_ids = {"static": 0, "loop": 1, "path": 2, "interactive": 3}
    for layer in scene.layers:
        layer_widths.append(layer.width)
        layer_heights.append(layer.height)
        layer_motion.append(motion_ids[layer.motion])
        layer_x0.append(layer.start[0])
        layer_y0.append(layer.start[1])
        layer_x1.append(layer.end[0])
        layer_y1.append(layer.end[1])
        layer_period.append(layer.period_ms)
        layer_active.append(layer.active_ms)
        layer_phase.append(layer.phase_ms)
        layer_frame_first.append(len(env_durations))
        layer_frame_count.append(len(layer.durations_ms))
        env_durations.extend(layer.durations_ms)
        for _ in layer.durations_ms:
            env_frame_starts.append(pixel_start)
            pixel_start += layer.width * layer.height

    entries = [
        f"const int M4_PET_WIDTH = {pet.frame_width};",
        f"const int M4_PET_HEIGHT = {pet.frame_height};",
        f"const int M4_PET_ANCHOR_X = {pet.anchor_x};",
        f"const int M4_PET_ANCHOR_Y = {pet.anchor_y};",
        f"const int M4_SCENE_WIDTH = {scene.width};",
        f"const int M4_SCENE_HEIGHT = {scene.height};",
        f"const int M4_GROUND_Y = {scene.ground_y};",
        f"const int M4_HOME_X = {scene.home_x};",
        f"const int M4_INSET = {scene.inset};",
        f"const int M4_SCALE = {scale};",
        f"const int M4_SLOT_MS = {scene.slot_ms};",
        f"const uint M4_SEED = {scene.seed}u;",
        f"const int M4_IDLE = {clip_ids['idle']};",
        f"const int M4_SLEEP = {clip_ids['sleep']};",
        f"const int M4_WAKE = {clip_ids['wake']};",
        f"const int M4_LAYER_COUNT = {len(scene.layers)};",
        _array("int", "M4_CLIP_START", clip_starts),
        _array("int", "M4_CLIP_COUNT", clip_counts),
        _array("int", "M4_PET_FRAME_DURATION", pet_durations),
        _array("int", "M4_CLIP_LOOP", pet_loops),
        _array("float", "M4_CLIP_SPEED", pet_speeds),
        _array("int", "M4_PET_FRAME_START", pet_frame_starts),
        _array("int", "M4_EP_START", episode_starts),
        _array("int", "M4_EP_COUNT", episode_counts),
        _array("int", "M4_EP_CUM", cumulative),
        f"const int M4_EP_TOTAL = {weight};",
        _array("int", "M4_PHASE_DURATION", phase_durations),
        _array("int", "M4_PHASE_CLIP", phase_clips),
        _array("int", "M4_PHASE_FROM", phase_from),
        _array("int", "M4_PHASE_TO", phase_to),
        _array("int", "M4_PHASE_FLIP", phase_flip),
        _array("int", "M4_PHASE_OBJECT_FROM", phase_object_from),
        _array("int", "M4_PHASE_OBJECT_TO", phase_object_to),
        _array("int", "M4_LAYER_WIDTH", layer_widths),
        _array("int", "M4_LAYER_HEIGHT", layer_heights),
        _array("int", "M4_LAYER_MOTION", layer_motion),
        _array("int", "M4_LAYER_X0", layer_x0),
        _array("int", "M4_LAYER_Y0", layer_y0),
        _array("int", "M4_LAYER_X1", layer_x1),
        _array("int", "M4_LAYER_Y1", layer_y1),
        _array("int", "M4_LAYER_PERIOD", layer_period),
        _array("int", "M4_LAYER_ACTIVE", layer_active),
        _array("int", "M4_LAYER_PHASE", layer_phase),
        _array("int", "M4_LAYER_FRAME_FIRST", layer_frame_first),
        _array("int", "M4_LAYER_FRAME_COUNT", layer_frame_count),
        _array("int", "M4_ENV_FRAME_DURATION", env_durations),
        _array("int", "M4_ENV_FRAME_START", env_frame_starts),
        _array("uint", "M4_PET_DATA", _pack(tuple(unique_pet_pixels))),
        _array("uint", "M4_ENV_DATA", _pack(scene.pixels)),
        _array("vec3", "M4_PET_PALETTE", _palette(pet.palette)),
        _array("vec3", "M4_ENV_PALETTE", _palette(scene.palette)),
    ]
    return "\n".join(entries)


SHADER = r"""
uint m4Hash(uint x) {
    x ^= x >> 16u;
    x *= 0x7feb352du;
    x ^= x >> 15u;
    x *= 0x846ca68bu;
    return x ^ (x >> 16u);
}

int m4Episode(int slot) {
    int value = int(m4Hash(uint(slot) ^ M4_SEED) % uint(M4_EP_TOTAL));
    for (int i = 0; i < M4_EP_CUM.length(); i++) {
        if (value < M4_EP_CUM[i]) return i;
    }
    return 0;
}

int m4PetFrame(int clip, float elapsedMs) {
    int start = M4_CLIP_START[clip];
    int count = M4_CLIP_COUNT[clip];
    int total = 0;
    for (int i = 0; i < 8; i++) {
        if (i >= count) break;
        total += M4_PET_FRAME_DURATION[start + i];
    }
    float timeMs = floor(max(0.0, elapsedMs) * M4_CLIP_SPEED[clip]);
    int remaining = M4_CLIP_LOOP[clip] == 1
        ? int(mod(timeMs, float(total))) : int(min(timeMs, float(total - 1)));
    for (int i = 0; i < 8; i++) {
        if (i >= count || remaining < M4_PET_FRAME_DURATION[start + i]) return start + i;
        remaining -= M4_PET_FRAME_DURATION[start + i];
    }
    return start + count - 1;
}

void m4Pose(out int clip, out float clipMs, out float petX,
            out int flip, out float objectX, out float fade) {
    clip = M4_SLEEP;
    clipMs = iTime * 1000.0;
    petX = 0.0;
    flip = 0;
    objectX = 0.0;
    fade = 1.0;
    if (iFocus == 0) return;

    float focusAge = max(0.0, iTime - iTimeFocus);
    fade = iTimeFocus <= 0.0 ? 1.0 : clamp(focusAge / 0.65, 0.0, 1.0);
    if (iTimeFocus > 0.0 && focusAge < 0.65) {
        clip = M4_WAKE;
        clipMs = focusAge * 1000.0;
        return;
    }
    float absoluteMs = max(0.0, iTime * 1000.0);
    int slot = int(floor(absoluteMs / float(M4_SLOT_MS)));
    float slotStartMs = float(slot) * float(M4_SLOT_MS);
    float localMs = absoluteMs - slotStartMs;
    if (slotStartMs < iTimeFocus * 1000.0) {
        clip = M4_IDLE;
        clipMs = localMs;
        return;
    }
    int episode = m4Episode(slot);
    int start = M4_EP_START[episode];
    for (int i = 0; i < 16; i++) {
        if (i >= M4_EP_COUNT[episode]) break;
        int phase = start + i;
        float duration = float(M4_PHASE_DURATION[phase]);
        if (localMs < duration) {
            clip = M4_PHASE_CLIP[phase];
            clipMs = localMs;
            float t = clamp(localMs / duration, 0.0, 1.0);
            float ease = t * t * (3.0 - 2.0 * t);
            petX = mix(float(M4_PHASE_FROM[phase]), float(M4_PHASE_TO[phase]), ease);
            objectX = mix(float(M4_PHASE_OBJECT_FROM[phase]), float(M4_PHASE_OBJECT_TO[phase]), ease);
            flip = M4_PHASE_FLIP[phase];
            return;
        }
        localMs -= duration;
    }
    clip = M4_IDLE;
    clipMs = localMs;
}

int m4EnvFrame(int layer, float elapsedMs) {
    int start = M4_LAYER_FRAME_FIRST[layer];
    int count = M4_LAYER_FRAME_COUNT[layer];
    int total = 0;
    for (int i = 0; i < 8; i++) {
        if (i >= count) break;
        total += M4_ENV_FRAME_DURATION[start + i];
    }
    int remaining = int(mod(max(0.0, elapsedMs), float(total)));
    for (int i = 0; i < 8; i++) {
        if (i >= count || remaining < M4_ENV_FRAME_DURATION[start + i]) return start + i;
        remaining -= M4_ENV_FRAME_DURATION[start + i];
    }
    return start + count - 1;
}

void m4LayerState(int layer, float objectX, out vec2 position,
                  out float frameMs, out bool visible) {
    position = vec2(float(M4_LAYER_X0[layer]), float(M4_LAYER_Y0[layer]));
    frameMs = 0.0;
    visible = true;
    int motion = M4_LAYER_MOTION[layer];
    if (motion == 1) {
        frameMs = iFocus == 0 ? 0.0 : iTime * 1000.0;
    } else if (motion == 2) {
        if (iFocus == 0) { visible = false; return; }
        float cycle = mod(iTime * 1000.0 + float(M4_LAYER_PHASE[layer]),
                          float(M4_LAYER_PERIOD[layer]));
        if (cycle >= float(M4_LAYER_ACTIVE[layer])) { visible = false; return; }
        float t = cycle / float(M4_LAYER_ACTIVE[layer]);
        float ease = t * t * (3.0 - 2.0 * t);
        position = mix(position, vec2(float(M4_LAYER_X1[layer]), float(M4_LAYER_Y1[layer])), ease);
        frameMs = cycle;
    } else if (motion == 3) {
        position.x += objectX;
        frameMs = abs(objectX) * 160.0;
    }
}

vec3 m4ToLinear(vec3 color) {
    vec3 low = color / 12.92;
    vec3 high = pow((color + 0.055) / 1.055, vec3(2.4));
    return mix(low, high, step(vec3(0.04045), color));
}

float m4CursorInfluence(vec4 cursor, vec4 region) {
    if (cursor.z <= 0.0 || cursor.w <= 0.0) return 0.0;
    vec4 bounds = vec4(cursor.x, cursor.y - cursor.w, cursor.x + cursor.z, cursor.y);
    vec2 gap = max(max(bounds.xy - region.zw, region.xy - bounds.zw), vec2(0.0));
    return 1.0 - smoothstep(0.0, 12.0, length(gap));
}

float m4CursorFade(vec4 region) {
    float current = m4CursorInfluence(iCurrentCursor, region);
    float age = max(0.0, iTime - iTimeCursorChange);
    float restoring = m4CursorInfluence(iPreviousCursor, region)
                    * (1.0 - smoothstep(0.0, 0.80, age));
    return max(current, restoring);
}

float m4TextFade(vec4 region) {
    vec3 background = m4ToLinear(iBackgroundColor);
    for (int row = 0; row < 5; row++) {
        float rowFraction = row == 0 ? 0.04 : (row == 4 ? 0.96 : float(row) * 0.25);
        for (int col = 0; col < 4; col++) {
            vec2 pixel = mix(region.xy, region.zw,
                             vec2((float(col) + 0.5) / 4.0, rowFraction));
            vec3 screen = texture(iChannel0, (floor(pixel) + vec2(0.5)) / iResolution.xy).rgb;
            if (length(screen - background) > 0.02) return 1.0;
        }
    }
    return 0.0;
}

float m4Opacity(vec4 region, float fade) {
    float cursorFade = m4CursorFade(region);
    float textFade = cursorFade < 0.95 ? m4TextFade(region) : 0.0;
    return fade * (1.0 - 0.92 * max(cursorFade, textFade));
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (floor(fragCoord) + vec2(0.5)) / iResolution.xy;
    vec4 terminal = texture(iChannel0, uv);
    fragColor = terminal;
    ivec2 sceneOrigin = ivec2(int(iResolution.x) - M4_INSET - M4_SCENE_WIDTH * M4_SCALE, M4_INSET);
    if (sceneOrigin.x < 0 || sceneOrigin.y + M4_SCENE_HEIGHT * M4_SCALE > int(iResolution.y)) return;
    ivec2 screenPx = ivec2(floor(fragCoord));
    if (screenPx.x < sceneOrigin.x || screenPx.y < sceneOrigin.y ||
        screenPx.x >= sceneOrigin.x + M4_SCENE_WIDTH * M4_SCALE ||
        screenPx.y >= sceneOrigin.y + M4_SCENE_HEIGHT * M4_SCALE) return;

    int clip, flip;
    float clipMs, petX, objectX, petFade;
    m4Pose(clip, clipMs, petX, flip, objectX, petFade);

    // Ordered, transparent environment layers. Each uses its own visibility region.
    for (int layer = 0; layer < M4_LAYER_COUNT; layer++) {
        vec2 position;
        float frameMs;
        bool visible;
        m4LayerState(layer, objectX, position, frameMs, visible);
        if (!visible) continue;
        ivec2 origin = sceneOrigin + ivec2(round(position)) * M4_SCALE;
        ivec2 local = screenPx - origin;
        if (local.x < 0 || local.y < 0 ||
            local.x >= M4_LAYER_WIDTH[layer] * M4_SCALE ||
            local.y >= M4_LAYER_HEIGHT[layer] * M4_SCALE) continue;
        ivec2 pixel = local / M4_SCALE;
        int frame = m4EnvFrame(layer, frameMs);
        int linear = M4_ENV_FRAME_START[frame] +
                     (M4_LAYER_HEIGHT[layer] - 1 - pixel.y) * M4_LAYER_WIDTH[layer] + pixel.x;
        uint word = M4_ENV_DATA[linear / 8];
        uint index = (word >> uint(4 * (linear % 8))) & 15u;
        if (index == 0u) continue;
        vec4 region = vec4(float(origin.x), float(origin.y),
                           float(origin.x + M4_LAYER_WIDTH[layer] * M4_SCALE),
                           float(origin.y + M4_LAYER_HEIGHT[layer] * M4_SCALE));
        float opacity = m4Opacity(region, 1.0);
        fragColor = mix(fragColor, vec4(M4_ENV_PALETTE[int(index)], terminal.a), opacity);
    }

    int frame = m4PetFrame(clip, clipMs);
    int petOriginX = M4_HOME_X + int(round(petX)) - M4_PET_ANCHOR_X;
    int petOriginY = M4_GROUND_Y - (M4_PET_HEIGHT - 1 - M4_PET_ANCHOR_Y);
    ivec2 petOrigin = sceneOrigin + ivec2(petOriginX, petOriginY) * M4_SCALE;
    ivec2 petLocal = screenPx - petOrigin;
    if (petLocal.x < 0 || petLocal.y < 0 ||
        petLocal.x >= M4_PET_WIDTH * M4_SCALE || petLocal.y >= M4_PET_HEIGHT * M4_SCALE) return;
    ivec2 petPixel = petLocal / M4_SCALE;
    int sourceX = flip == 1 ? M4_PET_WIDTH - 1 - petPixel.x : petPixel.x;
    int linear = M4_PET_FRAME_START[frame] +
                 (M4_PET_HEIGHT - 1 - petPixel.y) * M4_PET_WIDTH + sourceX;
    uint word = M4_PET_DATA[linear / 8];
    uint index = (word >> uint(4 * (linear % 8))) & 15u;
    if (index == 0u) return;
    int first = M4_PET_WIDTH / 3;
    int second = (M4_PET_WIDTH * 2) / 3;
    int left = petPixel.x < first ? 0 : (petPixel.x < second ? first : second);
    int right = petPixel.x < first ? first : (petPixel.x < second ? second : M4_PET_WIDTH);
    vec4 region = vec4(float(petOrigin.x + left * M4_SCALE), float(petOrigin.y),
                       float(petOrigin.x + right * M4_SCALE),
                       float(petOrigin.y + M4_PET_HEIGHT * M4_SCALE));
    float opacity = m4Opacity(region, petFade);
    fragColor = mix(fragColor, vec4(M4_PET_PALETTE[int(index)], terminal.a), opacity);
}
"""


def generate(pet_path: Path, scene_path: Path, scale: int = 2) -> str:
    if scale not in (1, 2, 3):
        raise ValueError("scale must be 1, 2 or 3")
    pet = load_pet(pet_path)
    scene = load_scene(scene_path, pet)
    fingerprint = hashlib.sha256(
        pet_path.read_bytes() + pet.sheet.read_bytes() + scene_path.read_bytes()
        + b"".join(layer.file.read_bytes() for layer in scene.layers)
    ).hexdigest()
    header = f"// Ghostty Pets M4 corgi/backyard proof\n// Source SHA-256: {fingerprint}; pet: {pet.name}; scene: {scene.name}; scale: {scale}x\n"
    shader = header + _definitions(pet, scene, scale) + "\n" + SHADER
    if len(shader.encode("utf-8")) > 128 * 1024:
        raise ValueError("generated shader exceeds 128 KiB M4 budget")
    return shader


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pet", type=Path, default=DEFAULT_PET)
    parser.add_argument("--scene", type=Path, default=DEFAULT_SCENE)
    parser.add_argument("--scale", type=int, choices=(1, 2, 3), default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    shader = generate(args.pet, args.scene, args.scale)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(shader, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
