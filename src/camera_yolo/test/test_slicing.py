import unittest

from camera_yolo.slicing import generate_tile_origins, global_nms


class TestSlicing(unittest.TestCase):
    def test_2448_by_2048_uses_nine_tiles(self):
        origins = generate_tile_origins(2448, 2048, 960, 0.20)
        self.assertEqual(len(origins), 9)
        self.assertEqual(origins[0], (0, 0))
        self.assertEqual(origins[-1], (1488, 1088))

    def test_tiles_cover_image_without_gaps(self):
        origins = generate_tile_origins(2448, 2048, 960, 0.20)
        xs = sorted({x for x, _ in origins})
        ys = sorted({y for _, y in origins})
        max_step = 960 * (1.0 - 0.20)
        self.assertTrue(all(b - a <= max_step for a, b in zip(xs, xs[1:])))
        self.assertTrue(all(b - a <= max_step for a, b in zip(ys, ys[1:])))

    def test_global_nms_removes_same_class_duplicate(self):
        detections = [
            {"x": 100, "y": 100, "w": 50, "h": 50, "conf": 0.9, "_class_id": 0},
            {"x": 102, "y": 102, "w": 50, "h": 50, "conf": 0.8, "_class_id": 0},
            {"x": 102, "y": 102, "w": 50, "h": 50, "conf": 0.7, "_class_id": 1},
        ]
        kept = global_nms(detections, 0.45)
        self.assertEqual(len(kept), 2)
        self.assertEqual([item["conf"] for item in kept], [0.9, 0.7])


if __name__ == "__main__":
    unittest.main()
