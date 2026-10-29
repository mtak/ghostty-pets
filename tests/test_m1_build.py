"""Small offline checks for the M1 sprite compiler."""

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.build_m1 import ROOT, SOURCE, generate, pack_nibbles, read_sprite


class M1BuildTests(unittest.TestCase):
    def test_generated_shader_is_reproducible(self) -> None:
        for scale in (1, 2):
            generated = generate(SOURCE, scale)
            artifact = ROOT / "dist" / f"m1-corgi-{scale}x.glsl"
            self.assertEqual(generated, artifact.read_text(encoding="utf-8"))
            self.assertIn(f"const int SPRITE_SCALE = {scale};", generated)

    def test_packing_round_trips_png_pixels(self) -> None:
        _, _, _, indices = read_sprite(SOURCE)
        words = pack_nibbles(indices)
        decoded = [(words[i // 8] >> (4 * (i % 8))) & 15 for i in range(len(indices))]
        self.assertEqual(decoded, indices)
        self.assertIn(0, indices)
        self.assertTrue(any(index > 0 for index in indices))

    def test_rejects_partial_alpha(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.png"
            Image.new("RGBA", (1, 1), (1, 2, 3, 128)).save(source)
            with self.assertRaisesRegex(ValueError, "alpha"):
                read_sprite(source)


if __name__ == "__main__":
    unittest.main()
