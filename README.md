# 🛡️Smart Lock (智能无感防窥与锁屏系统)

基于计算机视觉与深度学习大模型的“软件版 Windows Hello”。通过普通摄像头即可实现商用级的面部识别，为您提供**人走自动锁屏**与**陌生人防窥报警**的无感安防体验。

## ✨ 核心特性 (Features)
- ⚡ ****：完全运行在本地，无需联网，不用担心个人隐私泄露
- 🚀 **商用级 AI 引擎**：抛弃传统 Dlib 算法，接入 **InsightFace** (ArcFace) 深度学习框架与 `buffalo_l` 大模型，精准应对侧脸、光线变化，减少误误识别概率。
- 🚶 **人走自动无感锁屏**：内置缓冲计时器（默认 5 秒），离开座位自动锁屏，低头捡东西快速恢复，短时间内不会触发锁屏。
- 🚨 **陌生人闯入秒锁定**：当画面中出现非授权人脸时，无视缓冲时间，瞬间触发系统强制锁屏。
- 💻 **Windows平台兼容**：系统底层原生支持 Windows (`user32.dll`)的锁屏指令。
- 📦 **免安装绿色运行**：支持使用 `PyInstaller` 打包为独立 `.exe` 程序运行。

## 🛠️ 技术栈 (Tech Stack)
- **Python 3.10+** (推荐 3.10.11 以获得最佳环境兼容性)
- **OpenCV** (`cv2`) - 视频流捕获与 UI 渲染
- **InsightFace** - 人脸检测与特征向量 (Embedding) 提取
- **ONNXRuntime** - 深度学习模型的高效 CPU 推理引擎
- **NumPy** - 余弦相似度 (Cosine Similarity) 计算

## 🚀 快速开始 (Getting Started)

### 1. 环境准备
克隆本仓库后，安装依赖库（建议使用国内镜像源以保证速度）：
```python
pip install opencv-python insightface onnxruntime numpy -i [https://pypi.tuna.tsinghua.edu.cn/simple](https://pypi.tuna.tsinghua.edu.cn/simple)
```
### 2.录入你的面部信息
在项目根目录下，放置一张你本人的正脸照片，并严格命名为 my_face.jpg。
(建议：在日常使用电脑的自然光线和角度下，正对摄像头拍摄，以获得最高准确率。)

### 3.运行系统
`python smart_lock.py`
程序首次启动时，会自动从 GitHub 下载所需的人脸大模型 (buffalo_l.zip，约 330MB)。请保持网络畅通。如果下载缓慢，可以手动下载并解压到系统用户目录下的 ~/.insightface/models/buffalo_l/ 文件夹中。
## ⚙️ 核心参数配置 (Configuration)
可以通过修改 smart_lock.py 顶部的全局变量，来定制你的专属安防策略：
```python
CAMERA_ID = 1                  # 摄像头设备编号 (通常为 0 或 1)
MISSING_TIMEOUT = 5.0          # 主人离开画面的容忍时间(秒)，超时即锁屏
SIMILARITY_THRESHOLD = 0.45    # 识别严格度 (0.4 - 0.5 最佳，数值越大越严格)
PROCESS_EVERY_N_FRAMES = 5     # 性能优化：每隔几帧进行一次 AI 推理 (数值越大越省 CPU)
```
## 📦 如何打包为桌面软件 (.exe)
`pyinstaller --clean --icon=NONE smart_lock.py`
打包完成后，将你的 my_face.jpg 复制到生成的 dist/smart_lock/ 文件夹中即可双击运行。
## 🤝 致谢 (Acknowledgments)
感谢 DeepInsight 团队开源了强大的 C 算法。
https://github.com/deepinsight/insightface
