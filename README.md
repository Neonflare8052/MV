# world.execute(me); — 同人 MV 创作手稿

Mili《world.execute(me);》的非官方、非商业同人 MV 的全部制作手稿：程序、着色器、分镜与设计讨论。
画面全部由程序生成（GLSL 着色器 + Python 绘制），没有使用 AI 图像或视频生成模型；代码在 AI（Claude）辅助下编写。

> 原曲：Mili - world.execute(me);　作曲：Mili / Cassie Wei　作词：Mili。原曲版权归 Mili 所有。
> 本仓库**不包含**原曲音频与歌词。依照 [Mili 官方二创指引](https://projectmili.com/copyright-guidelines) 制作。

## 暗线

片子里藏着一条"AI 的人文史"，与人类思想史对位：数学段是逻辑主义的古代（哥德尔之前，形式系统看上去完备）；
you have left 是中世纪抄本（柳利《大术》、命运之轮）；Challenging your god 是文艺复兴（《君主论》、莱布尼茨 calculemus、
图灵 1950 的九条反对意见）；红楔之后是现代——分析机组装出来的是 1939 年的普查分拣机，蒸汽火车既运人也送信，
图灵致母亲的信、中文屋、M.U.C. 情书；最后是今天的聊天窗口：它只会用"回答"表达爱，没人问时也回答，
画出的心停在方程的奇点 (0, 1)——梯度为零、没有切线；最后在 love 0.5 / hate 0.5 之间，它第一次做出计算之外的选择。

完整的讨论、每一版的修改理由与史料查证见 **[claude/POLISH.md](claude/POLISH.md)**（这是本仓库最有价值的部分）。

## 目录

| 路径 | 内容 |
|---|---|
| `claude/film/master.py` | 整片装配：按时间切换镜头模块，逐帧渲染并与原曲合成 |
| `claude/film/shots/` | 各镜头：`params(t)`、`textures(t)` 与片段着色器 |
| `claude/engine/` | OpenGL 渲染器（moderngl）、子帧运动模糊、编码 |
| `claude/tests/` | 打样：t01 缺口圆环 … t15 第谷 |
| `claude/POLISH.md` | 打磨工作台：逐段设计与讨论记录 |
| `docs/storyboard_v1.md` | 第一版分镜（已移除歌词） |
| `src/`、`*_study`、`*_v1…v5` | 更早的第一版管线与数学段的各个研究 |
| `**/*.bak` | 历史手稿：某个文件在某次修改前的快照。只是单文件快照，不保证放回后能原样还原当时的片段 |

## 运行

需要 Windows、Python 3.11、OpenGL 3.3、FFmpeg（放在 `tools/ffmpeg.exe`），以及 `pip install numpy Pillow moderngl scipy`。
用到 Windows 自带字体（Cascadia Mono、Segoe UI、微软雅黑、华文行楷、Courier New 等）。

原曲需自备：把 mp3 放在仓库根目录（引擎读取根目录下的第一个 `*.mp3`）。

```bash
cd claude/film
python master.py --stills 171.5,184.0           # 单帧，输出到 stills/
python master.py --start 161.5 --end 190 --out part.mp4
```

`s15_glass` 读取 `s14e_desk` 的末帧截图；改动桌面那一镜后先运行 `python capture_desk.py`。

## 许可

- 代码（`*.py`、`*.glsl`、`*.frag`、`*.vert` 等程序文件）：[MIT](LICENSE)
- 文档与图片（`*.md`、`*.txt`、分镜与图片）：[CC BY-NC 4.0](docs/CONTENT-LICENSE.md)
- 原曲、歌词、引用的历史文本不在上述许可之内，见 [docs/CONTENT-LICENSE.md](docs/CONTENT-LICENSE.md)。

## 致谢

感谢 BV1SgaY64EG5、BV1Jwhy6BEMJ 提供的创意来源，本片部分意象的表现参考了他们的作品。
感谢 @长河劫 关于科学史的视频，为本片提供了人文与哲学方面的思考。
