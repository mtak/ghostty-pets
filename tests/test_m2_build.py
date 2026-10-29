"""M2 integration checks that leave the M1 artifacts intact."""

import unittest

from tools.build_m1 import ROOT, SOURCE, generate as generate_m1
from tools.build_m2 import generate


class M2BuildTests(unittest.TestCase):
    def test_m1_artifacts_are_unchanged(self) -> None:
        for scale in (1, 2):
            self.assertEqual(
                generate_m1(SOURCE, scale),
                (ROOT / "dist" / f"m1-corgi-{scale}x.glsl").read_text(encoding="utf-8"),
            )

    def test_policy_artifacts_are_reproducible(self) -> None:
        for scale in (1, 2):
            for policy in ("conservative", "cursor-only"):
                name = f"m2-corgi-{scale}x-{policy}.glsl"
                self.assertEqual(
                    generate(scale, policy),
                    (ROOT / "dist" / name).read_text(encoding="utf-8"),
                )

if __name__ == "__main__":
    unittest.main()
