"""
yolo_worker.py — 在 yolov8 conda 环境里跑推理（ultralytics + 较新 cv2）

由 yolo_node.py 通过 subprocess 启动。通信协议（二进制 stdio）：
  输入：4 字节 BE uint32 = JPEG 长度，然后 JPEG 字节
  输出：4 字节 BE uint32 = JSON 长度，然后 JSON 字节
        JSON 格式：{"detections": [{"x":int,"y":int,"w":int,"h":int,"conf":float,"label":str}, ...]}

该脚本只能用 conda 环境的 Python 运行，不依赖 ROS。
"""
import sys
import os
import struct
import json
import time

# 关键：dup 一份 stdout fd 给 IPC 用（二进制写），然后把真正的 fd=1 重定向到
# stderr。这样任何 Python/C 代码（ultralytics/numpy/torch）的 print/write 都
# 不会污染我们的二进制协议；只有显式写 _ipc_out 的内容才会经原 stdout 出去。
_ipc_fd = os.dup(1)                       # 复制原 stdout fd
os.dup2(2, 1)                              # fd=1 现在指向 stderr
_ipc_out = os.fdopen(_ipc_fd, "wb", buffering=0)
sys.stdout = sys.stderr                    # Python 层也指过去（保险）

# 进 conda 环境后才能 import
import numpy as np
import cv2
from ultralytics import YOLO

try:
    from .slicing import generate_tile_origins, global_nms
except ImportError:
    # yolo_node 以文件路径直接启动本脚本，此时使用同目录的顶层导入。
    from slicing import generate_tile_origins, global_nms


