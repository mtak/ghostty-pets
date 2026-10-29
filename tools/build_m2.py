"""Build the M2 visibility proof without changing the M1 renderer."""

from __future__ import annotations

import argparse
from pathlib import Path

if __package__:
    from .build_m1 import SOURCE, generate as generate_m1
else:
    from build_m1 import SOURCE, generate as generate_m1


VISIBILITY_GLSL = """
// M2 visibility: three coherent source-art regions, at most 16 text probes each.
vec3 m2ToLinear(vec3 color) {
    vec3 low = color / 12.92;
    vec3 high = pow((color + 0.055) / 1.055, vec3(2.4));
    return mix(low, high, step(vec3(0.04045), color));
}

vec4 m2RegionBounds(int sourceX, ivec2 origin) {
    int left = sourceX < 7 ? 0 : (sourceX < 20 ? 7 : 20);
    int right = sourceX < 7 ? 7 : (sourceX < 20 ? 20 : SPRITE_WIDTH);
    return vec4(
        float(origin.x + left * SPRITE_SCALE), float(origin.y),
        float(origin.x + right * SPRITE_SCALE),
        float(origin.y + SPRITE_HEIGHT * SPRITE_SCALE)
    );
}

float m2CursorInfluence(vec4 cursor, vec4 region) {
    if (cursor.z <= 0.0 || cursor.w <= 0.0) return 0.0;
    // iCurrentCursor.xy is the left/top (-X,+Y) corner in Ghostty.
    vec4 bounds = vec4(cursor.x, cursor.y - cursor.w,
                       cursor.x + cursor.z, cursor.y);
    vec2 gap = max(max(bounds.xy - region.zw, region.xy - bounds.zw), vec2(0.0));
    return 1.0 - smoothstep(0.0, 12.0, length(gap));
}

float m2CursorFade(vec4 region) {
    float current = m2CursorInfluence(iCurrentCursor, region);
    float age = max(0.0, iTime - iTimeCursorChange);
    float restoring = m2CursorInfluence(iPreviousCursor, region)
                    * (1.0 - smoothstep(0.0, 0.80, age));
    return max(current, restoring);
}
"""


TEXT_GLSL = """
float m2TextFade(vec4 region) {
    vec3 background = m2ToLinear(iBackgroundColor);
    int occupied = 0;
    for (int row = 0; row < 4; row++) {
        for (int col = 0; col < 4; col++) {
            vec2 pixel = mix(region.xy, region.zw,
                             (vec2(float(col), float(row)) + vec2(0.5)) / 4.0);
            vec3 screen = texture(iChannel0, (floor(pixel) + vec2(0.5)) / iResolution.xy).rgb;
            occupied += length(screen - background) > 0.02 ? 1 : 0;
        }
    }
    // One hit is enough to protect a whole small art region. False positives
    // favor readability; the cursor-only build exposes the heuristic's effect.
    return occupied > 0 ? 1.0 : 0.0;
}
"""


OLD_OUTPUT = """    fragColor = index == 0u
        ? terminal
        : vec4(SPRITE_PALETTE[int(index)], terminal.a);"""

NEW_OUTPUT = """    if (index == 0u) {
        fragColor = terminal;
        return;
    }
    vec4 region = m2RegionBounds(sourcePx.x, origin);
    float cursorFade = m2CursorFade(region);
    float textFade = __TEXT_EXPRESSION__;
    float opacity = 1.0 - 0.92 * max(cursorFade, textFade);
    fragColor = mix(terminal, vec4(SPRITE_PALETTE[int(index)], terminal.a), opacity);"""


def generate(scale: int, policy: str) -> str:
    if policy not in ("conservative", "cursor-only"):
        raise ValueError("unknown M2 visibility policy")
    base = generate_m1(SOURCE, scale)
    if base.count(OLD_OUTPUT) != 1 or base.count("void mainImage") != 1:
        raise ValueError("M1 shader structure changed; review M2 integration")
    base = base.replace("// Ghostty Pets M1 static sprite proof", "// Ghostty Pets M2 visibility proof", 1)
    base = base.replace("// Generator: m1.1;", f"// Generator: m2.1; visibility policy: {policy};", 1)
    helpers = VISIBILITY_GLSL + (TEXT_GLSL if policy == "conservative" else "")
    base = base.replace("void mainImage", f"{helpers}\nvoid mainImage", 1)
    expression = "cursorFade < 0.95 ? m2TextFade(region) : 0.0" if policy == "conservative" else "0.0"
    output = NEW_OUTPUT.replace("__TEXT_EXPRESSION__", expression)
    return base.replace(OLD_OUTPUT, output, 1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", type=int, choices=(1, 2), required=True)
    parser.add_argument("--policy", choices=("conservative", "cursor-only"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    shader = generate(args.scale, args.policy)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(shader, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
