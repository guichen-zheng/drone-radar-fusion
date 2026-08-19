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


def read_exact(stream, n):
    buf = b""
    while len(buf) < n:
        chunk = stream.read(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def main():
    model_path = sys.argv[1] if len(sys.argv) > 1 else "model/ONNX/yolo_drone.onnx"
    conf_thresh = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
    imgsz = int(sys.argv[3]) if len(sys.argv) > 3 else 1280

    # 优先用 .pt（更稳定），找不到再退回 .onnx
    pt_alt = model_path.replace(".onnx", ".pt")
    if os.path.exists(pt_alt):
        model_path = pt_alt

    model = YOLO(model_path)
    sys.stderr.write(f"[yolo_worker] 模型已加载: {model_path}\n")
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
            results = model.predict(
                img, imgsz=imgsz, conf=conf_thresh, verbose=False
            )
            dets = []
            for r in results:
                if r.boxes is None:
                    continue
                for b in r.boxes:
                    xyxy = b.xyxy.cpu().numpy()[0]
                    conf = float(b.conf.cpu().numpy()[0])
                    cls_idx = int(b.cls.cpu().numpy()[0])
                    label = (model.names.get(cls_idx, "drone")
                             if hasattr(model, "names") else "drone")
                    x1, y1, x2, y2 = (int(v) for v in xyxy)
                    dets.append({
                        "x": x1, "y": y1,
                        "w": x2 - x1, "h": y2 - y1,
                        "conf": conf, "label": label,
                    })
            results_json = {"detections": dets}

        payload = json.dumps(results_json).encode("utf-8")
        out_stream.write(struct.pack(">I", len(payload)))
        out_stream.write(payload)
        out_stream.flush()


if __name__ == "__main__":
    main()
