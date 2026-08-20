# model/ONNX/ — 模型文件存放目录

## 当前模型

### `yolo_drone.onnx` — YOLOv8s 无人机检测模型

- 权重来源：`runs/detect/drone_v8s_640/weights/best.pt`
- 训练数据：`Drone.v1i.yolov8`
- 训练尺寸：640
- ONNX 固定输入：`1x3x1280x1280`
- 输出：`1x5x33600`
- 类别：`drone`

模型虽然以 640 训练，但导出和推理使用 1280，以保留更多小目标细节。项目推理采用
“整图一次 + 960 重叠切片”的混合策略：整图负责近距离大目标，切片负责远距离小目标。

重新导出命令：

```bash
cd /home/guichen/Documents/ultralytics
/home/guichen/miniconda3/envs/yolov8/bin/yolo export \
  model=runs/detect/drone_v8s_640/weights/best.pt \
  format=onnx imgsz=1280 device=cpu \
  simplify=True dynamic=False half=False nms=False
```

导出后，把 `runs/detect/drone_v8s_640/weights/best.onnx` 复制为本目录的
`yolo_drone.onnx`。

### `classes.txt` — 类别名称文件
每行一个类别名称，例如：
```
drone
bird
airplane
```
（若仅检测无人机，只需一行 `drone`）

### TensorRT 引擎（可选，GPU 加速）
如果使用 NVIDIA 显卡，可将 ONNX 转为 TRT 引擎以获得更高帧率：
```bash
trtexec --onnx=yolo_drone.onnx --saveEngine=yolo_drone.engine --fp16
```
转换后将 `.engine` 文件放入此目录，并在 `params.yaml` 中修改 `model_path`。
