# README screenshot provenance

[`ghostty-pets-medium-linux.png`](ghostty-pets-medium-linux.png) is an actual capture of a dedicated Ghostty window, taken on 2026-10-30. It was not generated from the offline art preview.

- **Ghostty:** `1.3.0-dev+0000000`, Linux GTK/OpenGL build, launched with `GDK_BACKEND=x11` under a GNOME Wayland session.
- **Shader:** `dist/corgi-backyard-medium.glsl`, SHA-256 `4e7b148e0a3bdd5be4361b9253d70bfad33eb6795fddb879b57ef4f7aa28ed9d`.
- **Capture:** the isolated 760 × 430 Ghostty window was read through X11 `XGetImage` and saved directly as an RGB PNG. No image-generation or compositing step was applied. PNG SHA-256: `e0a899f0b46d3c56e89dbd37d53865a14c11bd7eb27a23a0b636766a0c5971b6`.
- **Content review:** the terminal text was scripted only for this screenshot (`Ghostty Pets`, `A little corgi in your terminal.`, and `echo hello, corgi`). It contains no user files, account names, hostnames, or private terminal output. The PNG has no embedded metadata fields.
- **Limit:** Mesa reported AMD EGL authorization failure and fallback. The screenshot proves this Ghostty window displayed the shader; it does not establish hardware GPU performance or macOS appearance.
