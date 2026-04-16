# model/ONNX/ — 模型文件存放目录

## ★ 待填入文件

### 1. `yolo_drone.onnx`  — YOLO 无人机检测模型
训练并导出步骤：
1. 数据集：推荐 VisDrone-DET（无人机视角目标检测）
   - 官方仓库：https://github.com/VisDrone/VisDrone-Dataset
   - 也可使用 Roboflow 上的无人机数据集：
     https://roboflow.com/search?q=drone+detection
2. 训练（YOLOv8 为例）：
   ```bash
   pip install ultralytics
   yolo train model=yolov8n.pt data=drone.yaml epochs=100 imgsz=640
   ```
3. 导出 ONNX：
   ```bash
   yolo export model=runs/detect/train/weights/best.pt format=onnx opset=12
   ```
4. 将 `best.onnx` 重命名为 `yolo_drone.onnx` 放入此目录

### 2. `classes.txt`  — 类别名称文件
每行一个类别名称，例如：
```
drone
bird
airplane
```
（若仅检测无人机，只需一行 `drone`）

### 3. TensorRT 引擎（可选，GPU 加速）
如果使用 NVIDIA 显卡，可将 ONNX 转为 TRT 引擎以获得更高帧率：
```bash
trtexec --onnx=yolo_drone.onnx --saveEngine=yolo_drone.engine --fp16
```
转换后将 `.engine` 文件放入此目录，并在 `params.yaml` 中修改 `model_path`。