def read_exact(stream, n):
    buf = b""
    while len(buf) < n:
        chunk = stream.read(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def extract_detections(result, offset_x, offset_y, image_width, image_height, names):
    """把单个切片的 YOLO 结果还原到整图坐标。"""
    detections = []
    if result.boxes is None:
        return detections

    for box in result.boxes:
        xyxy = box.xyxy.cpu().numpy()[0]
        confidence = float(box.conf.cpu().numpy()[0])
        class_id = int(box.cls.cpu().numpy()[0])
        label = names.get(class_id, "drone") if isinstance(names, dict) else names[class_id]

        x1 = max(0, min(image_width, int(xyxy[0]) + offset_x))
        y1 = max(0, min(image_height, int(xyxy[1]) + offset_y))
        x2 = max(0, min(image_width, int(xyxy[2]) + offset_x))
        y2 = max(0, min(image_height, int(xyxy[3]) + offset_y))
        if x2 <= x1 or y2 <= y1:
            continue

        detections.append({
            "x": x1,
            "y": y1,
            "w": x2 - x1,
            "h": y2 - y1,
            "conf": confidence,
            "label": label,
            "_class_id": class_id,
        })
    return detections


def predict_sliced(
    model,
    image,
    imgsz,
    conf_thresh,
    slice_size,
    overlap,
    nms_iou,
    hybrid_full_frame=True,
):
    """整图与切片混合推理，统一映射到整图坐标后执行全局 NMS。"""
    image_height, image_width = image.shape[:2]
    origins = generate_tile_origins(image_width, image_height, slice_size, overlap)
    detections = []

    # 整图分支保留近距离大目标的完整轮廓。纯切片会在切片边界截断大目标，
    # 且会改变其相对尺度；整图分支与切片分支最终通过全局 NMS 合并。
    if hybrid_full_frame:
        full_results = model.predict(
            image,
            imgsz=imgsz,
            conf=conf_thresh,
            iou=nms_iou,
            verbose=False,
        )
        detections.extend(extract_detections(
            full_results[0], 0, 0, image_width, image_height, model.names
        ))

    # 当前 ONNX 导出为固定 batch=1，因此逐片调用，避免 batch 维度不匹配。
    for offset_x, offset_y in origins:
        tile = image[
            offset_y:min(offset_y + slice_size, image_height),
            offset_x:min(offset_x + slice_size, image_width),
        ]
        results = model.predict(
            tile,
            imgsz=imgsz,
            conf=conf_thresh,
            iou=nms_iou,
            verbose=False,
        )
        detections.extend(extract_detections(
            results[0], offset_x, offset_y, image_width, image_height, model.names
        ))

    raw_count = len(detections)
    detections = global_nms(detections, nms_iou)
    for detection in detections:
        detection.pop("_class_id", None)
    return detections, len(origins), raw_count


def predict_full_frame(model, image, imgsz, conf_thresh, nms_iou):
    results = model.predict(
        image,
        imgsz=imgsz,
        conf=conf_thresh,
        iou=nms_iou,
        verbose=False,
    )
    height, width = image.shape[:2]
    detections = extract_detections(results[0], 0, 0, width, height, model.names)
    for detection in detections:
        detection.pop("_class_id", None)
    return detections


def main():
    model_path = sys.argv[1] if len(sys.argv) > 1 else "model/ONNX/yolo_drone.onnx"
    conf_thresh = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
    imgsz = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    slice_enabled = sys.argv[4].lower() in {"1", "true", "yes"} if len(sys.argv) > 4 else True
    slice_size = int(sys.argv[5]) if len(sys.argv) > 5 else 960
    slice_overlap = float(sys.argv[6]) if len(sys.argv) > 6 else 0.20
    slice_nms_iou = float(sys.argv[7]) if len(sys.argv) > 7 else 0.45
    hybrid_full_frame = (
        sys.argv[8].lower() in {"1", "true", "yes"} if len(sys.argv) > 8 else True
    )

    # 优先用 .pt（更稳定），找不到再退回 .onnx
    pt_alt = model_path.replace(".onnx", ".pt")
    if os.path.exists(pt_alt):
        model_path = pt_alt

    model = YOLO(model_path, task="detect")
    sys.stderr.write(f"[yolo_worker] 模型已加载: {model_path}\n")
    sys.stderr.write(
        f"[yolo_worker] 切片: enabled={slice_enabled}, size={slice_size}, "
        f"overlap={slice_overlap}, global_nms={slice_nms_iou}, "
        f"full_frame={hybrid_full_frame}\n"
    )
    sys.stderr.flush()

    # 预热推理，避免首帧 JIT 卡很久
    sys.stderr.write("[yolo_worker] 预热中...\n"); sys.stderr.flush()
    warmup = np.zeros((imgsz, imgsz, 3), dtype=np.uint8)
    try:
        model.predict(warmup, imgsz=imgsz, conf=conf_thresh, verbose=False)
        sys.stderr.write("[yolo_worker] 预热完成，开始接受帧\n"); sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"[yolo_worker] 预热失败: {e}\n"); sys.stderr.flush()

    in_stream = sys.stdin.buffer
    out_stream = _ipc_out

    frame_idx = 0
    while True:
        hdr = read_exact(in_stream, 4)
        if hdr is None:
            sys.stderr.write("[yolo_worker] stdin EOF\n"); sys.stderr.flush()
            break
        n = struct.unpack(">I", hdr)[0]
        if n == 0:
            break
        jpeg = read_exact(in_stream, n)
        if jpeg is None:
            break
        frame_idx += 1
        if frame_idx <= 3 or frame_idx % 30 == 0:
            sys.stderr.write(
                f"[yolo_worker] 收到帧 #{frame_idx} ({n} 字节)\n"
            ); sys.stderr.flush()

        arr = np.frombuffer(jpeg, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            results_json = {"detections": []}
        else:
            started = time.perf_counter()
            if slice_enabled:
                dets, tile_count, raw_count = predict_sliced(
                    model,
                    img,
                    imgsz,
                    conf_thresh,
                    slice_size,
                    slice_overlap,
                    slice_nms_iou,
                    hybrid_full_frame,
                )
            else:
                dets = predict_full_frame(
                    model, img, imgsz, conf_thresh, slice_nms_iou
                )
                tile_count = 1
                raw_count = len(dets)
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            if frame_idx <= 3 or frame_idx % 30 == 0:
                sys.stderr.write(
                    f"[yolo_worker] 推理 #{frame_idx}: tiles={tile_count}, "
                    f"full_frame={hybrid_full_frame if slice_enabled else True}, "
                    f"raw={raw_count}, final={len(dets)}, {elapsed_ms:.1f} ms\n"
                )
                sys.stderr.flush()
            results_json = {"detections": dets}

        payload = json.dumps(results_json).encode("utf-8")
        out_stream.write(struct.pack(">I", len(payload)))
        out_stream.write(payload)
        out_stream.flush()


if __name__ == "__main__":
    main()
