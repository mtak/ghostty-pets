// Ghostty Pets M3 animation proof
// Source SHA-256: 834e8a3b477485312d85164482e2acc528b71e5a71c30e56a8a2568689e6718d; pet: corgi-placeholder; scene: empty-stage; scale: 2x
const int M3_WIDTH = 16;
const int M3_HEIGHT = 12;
const int M3_ANCHOR_X = 8;
const int M3_ANCHOR_Y = 11;
const int M3_SCENE_WIDTH = 64;
const int M3_SCENE_HEIGHT = 24;
const int M3_GROUND_Y = 4;
const int M3_HOME_X = 32;
const int M3_INSET = 12;
const int M3_SCALE = 2;
const int M3_SLOT_MS = 12000;
const float M3_QUIET_S = 10.000000;
const float M3_SLEEP_S = 120.000000;
const uint M3_SEED = 5u;
const int M3_IDLE = 0;
const int M3_SLEEP = 8;
const int M3_WAKE = 9;
const int M3_CLIP_START[10] = int[10](0, 2, 5, 7, 9, 12, 15, 17, 19, 21);
const int M3_CLIP_COUNT[10] = int[10](2, 3, 2, 2, 3, 3, 2, 2, 2, 2);
const int M3_FRAME_DURATION[23] = int[23](600, 600, 450, 450, 600, 350, 450, 220, 250, 150, 150, 150, 190, 180, 210, 250, 220, 260, 340, 850, 1100, 280, 320);
const int M3_CLIP_LOOP[10] = int[10](1, 1, 0, 0, 1, 1, 0, 0, 1, 0);
const float M3_CLIP_SPEED[10] = float[10](1.000000, 1.000000, 1.000000, 1.000000, 1.000000, 1.150000, 1.000000, 1.000000, 0.800000, 1.000000);
const int M3_FRAME_START[23] = int[23](0, 192, 384, 576, 768, 960, 1152, 1344, 1536, 1728, 1920, 2112, 2304, 2496, 2688, 2880, 3072, 3264, 3456, 3648, 3840, 4032, 4224);
const int M3_EP_START[7] = int[7](0, 2, 4, 6, 9, 14, 19);
const int M3_EP_COUNT[7] = int[7](2, 2, 2, 3, 5, 5, 5);
const int M3_PHASE_DURATION[24] = int[24](4000, 800, 1600, 800, 3000, 700, 600, 1000, 600, 700, 2500, 500, 2500, 700, 700, 2500, 500, 2500, 700, 700, 1600, 1600, 1600, 700);
const int M3_PHASE_CLIP[24] = int[24](1, 2, 0, 2, 1, 2, 3, 7, 6, 3, 4, 2, 4, 6, 3, 4, 2, 4, 6, 3, 4, 5, 4, 6);
const int M3_PHASE_FROM[24] = int[24](0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -12, -12, 0, 0, 0, 12, 12, 0, 0, 0, 8, 8, 0);
const int M3_PHASE_TO[24] = int[24](0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -12, -12, 0, 0, 0, 12, 12, 0, 0, 0, 8, 8, 0, 0);
const int M3_PHASE_FLIP[24] = int[24](0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0);
const int M3_QUIET_EP[2] = int[2](0, 1);
const int M3_QUIET_CUM[2] = int[2](4, 5);
const int M3_QUIET_TOTAL = 5;
const int M3_ACTIVE_EP[5] = int[5](2, 3, 4, 5, 6);
const int M3_ACTIVE_CUM[5] = int[5](4, 6, 7, 8, 10);
const int M3_ACTIVE_TOTAL = 10;
const uint M3_DATA[552] = uint[552](0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x13331300u, 0x00003331u, 0x03330000u, 0x00003330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01111100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x13331300u, 0x00003331u, 0x03330000u, 0x00003330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x13331300u, 0x00003331u, 0x03330000u, 0x00003330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x11111300u, 0x01211111u, 0x11111330u, 0x04441111u, 0x44411330u, 0x34441114u, 0x44411300u, 0x01111114u, 0x44411300u, 0x00003114u, 0x13331300u, 0x00003331u, 0x03330000u, 0x00003330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x13331300u, 0x00003331u, 0x03330000u, 0x00003330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x13331300u, 0x00003331u, 0x03330000u, 0x00003330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x00000000u, 0x04441100u, 0x11111300u, 0x34441111u, 0x11111330u, 0x04441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x13331300u, 0x00003331u, 0x03330000u, 0x00003330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x11331300u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x11111300u, 0x01211111u, 0x11111330u, 0x04441111u, 0x44411330u, 0x34441114u, 0x44411300u, 0x01111114u, 0x44411300u, 0x00003114u, 0x11331300u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x11331300u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x11111300u, 0x01211111u, 0x11111330u, 0x04441111u, 0x44411330u, 0x34441114u, 0x44411300u, 0x01111114u, 0x44411300u, 0x00003114u, 0x13311300u, 0x00003133u, 0x03300000u, 0x00000033u, 0x03300000u, 0x00000033u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x11331300u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x05111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x11331300u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u, 0x00000000u, 0x01111000u, 0x00000000u, 0x05111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x04441114u, 0x44411300u, 0x01111114u, 0x44411300u, 0x00003114u, 0x11331300u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x05111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x11331300u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x11111300u, 0x01211111u, 0x11111330u, 0x04441111u, 0x44411330u, 0x34441114u, 0x44411300u, 0x01111114u, 0x44411300u, 0x00003114u, 0x13331300u, 0x00003331u, 0x03330000u, 0x00003330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x13331300u, 0x00003331u, 0x03330000u, 0x00003330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x00000000u, 0x04441100u, 0x11111300u, 0x34441111u, 0x11111330u, 0x01111111u, 0x44411330u, 0x00003114u, 0x11331300u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x04441114u, 0x44411300u, 0x01111114u, 0x44411300u, 0x00003114u, 0x11331300u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111100u, 0x11111300u, 0x01221111u, 0x11111330u, 0x01111111u, 0x33300330u, 0x00000333u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x11111300u, 0x01111111u, 0x11111330u, 0x01221111u, 0x11111330u, 0x01111111u, 0x33300000u, 0x00000333u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x30003111u, 0x11331330u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u, 0x00000000u, 0x00000000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111000u, 0x00000000u, 0x01111100u, 0x00000000u, 0x01211100u, 0x11111300u, 0x04441111u, 0x11111330u, 0x34441111u, 0x44411330u, 0x01111114u, 0x44411300u, 0x00003114u, 0x11331300u, 0x00003331u, 0x00330000u, 0x00000330u, 0x00330000u, 0x00000330u);
const vec3 M3_PALETTE[16] = vec3[16](vec3(0.0), vec3(218.0, 154.0, 91.0) / 255.0, vec3(21.0, 23.0, 29.0) / 255.0, vec3(42.0, 36.0, 42.0) / 255.0, vec3(250.0, 227.0, 184.0) / 255.0, vec3(229.0, 124.0, 119.0) / 255.0, vec3(0.0), vec3(0.0), vec3(0.0), vec3(0.0), vec3(0.0), vec3(0.0), vec3(0.0), vec3(0.0), vec3(0.0), vec3(0.0));

