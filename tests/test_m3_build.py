"""M3 metadata, timeline, and generated shader regression checks."""

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.build_m1 import ROOT, SOURCE, generate as generate_m1
from tools.build_m2 import generate as generate_m2
from tools.build_m3 import DEFAULT_PET, DEFAULT_SCENE, generate
from tools.m3_model import evaluate, load_pet, load_scene, select_episode, select_frame


class M3BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pet = load_pet(DEFAULT_PET)
        cls.scene = load_scene(DEFAULT_SCENE, cls.pet)

    def test_source_build_is_deterministic_and_standalone(self) -> None:
        built = generate(DEFAULT_PET, DEFAULT_SCENE, 2)
        self.assertEqual(built, generate(DEFAULT_PET, DEFAULT_SCENE, 2))
        self.assertEqual(built, (ROOT / "dist/m3-placeholder-2x.glsl").read_text(encoding="utf-8"))
        self.assertLessEqual(len(built.encode()), 128 * 1024)
        self.assertIn("void mainImage", built)
        self.assertNotIn("iFrame", built)

    def test_m1_m2_artifacts_still_match(self) -> None:
        for scale in (1, 2):
            self.assertEqual(generate_m1(SOURCE, scale), (ROOT / "dist" / f"m1-corgi-{scale}x.glsl").read_text())
            for policy in ("conservative", "cursor-only"):
                name = f"m2-corgi-{scale}x-{policy}.glsl"
                self.assertEqual(generate_m2(scale, policy), (ROOT / "dist" / name).read_text())

    def test_frame_durations_speed_and_looping(self) -> None:
        clips = {clip.name: clip for clip in self.pet.clips}
        walk = clips["walk"]
        self.assertEqual([select_frame(walk, t) for t in (0, 149, 150, 299, 300, 450)], [0, 0, 1, 1, 2, 0])
        stand = clips["stand"]
        self.assertEqual(select_frame(stand, 10_000), 1)
        play = clips["play"]
        self.assertEqual(select_frame(play, 166), 1)  # 166 ms * 1.15 crosses 190 ms.

    def test_schedule_is_deterministic_and_varied(self) -> None:
        first = [select_episode(self.scene, "active", i).name for i in range(9)]
        self.assertEqual(first, [select_episode(self.scene, "active", i).name for i in range(9)])
        self.assertTrue({"walk-left", "walk-right", "play", "active-stretch"} <= set(first))
        self.assertGreater(len({select_episode(self.scene, "active", i).name for i in range(100)}), 4)
        later = [select_episode(self.scene, "active", i).name for i in range(9, 18)]
        self.assertNotEqual(first, later)

    def test_walk_continuity_and_orientation(self) -> None:
        # Seed 5 chooses the left walk in the first Active slot.
        t = 10.0
        before = evaluate(self.scene, self.pet, t + .699, 0, 0, True)
        after = evaluate(self.scene, self.pet, t + .701, 0, 0, True)
        self.assertEqual((before.clip, after.clip), ("stand", "walk"))
        self.assertAlmostEqual(before.x, after.x, places=2)
        self.assertEqual(after.face, "left")
        middle = evaluate(self.scene, self.pet, t + 1.95, 0, 0, True)
        self.assertLess(middle.x, -5)
        back = evaluate(self.scene, self.pet, t + 5.0, 0, 0, True)
        self.assertEqual(back.face, "right")
        for slot in range(9):
            start = evaluate(self.scene, self.pet, 10 + slot * 12 + .001, 0, 0, True)
            end = evaluate(self.scene, self.pet, 10 + (slot + 1) * 12 - .001, 0, 0, True)
            self.assertAlmostEqual(start.x, 0, places=2)
            self.assertAlmostEqual(end.x, 0, places=2)

    def test_activity_focus_and_time_jumps(self) -> None:
        self.assertEqual(evaluate(self.scene, self.pet, 9, 0, 0, True).mode, "quiet")
        self.assertEqual(evaluate(self.scene, self.pet, 11, 0, 0, True).mode, "active")
        self.assertEqual(evaluate(self.scene, self.pet, 121, 0, 0, True).mode, "sleeping")
        self.assertEqual(evaluate(self.scene, self.pet, 121, 0, 0, False).clip, "sleep")
        self.assertEqual(evaluate(self.scene, self.pet, 5000.2, 0, 5000, True).clip, "wake")
        self.assertEqual(evaluate(self.scene, self.pet, 5002, 0, 5000, True).mode, "quiet")
        self.assertEqual(evaluate(self.scene, self.pet, 5000.2, 5000, 0, True).mode, "quiet")
        self.assertEqual(evaluate(self.scene, self.pet, 5000.2, 5000, 0, True).x, 0)
        self.assertLess(evaluate(self.scene, self.pet, 5000.2, 5000, 0, True).opacity, 1)

    def test_metadata_rejects_bad_inputs(self) -> None:
        pet_json = json.loads(DEFAULT_PET.read_text())
        scene_json = json.loads(DEFAULT_SCENE.read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = root / "m3-placeholder.png"
            sheet.write_bytes(self.pet.sheet.read_bytes())
            pet_path, scene_path = root / "pet.json", root / "scene.json"
            for change in (
                lambda d: d["clips"]["walk"].update(durations_ms=[150, 0]),
                lambda d: d["clips"]["walk"].update(row=30),
                lambda d: d.update(frame_size=[17, 12]),
            ):
                data = json.loads(json.dumps(pet_json))
                change(data)
                pet_path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    load_pet(pet_path)
            pet_path.write_text(json.dumps(pet_json))
            for change in (
                lambda d: d["episodes"][0]["phases"][0].update(clip="absent"),
                lambda d: d["episodes"][2]["phases"][0].update(to_x=3),
                lambda d: d["episodes"][4]["phases"][1].update(to_x=-40),
            ):
                data = json.loads(json.dumps(scene_json))
                change(data)
                scene_path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    load_scene(scene_path, self.pet)
            with Image.open(sheet) as source:
                image = source.copy()
            image.putpixel((1, 1), (100, 100, 100, 128))
            image.save(sheet)
            with self.assertRaises(ValueError):
                load_pet(pet_path)
            with Image.open(self.pet.sheet) as source:
                image = source.copy()
            for index in range(16):
                image.putpixel((index, 0), (index * 13, 40, 90, 255))
            image.save(sheet)
            with self.assertRaises(ValueError):
                load_pet(pet_path)

    def test_second_pet_and_environment_use_same_compiler(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = Image.new("RGBA", (48, 120), (0, 0, 0, 0))
            for row in range(10):
                sheet.putpixel((8, row * 12 + 10), (50, 190, 120, 255))
            sheet.save(root / "dummy.png")
            pet = json.loads(DEFAULT_PET.read_text())
            pet.update(id="dummy", sheet="dummy.png")
            pet_path = root / "pet.json"
            pet_path.write_text(json.dumps(pet))
            scene = json.loads(DEFAULT_SCENE.read_text())
            scene.update(id="alternate-stage", seed=91, home_x=30)
            scene_path = root / "scene.json"
            scene_path.write_text(json.dumps(scene))
            shader = generate(pet_path, scene_path, 1)
            self.assertIn("pet: dummy; scene: alternate-stage", shader)


if __name__ == "__main__":
    unittest.main()
