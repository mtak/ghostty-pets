// Ghostty Pets M2 visibility proof
// Generator: m2.1; visibility policy: cursor-only; source SHA-256: ee35922e7dfd568522b7f36950d38aef8edfda8b9335a2da26b8b48c9ed4becb
// Source: assets/pets/corgi/m1-silhouette.png; scale: 1x
const int SPRITE_WIDTH = 32;
const int SPRITE_HEIGHT = 24;
const int SPRITE_SCALE = 1;
const int SPRITE_INSET = 12;
const uint SPRITE_DATA[96] = uint[96](
    0x00000000u,
    0x00000000u,
    0x00000000u,
    0x00000000u,
    0x00000000u,
    0x00000000u,
    0x00100000u,
    0x00000100u,
    0x00000000u,
    0x00000000u,
    0x01100000u,
    0x00000100u,
    0x00000000u,
    0x00000000u,
    0x02100000u,
    0x00001210u,
    0x00000000u,
    0x00000000u,
    0x12100000u,
    0x00001210u,
    0x00000000u,
    0x00000000u,
    0x22110000u,
    0x00012221u,
    0x00011110u,
    0x00000000u,
    0x22210000u,
    0x00012221u,
    0x00111110u,
    0x00000000u,
    0x22210000u,
    0x00122222u,
    0x00111100u,
    0x00000000u,
    0x32210000u,
    0x00132222u,
    0x01111000u,
    0x00000000u,
    0x12210000u,
    0x00112222u,
    0x11110000u,
    0x11111111u,
    0x22211111u,
    0x00122222u,
    0x41100000u,
    0x44444444u,
    0x55221444u,
    0x00222555u,
    0x41000000u,
    0x44444444u,
    0x55221444u,
    0x01222555u,
    0x41000000u,
    0x44444444u,
    0x55221444u,
    0x01555555u,
    0x41000000u,
    0x44444444u,
    0x55214444u,
    0x01555555u,
    0x41000000u,
    0x22222222u,
    0x55212222u,
    0x01555555u,
    0x41000000u,
    0x22222222u,
    0x55122222u,
    0x00112555u,
    0x41000000u,
    0x22222222u,
    0x11122222u,
    0x00011211u,
    0x11000000u,
    0x11111122u,
    0x11155111u,
    0x00001001u,
    0x10000000u,
    0x00000122u,
    0x00155100u,
    0x00000000u,
    0x10000000u,
    0x00000122u,
    0x00155100u,
    0x00000000u,
    0x10000000u,
    0x00000122u,
    0x00155100u,
    0x00000000u,
    0x10000000u,
    0x00000111u,
    0x00111100u,
    0x00000000u,
    0x00000000u,
    0x00000000u,
    0x00000000u,
    0x00000000u
);
const vec3 SPRITE_PALETTE[16] = vec3[16](
    vec3(0.0),
    vec3(38.0, 32.0, 39.0) / 255.0,
    vec3(213.0, 139.0, 70.0) / 255.0,
    vec3(255.0, 255.0, 255.0) / 255.0,
    vec3(57.0, 48.0, 49.0) / 255.0,
    vec3(250.0, 238.0, 211.0) / 255.0,
    vec3(0.0),
    vec3(0.0),
    vec3(0.0),
    vec3(0.0),
    vec3(0.0),
    vec3(0.0),
    vec3(0.0),
    vec3(0.0),
    vec3(0.0),
    vec3(0.0)
);


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

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Pixel centers avoid interpolation between terminal texels.
    vec2 uv = (floor(fragCoord) + vec2(0.5)) / iResolution.xy;
    vec4 terminal = texture(iChannel0, uv);
    ivec2 sizePx = ivec2(SPRITE_WIDTH, SPRITE_HEIGHT) * SPRITE_SCALE;
    // Ghostty fragment Y increases upward from the bottom of the surface.
    ivec2 origin = ivec2(int(iResolution.x) - SPRITE_INSET - sizePx.x, SPRITE_INSET);
    ivec2 screenPx = ivec2(floor(fragCoord));
    if (origin.x < 0 || origin.y < 0 ||
        screenPx.x < origin.x || screenPx.y < origin.y ||
        screenPx.x >= origin.x + sizePx.x || screenPx.y >= origin.y + sizePx.y) {
        fragColor = terminal;
        return;
    }

    ivec2 sourcePx = (screenPx - origin) / SPRITE_SCALE;
    // PNG rows run top-down, opposite to fragment Y.
    int linear = (SPRITE_HEIGHT - 1 - sourcePx.y) * SPRITE_WIDTH + sourcePx.x;
    uint word = SPRITE_DATA[linear / 8];
    uint index = (word >> uint(4 * (linear % 8))) & 15u;
    if (index == 0u) {
        fragColor = terminal;
        return;
    }
    vec4 region = m2RegionBounds(sourcePx.x, origin);
    float cursorFade = m2CursorFade(region);
    float textFade = 0.0;
    float opacity = 1.0 - 0.92 * max(cursorFade, textFade);
    fragColor = mix(terminal, vec4(SPRITE_PALETTE[int(index)], terminal.a), opacity);
}