uint m3Hash(uint x) {
    x ^= x >> 16u;
    x *= 0x7feb352du;
    x ^= x >> 15u;
    x *= 0x846ca68bu;
    return x ^ (x >> 16u);
}

int m3Episode(int mode, int slot) {
    uint random = m3Hash(uint(slot) ^ M3_SEED);
    if (mode == 0) {
        int value = int(random % uint(M3_QUIET_TOTAL));
        for (int i = 0; i < M3_QUIET_EP.length(); i++) {
            if (value < M3_QUIET_CUM[i]) return M3_QUIET_EP[i];
        }
    } else {
        int value = int(random % uint(M3_ACTIVE_TOTAL));
        for (int i = 0; i < M3_ACTIVE_EP.length(); i++) {
            if (value < M3_ACTIVE_CUM[i]) return M3_ACTIVE_EP[i];
        }
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

    float eventTime = max(iTimeCursorChange, iTimeFocus);
    float age = max(0.0, iTime - eventTime);
    fade = clamp(min(age, min(abs(age - M3_QUIET_S), abs(age - M3_SLEEP_S))) / 0.65, 0.0, 1.0);
    int mode = age < M3_QUIET_S ? 0 : (age < M3_SLEEP_S ? 1 : 2);
    if (mode == 2) {
        clipMs = (age - M3_SLEEP_S) * 1000.0;
        return;
    }
    if (iTimeFocus >= iTimeCursorChange && iTime - iTimeFocus < 0.65) {
        clip = M3_WAKE;
        clipMs = (iTime - iTimeFocus) * 1000.0;
        return;
    }
    float modeMs = (age - (mode == 1 ? M3_QUIET_S : 0.0)) * 1000.0;
    int slot = int(floor(modeMs / float(M3_SLOT_MS)));
    float localMs = modeMs - float(slot * M3_SLOT_MS);
    int episode = m3Episode(mode, slot);
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
