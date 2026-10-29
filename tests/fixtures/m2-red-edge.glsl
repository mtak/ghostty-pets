// Diagnostic first shader for M2: a narrow red mark near the sprite's bottom edge.
// Chain this before the M2 shader in Ghostty to test edge sample coverage.
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (floor(fragCoord) + vec2(0.5)) / iResolution.xy;
    fragColor = texture(iChannel0, uv);
    float left = iResolution.x - 12.0 - 64.0 + 14.0;
    if (fragCoord.x >= left && fragCoord.x < left + 26.0 &&
        fragCoord.y >= 13.0 && fragCoord.y < 16.0)
        fragColor = vec4(0.8, 0.1, 0.2, 1.0);
}
