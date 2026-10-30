"""M4 art, layered scene, timeline, and shader regression checks."""

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.build_m1 import ROOT, SOURCE, generate as generate_m1
from tools.build_m2 import generate as generate_m2
from tools.build_m3 import DEFAULT_PET as M3_PET, DEFAULT_SCENE as M3_SCENE, generate as generate_m3
from tools.build_m4 import DEFAULT_PET, DEFAULT_SCENE, generate
from tools.m3_model import load_pet, select_frame
from tools.m4_model import evaluate, layer_state, load_scene, select_episode
from tools.make_m4_art import outputs


class M4BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pet = load_pet(DEFAULT_PET)
        cls.scene = load_scene(DEFAULT_SCENE, cls.pet)

    def test_source_art_is_editable_and_reproducible(self) -> None:
        for path, expected in outputs().items():
            with self.subTest(path=path.name), Image.open(path) as source:
                self.assertEqual(source.mode, "RGBA")
                self.assertEqual(source.size, expected.size)
                self.assertEqual(source.tobytes(), expected.tobytes())
                self.assertEqual({pixel[3] for pixel in source.get_flattened_data()}, {0, 255})
        self.assertEqual(len(self.pet.palette), 8)
        self.assertEqual(len(self.scene.palette), 15)
        colors = set(self.pet.palette)
        self.assertTrue({(51, 46, 54), (206, 132, 72), (250, 233, 198)} <= colors)

    def test_animation_clips_and_layers_are_present(self) -> None:
        clips = {clip.name: clip for clip in self.pet.clips}
        self.assertTrue({"idle", "breathe", "look", "stand", "walk", "play", "sit",
                         "stretch", "sleep", "wake", "scratch", "happy", "blink"} <= clips.keys())
        self.assertEqual(len(clips["walk"].durations_ms), 6)
        self.assertEqual(select_frame(clips["walk"], 140), 1)
        self.assertEqual(select_frame(clips["stand"], 3000), 3)
        layers = {layer.name: layer for layer in self.scene.layers}
        self.assertEqual({"ground", "tree-trunk", "tree-canopy", "doghouse", "flowers",
                          "leaf", "butterfly", "ball"}, layers.keys())

    def test_episode_selection_and_complete_ball_path(self) -> None:
        first = [select_episode(self.scene, slot).name for slot in range(10)]
        self.assertEqual(first[:4], ["walk-left", "idle-and-look", "ball-play", "walk-right"])
        self.assertGreater(len(set(first)), 4)
        self.assertEqual(sum(e.weight for e in self.scene.episodes), 10)
        ball = next(layer for layer in self.scene.layers if layer.name == "ball")
        self.assertFalse(layer_state(ball, 24, True, 0).frame)
        self.assertGreater(evaluate(self.scene, self.pet, 26.55, 0, True).object_x, 0)
        self.assertGreater(evaluate(self.scene, self.pet, 28.0, 0, True).object_x, 6)
        self.assertEqual(evaluate(self.scene, self.pet, 31.0, 0, True).object_x, 0)
        self.assertEqual(evaluate(self.scene, self.pet, 31.0, 0, True).x, 0)
        play = next(e for e in self.scene.episodes if e.name == "ball-play")
        boundary = 24.0
        for phase in play.phases[:-1]:
            boundary += phase.duration_ms / 1000
            before = evaluate(self.scene, self.pet, boundary - .001, 0, True)
            after = evaluate(self.scene, self.pet, boundary + .001, 0, True)
            self.assertLess(abs(before.x - after.x), .05)
            self.assertLess(abs(before.object_x - after.object_x), .05)
        for slot in range(10):
            start = evaluate(self.scene, self.pet, slot * 12 + .001, 0, True)
            end = evaluate(self.scene, self.pet, (slot + 1) * 12 - .001, 0, True)
            self.assertAlmostEqual(start.x, 0, places=2)
            self.assertAlmostEqual(end.x, 0, places=2)
            self.assertAlmostEqual(start.object_x, 0, places=2)
            self.assertAlmostEqual(end.object_x, 0, places=2)

    def test_ambient_timing_and_focus(self) -> None:
        layers = {layer.name: layer for layer in self.scene.layers}
        self.assertFalse(layer_state(layers["leaf"], 0, True).visible)
        self.assertTrue(layer_state(layers["leaf"], 31, True).visible)
        middle = layer_state(layers["leaf"], 32.5, True)
        self.assertTrue(middle.visible)
        self.assertGreater(middle.y, 8)
        self.assertLess(middle.y, 31)
        self.assertFalse(layer_state(layers["leaf"], 34, True).visible)
        self.assertFalse(layer_state(layers["leaf"], 31, False).visible)
        self.assertTrue(layer_state(layers["butterfly"], 44, True).visible)
        self.assertEqual(layer_state(layers["tree-canopy"], 0, True).frame, 0)
        self.assertEqual(layer_state(layers["tree-canopy"], 1.3, True).frame, 1)
        self.assertEqual(layer_state(layers["tree-canopy"], 1.3, False).frame, 0)
        self.assertEqual(evaluate(self.scene, self.pet, 50, 0, False).clip, "sleep")
        self.assertEqual(evaluate(self.scene, self.pet, 50.2, 50, True).clip, "wake")
        self.assertEqual(evaluate(self.scene, self.pet, 51, 50, True).episode, "refocus-rest")

    def test_shader_is_bounded_reproducible_and_standalone(self) -> None:
        built = generate(DEFAULT_PET, DEFAULT_SCENE, 2)
        self.assertEqual(built, generate(DEFAULT_PET, DEFAULT_SCENE, 2))
        self.assertEqual(built, (ROOT / "dist/m4-corgi-backyard-2x.glsl").read_text())
        self.assertLess(len(built.encode()), 128 * 1024)
        self.assertIn("void mainImage", built)
        self.assertNotIn("iFrame", built)
        behavior = built.split("void m4Pose", 1)[1].split("int m4EnvFrame", 1)[0]
        self.assertNotIn("iTimeCursorChange", behavior)
        self.assertIn("iTimeCursorChange", built)  # M2 visibility still uses it.
        self.assertGreater(len(generate(DEFAULT_PET, DEFAULT_SCENE, 1)), 0)
        self.assertGreater(len(generate(DEFAULT_PET, DEFAULT_SCENE, 3)), 0)

    def test_compiled_frame_data_round_trips_after_deduplication(self) -> None:
        shader = generate(DEFAULT_PET, DEFAULT_SCENE, 2)

        def values(name: str) -> list[int]:
            match = re.search(rf"const (?:int|uint) {name}\[\d+\] = (?:int|uint)\[\d+\]\(([^)]*)\);", shader)
            self.assertIsNotNone(match)
            return [int(item.strip().removesuffix("u"), 0) for item in match.group(1).split(",")]

        def unpack(words: list[int]) -> list[int]:
            return [(word >> (4 * shift)) & 15 for word in words for shift in range(8)]

        pet_starts = values("M4_PET_FRAME_START")
        pet_pixels = unpack(values("M4_PET_DATA"))
        pet_area = self.pet.frame_width * self.pet.frame_height
        self.assertLess(len(pet_pixels), len(self.pet.pixels))
        for frame, start in enumerate(pet_starts):
            self.assertEqual(tuple(pet_pixels[start:start + pet_area]),
                             self.pet.pixels[frame * pet_area:(frame + 1) * pet_area])

        env_starts = values("M4_ENV_FRAME_START")
        env_pixels = unpack(values("M4_ENV_DATA"))
        frame = source = 0
        for layer in self.scene.layers:
            area = layer.width * layer.height
            for _ in layer.durations_ms:
                self.assertEqual(tuple(env_pixels[env_starts[frame]:env_starts[frame] + area]),
                                 self.scene.pixels[source:source + area])
                frame += 1
                source += area

    def test_prior_milestone_artifacts_remain_identical(self) -> None:
        for scale in (1, 2):
            self.assertEqual(generate_m1(SOURCE, scale), (ROOT / "dist" / f"m1-corgi-{scale}x.glsl").read_text())
            for policy in ("conservative", "cursor-only"):
                name = f"m2-corgi-{scale}x-{policy}.glsl"
                self.assertEqual(generate_m2(scale, policy), (ROOT / "dist" / name).read_text())
        self.assertEqual(generate_m3(M3_PET, M3_SCENE, 2), (ROOT / "dist/m3-placeholder-2x.glsl").read_text())

    def test_validator_rejects_bad_layers_and_object_paths(self) -> None:
        source = json.loads(DEFAULT_SCENE.read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for layer in self.scene.layers:
                shutil.copyfile(layer.file, root / layer.file.name)
            path = root / "scene.json"
            mutations = (
                lambda d: d.update(schema_version=2),
                lambda d: d["layers"][0].update(frame_size=[109, 7]),
                lambda d: d["layers"][5].update(to=[109, 8]),
                lambda d: d["layers"][6].update(active_ms=61000),
                lambda d: d["layers"][7].update(motion="path"),
                lambda d: d["episodes"][6]["phases"][2].update(object_from_x=2),
                lambda d: d["episodes"][6]["phases"][4].update(object_to_x=20),
                lambda d: d["episodes"][6]["phases"][-1].update(object_to_x=1),
            )
            for change in mutations:
                data = json.loads(json.dumps(source))
                change(data)
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    load_scene(path, self.pet)
            path.write_text(json.dumps(source))
            with Image.open(root / "ground.png") as source_image:
                image = source_image.copy()
            image.putpixel((0, 0), (1, 2, 3, 128))
            image.save(root / "ground.png")
            with self.assertRaises(ValueError):
                load_scene(path, self.pet)
            image.putpixel((0, 0), (1, 2, 3, 255))
            image.save(root / "ground.png")
            with self.assertRaises(ValueError):
                load_scene(path, self.pet)  # sixteenth environment color

    def test_second_pet_and_scene_build_without_core_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with Image.open(self.pet.sheet) as source:
                pet_image = source.copy()
            pet_image.putpixel((0, 0), (71, 152, 218, 255))
            pet_image.save(root / "alternate-pet.png")
            pet_data = json.loads(DEFAULT_PET.read_text())
            pet_data.update(id="alternate-pet", sheet="alternate-pet.png")
            pet_path = root / "pet.json"
            pet_path.write_text(json.dumps(pet_data))
            for layer in self.scene.layers:
                shutil.copyfile(layer.file, root / layer.file.name)
            scene_data = json.loads(DEFAULT_SCENE.read_text())
            scene_data.update(id="alternate-garden", home_x=74, seed=91)
            scene_path = root / "scene.json"
            scene_path.write_text(json.dumps(scene_data))
            shader = generate(pet_path, scene_path, 1)
            self.assertIn("pet: alternate-pet; scene: alternate-garden", shader)


if __name__ == "__main__":
    unittest.main()
