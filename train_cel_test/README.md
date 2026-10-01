# 蒸汽火车 / 统计卡 / 工厂近景测试

独立镜头实验，6 秒，1920×1080，60 fps。主卡片固定在紧接蒸汽机车的第一节车厢侧面，远处是 18 节有体积的车厢沿曲线延伸。原曲音频从 162.632 秒开始。测试放宽了镜头时长以观察空间与运镜，尚未套用主片原段落的剪辑时长。

| 测试时间 | 镜头与空间关系 |
| --- | --- |
| 0–1.05 秒 | 跟随第一节车厢侧面的卡片；车头同框，轨枕和固定在地面的电线杆移动 |
| 1.05–3.50 秒 | 镜头从侧面连续抬升到车头前上方，转向后方，看清蜿蜒的整列车厢 |
| 3.50–4.10 秒 | 保留完整车列轮廓，镜头跟随车头向前行进 |
| 4.10–6.00 秒 | 镜头稍降；二维工厂与围墙从右侧快速进入，带轻微失焦；更近的门柱掠过镜头 |

技术：Python + ModernGL 的真实网格、深度缓冲和透视摄影机；车体用少量色阶及细轮廓渲染成平面插画风格。卡片是程序绘制的平面图形。近景工厂和围墙使用程序绘制的二维透明层，加独立的视差位移与轻微模糊。轨道和车厢共用曲线路径，机车车轮转动，连杆往复。黑、纸色为主，红色保留在统计字段上。没有使用生成图片或外部视觉素材。

`render.py` 生成关键帧和视频；`verify.py` 检查实际编码视频的尺寸、帧数、时长、完整解码及起中末三段音频同步。`verification.json` 保存检查结果，`encoded_contact_sheet.jpg` 来自实际 MP4 的抽帧。

运行环境为本机 Python 3.12，NumPy、Pillow 和此目录 `_vendor` 内的 ModernGL / glcontext。编码使用工作区 `tools/ffmpeg.exe` 与 NVIDIA H.264 编码器。

```powershell
& '%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' '.\train_cel_test\render.py' --stills
& '%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' '.\train_cel_test\render.py'
& '%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' '.\train_cel_test\verify.py'
```
