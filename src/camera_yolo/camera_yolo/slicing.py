"""切片推理所需的网格生成与全局 NMS 工具。"""

import math
from typing import Dict, List, Sequence, Tuple


def _axis_starts(length: int, tile_size: int, overlap: float) -> List[int]:
    """生成覆盖整条轴的均匀起点，并保证相邻切片至少达到指定重叠率。"""
    if length <= 0:
        raise ValueError("image dimensions must be positive")
    if tile_size <= 0:
        raise ValueError("slice_size must be positive")
    if not 0.0 <= overlap < 1.0:
        raise ValueError("slice_overlap must be in [0, 1)")
    if length <= tile_size:
        return [0]

    max_step = tile_size * (1.0 - overlap)
    intervals = max(1, math.ceil((length - tile_size) / max_step))
    span = length - tile_size
    return [round(i * span / intervals) for i in range(intervals + 1)]


def generate_tile_origins(
    image_width: int,
    image_height: int,
    tile_size: int,
    overlap: float,
) -> List[Tuple[int, int]]:
    """返回按行排列的 ``(x, y)`` 切片左上角坐标。"""
    xs = _axis_starts(image_width, tile_size, overlap)
    ys = _axis_starts(image_height, tile_size, overlap)
    return [(x, y) for y in ys for x in xs]


def _iou(a: Dict, b: Dict) -> float:
    ax2 = a["x"] + a["w"]
    ay2 = a["y"] + a["h"]
    bx2 = b["x"] + b["w"]
    by2 = b["y"] + b["h"]

    inter_w = max(0.0, min(ax2, bx2) - max(a["x"], b["x"]))
    inter_h = max(0.0, min(ay2, by2) - max(a["y"], b["y"]))
    intersection = inter_w * inter_h
    if intersection <= 0.0:
        return 0.0

    union = a["w"] * a["h"] + b["w"] * b["h"] - intersection
    return intersection / union if union > 0.0 else 0.0


def global_nms(detections: Sequence[Dict], iou_threshold: float) -> List[Dict]:
    """对映射回整图的检测框执行按类别 NMS。"""
    if not 0.0 <= iou_threshold <= 1.0:
        raise ValueError("slice_nms_iou must be in [0, 1]")

    remaining = sorted(
        range(len(detections)),
        key=lambda index: detections[index]["conf"],
        reverse=True,
    )
    kept = []
    while remaining:
        best = remaining.pop(0)
        kept.append(best)
        best_class = detections[best].get("_class_id", 0)
        remaining = [
            index
            for index in remaining
            if detections[index].get("_class_id", 0) != best_class
            or _iou(detections[best], detections[index]) <= iou_threshold
        ]

    return [dict(detections[index]) for index in kept]
