# world.execute(me); — 4K60 MV

成片：`output/world_execute_me_4K60.mp4`。

3840×2160，60 fps，16:9，H.264，BT.709；原曲以 AAC 320 kb/s 编码，未剪辑、变速或重新演奏。字幕不烧入画面，可加载 `output/lyrics.srt`。完整分镜及原文歌词映射见 `MV_storyboard_lyrics.md`。

## 制作

全部画面由本工程程序生成。实体部件使用 OpenGL 三维网格、相机、阴影与材质；天体由程序着色器渲染；终端、ASCII、随机字符清屏、卡通、曲线和现代聊天界面由二维绘图程序生成。网格开屏使用带切口的纹理坐标映射。60 fps 各帧按时间独立计算并直接记录，不以补帧或整帧放大制作 4K。

主角、医学界面、天体与历史计算机均为这支 MV 的艺术演绎；界面中的聊天、报错和指令是原创剧情素材，不调用真实服务。老式机器为原创纸带计算机造型，并非某一具体型号的历史复原。

- `src/act_open.py`：START、计算层、眼睛、数学形态、计时装置、碰撞。
- `src/act_middle.py`：扫描与终端、ASCII、纸箱、轨道、双圆、心电、离去。
- `src/act_final.py`：曲面屏幕、纸带计算机、刀架、纸带到聊天、TCP 关闭。
- `src/canvas.py` / `src/geometry.py`：原生分辨率绘图、三维渲染与图像合成。
- `src/render_movie.py`：逐帧录制与编码。
- `src/validate_movie.py`：独立检查交付文件。

## 本机重新生成

需要 Python 3.11+、OpenGL 3.3、NVIDIA NVENC，以及 `requirements.txt` 的依赖。使用 Windows 本地 Cascadia Mono / Segoe UI / Microsoft YaHei 字体。FFmpeg / FFprobe 位于 `tools`。

```powershell
python -X utf8 src/render_movie.py
python -X utf8 src/validate_movie.py
```

导出单帧或短段：

```powershell
python -X utf8 src/render_movie.py --stills "27,84.5,132,197"
python -X utf8 src/render_movie.py --start 176.8 --end 181 --output work/transition.mp4
```

`output/render_manifest.json` 记录实际参数与音源哈希。`output/verification.json` 记录成片完整解码及音频对齐检查结果。`work` 保存设计检查帧、初始分镜备份和日志。
