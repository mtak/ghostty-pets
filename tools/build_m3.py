"""Compile M3 pet/scene PNG and JSON sources into standalone Ghostty GLSL."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

if __package__:
    from .m3_model import Pet, Scene, load_pet, load_scene
else:
    from m3_model import Pet, Scene, load_pet, load_scene


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PET = ROOT / "assets/pets/corgi/m3-pet.json"
DEFAULT_SCENE = ROOT / "assets/environments/m3-empty.json"


def _array(kind: str, name: str, values: list[int | float | str]) -> str:
    def literal(value: int | float | str) -> str:
        if isinstance(value, str):
            return value
        if kind == "uint":
            return f"{value}u"
        if kind == "float":
            return f"{float(value):.6f}"
        return str(value)
    return f"const {kind} {name}[{len(values)}] = {kind}[{len(values)}]({', '.join(map(literal, values))});"


def _pack(indices: tuple[int, ...]) -> list[str]:
    words = []
    for start in range(0, len(indices), 8):
        word = 0
        for shift, index in enumerate(indices[start : start + 8]):
            word |= index << (4 * shift)
        words.append(f"0x{word:08x}u")
    return words


def _definitions(pet: Pet, scene: Scene, scale: int) -> str:
    clip_ids = {clip.name: index for index, clip in enumerate(pet.clips)}
    frame_starts = []
    clip_starts = []
    clip_counts = []
    durations = []
    loops = []
    speeds = []
    pixel_cursor = 0
    for clip in pet.clips:
        clip_starts.append(len(durations))
        clip_counts.append(len(clip.durations_ms))
        durations.extend(clip.durations_ms)
        loops.append(int(clip.loop))
        speeds.append(clip.speed)
        for _ in clip.durations_ms:
            frame_starts.append(pixel_cursor)
            pixel_cursor += pet.frame_width * pet.frame_height
    episode_starts = []
    episode_counts = []
    phase_durations = []
    phase_clips = []
    phase_from = []
    phase_to = []
    phase_flip = []
    for episode in scene.episodes:
        episode_starts.append(len(phase_durations))
        episode_counts.append(len(episode.phases))
        for phase in episode.phases:
            phase_durations.append(phase.duration_ms)
            phase_clips.append(clip_ids[phase.clip])
            phase_from.append(phase.from_x)
            phase_to.append(phase.to_x)
            phase_flip.append(int(phase.face == "left"))
    sections = [
        f"const int M3_WIDTH = {pet.frame_width};",
        f"const int M3_HEIGHT = {pet.frame_height};",
        f"const int M3_ANCHOR_X = {pet.anchor_x};",
        f"const int M3_ANCHOR_Y = {pet.anchor_y};",
        f"const int M3_SCENE_WIDTH = {scene.width};",
        f"const int M3_SCENE_HEIGHT = {scene.height};",
        f"const int M3_GROUND_Y = {scene.ground_y};",
        f"const int M3_HOME_X = {scene.home_x};",
        f"const int M3_INSET = {scene.inset};",
        f"const int M3_SCALE = {scale};",
        f"const int M3_SLOT_MS = {scene.slot_ms};",
        f"const uint M3_SEED = {scene.seed}u;",
        f"const int M3_IDLE = {clip_ids['idle']};",
        f"const int M3_SLEEP = {clip_ids['sleep']};",
        f"const int M3_WAKE = {clip_ids['wake']};",
        _array("int", "M3_CLIP_START", clip_starts),
        _array("int", "M3_CLIP_COUNT", clip_counts),
        _array("int", "M3_FRAME_DURATION", durations),
        _array("int", "M3_CLIP_LOOP", loops),
        _array("float", "M3_CLIP_SPEED", speeds),
        _array("int", "M3_FRAME_START", frame_starts),
        _array("int", "M3_EP_START", episode_starts),
        _array("int", "M3_EP_COUNT", episode_counts),
        _array("int", "M3_PHASE_DURATION", phase_durations),
        _array("int", "M3_PHASE_CLIP", phase_clips),
        _array("int", "M3_PHASE_FROM", phase_from),
        _array("int", "M3_PHASE_TO", phase_to),
        _array("int", "M3_PHASE_FLIP", phase_flip),
    ]
    cumulative = []
    weight = 0
    for episode in scene.episodes:
        weight += episode.weight
        cumulative.append(weight)
    sections.append(_array("int", "M3_EP_CUM", cumulative))
    sections.append(f"const int M3_EP_TOTAL = {weight};")
    sections.append(_array("uint", "M3_DATA", _pack(pet.pixels)))
    colors = ["vec3(0.0)"] + [f"vec3({r}.0, {g}.0, {b}.0) / 255.0" for r, g, b in pet.palette]
    colors += ["vec3(0.0)"] * (16 - len(colors))
    sections.append(_array("vec3", "M3_PALETTE", colors))
    return "\n".join(sections)


SHADER = r"""
uint m3Hash(uint x) {
    x ^= x >> 16u;
    x *= 0x7feb352du;
    x ^= x >> 15u;
    x *= 0x846ca68bu;
    return x ^ (x >> 16u);
}

