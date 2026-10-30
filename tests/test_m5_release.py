"""M5 release layout and standalone artifact checks."""

from __future__ import annotations

import tempfile
import unittest
import subprocess
import sys
from pathlib import Path

from tools.build_m4 import DEFAULT_PET, DEFAULT_SCENE, generate as generate_m4
from tools.build_m5 import PRESETS, generate
from tools.m3_model import load_pet
from tools.m4_model import load_scene
from tools.m5_layout import select_layout


ROOT = Path(__file__).resolve().parents[1]


class M5ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pet = load_pet(DEFAULT_PET)
        scene = load_scene(DEFAULT_SCENE, pet)
        cls.scene_size = (scene.width, scene.height)
        cls.pet_size = (pet.frame_width, pet.frame_height)
        cls.inset = scene.inset

    def layout(self, width: int, height: int, preset: int):
        return select_layout((width, height), preset, self.scene_size, self.pet_size, self.inset)

    def test_full_scene_fit_boundaries_and_preset_caps(self) -> None:
        # Exact fit requires the art plus the inset on all four sides.
        for preset, minimum, expected in (
            (1, (134, 69), ("full", 1)),
            (2, (244, 114), ("full", 2)),
            (3, (354, 159), ("full", 3)),
        ):
            layout = self.layout(*minimum, preset)
            self.assertEqual((layout.mode, layout.scale), expected)
            self.assertEqual(layout.origin, (self.inset, self.inset))
            self.assertEqual(layout.size, (110 * preset, 45 * preset))
        self.assertEqual(self.layout(243, 114, 2).scale, 1)
        self.assertEqual(self.layout(354, 158, 3).scale, 2)
        self.assertEqual(self.layout(1000, 1000, 1).scale, 1)
        self.assertEqual(self.layout(1000, 1000, 2).scale, 2)

    def test_pet_only_and_hidden_fit_boundaries(self) -> None:
        for preset, minimum, scale in (
            (1, (52, 48), 1),
            (2, (80, 72), 2),
            (3, (108, 96), 3),
        ):
            layout = self.layout(*minimum, preset)
            self.assertEqual((layout.mode, layout.scale), ("pet-only", scale))
            self.assertEqual(layout.origin, (self.inset, self.inset))
        self.assertEqual(self.layout(133, 69, 3).mode, "pet-only")
        self.assertIsNone(self.layout(51, 1000, 3))
        self.assertIsNone(self.layout(1000, 47, 3))
        self.assertIsNone(self.layout(0, 0, 1))

    def test_every_mode_stays_within_surface_and_preserves_margins(self) -> None:
        for width in range(0, 391, 13):
            for height in range(0, 201, 11):
                for preset in PRESETS.values():
                    layout = self.layout(width, height, preset)
                    if layout is None:
                        continue
                    x, y = layout.origin
                    art_width, art_height = layout.size
                    self.assertGreaterEqual(x, self.inset)
                    self.assertEqual(y, self.inset)
                    self.assertLessEqual(x + art_width + self.inset, width)
                    self.assertLessEqual(y + art_height + self.inset, height)
                    self.assertLessEqual(layout.scale, preset)

    def test_artifacts_are_reproducible_standalone_and_leave_m4_unchanged(self) -> None:
        for preset, max_scale in PRESETS.items():
            built = generate(DEFAULT_PET, DEFAULT_SCENE, max_scale)
            artifact = ROOT / "dist" / f"corgi-backyard-{preset}.glsl"
            self.assertEqual(artifact.read_text(encoding="utf-8"), built)
            self.assertLess(len(built.encode("utf-8")), 128 * 1024)
            self.assertTrue(built.startswith("// SPDX-License-Identifier: GPL-3.0-or-later\n"))
            self.assertEqual(built.count("void mainImage("), 1)
            self.assertNotIn("iFrame", built)
            self.assertIn("Source SHA-256:", built)
            self.assertIn(f"const int M4_SCALE = {max_scale};", built)
            self.assertIn("M4_UNFOCUSED : M4_IDLE", built)
        self.assertEqual(generate_m4(DEFAULT_PET, DEFAULT_SCENE, 2),
                         (ROOT / "dist/m4-corgi-backyard-2x.glsl").read_text())

    def test_build_is_independent_of_working_directory(self) -> None:
        # Exact source bytes must not contain checkout paths or timestamps.
        generated = generate(DEFAULT_PET, DEFAULT_SCENE, 2)
        self.assertNotIn(str(ROOT), generated)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "medium.glsl"
            output.write_text(generated, encoding="utf-8")
            self.assertEqual(output.read_bytes(),
                             (ROOT / "dist/corgi-backyard-medium.glsl").read_bytes())

    def test_cli_rejects_unsafe_output_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/build_m5.py"),
                 "--output-prefix", "../outside", "--output-dir", directory],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--output-prefix", result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
