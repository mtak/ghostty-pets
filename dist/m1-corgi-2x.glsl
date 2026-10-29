// Ghostty Pets M1 static sprite proof
// Generator: m1.1; source SHA-256: ee35922e7dfd568522b7f36950d38aef8edfda8b9335a2da26b8b48c9ed4becb
// Source: assets/pets/corgi/m1-silhouette.png; scale: 2x
const int SPRITE_WIDTH = 32;
const int SPRITE_HEIGHT = 24;
const int SPRITE_SCALE = 2;
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
    fragColor = index == 0u
        ? terminal
        : vec4(SPRITE_PALETTE[int(index)], terminal.a);
}