int m3Episode(int slot) {
    uint random = m3Hash(uint(slot) ^ M3_SEED);
    int value = int(random % uint(M3_EP_TOTAL));
    for (int i = 0; i < M3_EP_CUM.length(); i++) {
        if (value < M3_EP_CUM[i]) return i;
    }
    return 0;
}

int m3Frame(int clip, float elapsedMs) {
    int start = M3_CLIP_START[clip];
    int count = M3_CLIP_COUNT[clip];
    int total = 0;
    for (int i = 0; i < 8; i++) {
        if (i >= count) break;
        total += M3_FRAME_DURATION[start + i];
    }
    float timeMs = floor(max(0.0, elapsedMs) * M3_CLIP_SPEED[clip]);
    int remaining = M3_CLIP_LOOP[clip] == 1
        ? int(mod(timeMs, float(total)))
        : int(min(timeMs, float(total - 1)));
    for (int i = 0; i < 8; i++) {
        if (i >= count || remaining < M3_FRAME_DURATION[start + i]) return start + i;
        remaining -= M3_FRAME_DURATION[start + i];
    }
    return start + count - 1;
}

void m3Pose(out int clip, out float clipMs, out float x, out int flip, out float fade) {
    clip = M3_SLEEP;
    clipMs = iTime * 1000.0;
    x = 0.0;
    flip = 0;
    fade = 1.0;
    if (iFocus == 0) return;

    float focusAge = max(0.0, iTime - iTimeFocus);
    fade = iTimeFocus <= 0.0 ? 1.0 : clamp(focusAge / 0.65, 0.0, 1.0);
    if (iTimeFocus > 0.0 && focusAge < 0.65) {
        clip = M3_WAKE;
        clipMs = focusAge * 1000.0;
        return;
    }
    // Absolute episode slots are unaffected by terminal input.
    float absoluteMs = max(0.0, iTime * 1000.0);
    int slot = int(floor(absoluteMs / float(M3_SLOT_MS)));
    float slotStartMs = float(slot) * float(M3_SLOT_MS);
    float localMs = absoluteMs - slotStartMs;
    if (slotStartMs < iTimeFocus * 1000.0) {
        clip = M3_IDLE;
        clipMs = localMs;
        return;
    }
    int episode = m3Episode(slot);
    int start = M3_EP_START[episode];
    for (int i = 0; i < 16; i++) {
        if (i >= M3_EP_COUNT[episode]) break;
        int phase = start + i;
        float duration = float(M3_PHASE_DURATION[phase]);
        if (localMs < duration) {
            clip = M3_PHASE_CLIP[phase];
            clipMs = localMs;
            float t = clamp(localMs / duration, 0.0, 1.0);
            float ease = t * t * (3.0 - 2.0 * t);
            x = mix(float(M3_PHASE_FROM[phase]), float(M3_PHASE_TO[phase]), ease);
            flip = M3_PHASE_FLIP[phase];
            return;
        }
        localMs -= duration;
    }
    clip = M3_IDLE;
    clipMs = localMs;
}

vec3 m3ToLinear(vec3 color) {
    vec3 low = color / 12.92;
    vec3 high = pow((color + 0.055) / 1.055, vec3(2.4));
    return mix(low, high, step(vec3(0.04045), color));
}

vec4 m3Region(int sourceX, ivec2 origin) {
    int first = M3_WIDTH / 3;
    int second = (M3_WIDTH * 2) / 3;
    int left = sourceX < first ? 0 : (sourceX < second ? first : second);
    int right = sourceX < first ? first : (sourceX < second ? second : M3_WIDTH);
    return vec4(float(origin.x + left * M3_SCALE), float(origin.y),
                float(origin.x + right * M3_SCALE), float(origin.y + M3_HEIGHT * M3_SCALE));
}

float m3CursorInfluence(vec4 cursor, vec4 region) {
    if (cursor.z <= 0.0 || cursor.w <= 0.0) return 0.0;
    vec4 bounds = vec4(cursor.x, cursor.y - cursor.w, cursor.x + cursor.z, cursor.y);
    vec2 gap = max(max(bounds.xy - region.zw, region.xy - bounds.zw), vec2(0.0));
    return 1.0 - smoothstep(0.0, 12.0, length(gap));
}

float m3CursorFade(vec4 region) {
    float current = m3CursorInfluence(iCurrentCursor, region);
    float age = max(0.0, iTime - iTimeCursorChange);
    float restoring = m3CursorInfluence(iPreviousCursor, region)
                    * (1.0 - smoothstep(0.0, 0.80, age));
    return max(current, restoring);
}

float m3TextFade(vec4 region) {
    vec3 background = m3ToLinear(iBackgroundColor);
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

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (floor(fragCoord) + vec2(0.5)) / iResolution.xy;
    vec4 terminal = texture(iChannel0, uv);
    fragColor = terminal;

    ivec2 sceneOrigin = ivec2(int(iResolution.x) - M3_INSET - M3_SCENE_WIDTH * M3_SCALE, M3_INSET);
    if (sceneOrigin.x < 0 || sceneOrigin.y + M3_SCENE_HEIGHT * M3_SCALE > int(iResolution.y)) return;

    int clip;
    float clipMs, x, fade;
    int flip;
    m3Pose(clip, clipMs, x, flip, fade);
    int frame = m3Frame(clip, clipMs);
    int spriteX = M3_HOME_X + int(round(x)) - M3_ANCHOR_X;
    int spriteY = M3_GROUND_Y - (M3_HEIGHT - 1 - M3_ANCHOR_Y);
    ivec2 origin = sceneOrigin + ivec2(spriteX, spriteY) * M3_SCALE;
    ivec2 screenPx = ivec2(floor(fragCoord));
    ivec2 sourcePx = (screenPx - origin) / M3_SCALE;
    if (screenPx.x < origin.x || screenPx.y < origin.y ||
        sourcePx.x >= M3_WIDTH || sourcePx.y >= M3_HEIGHT) return;

    int sourceX = flip == 1 ? M3_WIDTH - 1 - sourcePx.x : sourcePx.x;
    int linear = M3_FRAME_START[frame] + (M3_HEIGHT - 1 - sourcePx.y) * M3_WIDTH + sourceX;
    uint word = M3_DATA[linear / 8];
    uint index = (word >> uint(4 * (linear % 8))) & 15u;
    if (index == 0u) return;

    vec4 region = m3Region(sourcePx.x, origin);
    float cursorFade = m3CursorFade(region);
    float textFade = cursorFade < 0.95 ? m3TextFade(region) : 0.0;
    float opacity = fade * (1.0 - 0.92 * max(cursorFade, textFade));
    fragColor = mix(terminal, vec4(M3_PALETTE[int(index)], terminal.a), opacity);
}
"""


def generate(pet_path: Path, scene_path: Path, scale: int = 2) -> str:
    if scale not in (1, 2, 3):
        raise ValueError("scale must be 1, 2 or 3")
    pet = load_pet(pet_path)
    scene = load_scene(scene_path, pet)
    fingerprint = hashlib.sha256(pet_path.read_bytes() + pet.sheet.read_bytes() + scene_path.read_bytes()).hexdigest()
    header = f"// Ghostty Pets M3 animation proof\n// Source SHA-256: {fingerprint}; pet: {pet.name}; scene: {scene.name}; scale: {scale}x\n"
    result = header + _definitions(pet, scene, scale) + "\n" + SHADER
    if len(result.encode("utf-8")) > 128 * 1024:
        raise ValueError("generated shader exceeds 128 KiB M3 budget")
    return result


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
