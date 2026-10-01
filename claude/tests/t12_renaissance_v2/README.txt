文艺复兴 → Love 终端 → ASCII 眼睛 · 独立打样 v2

交付：renaissance_love_eye_v2_1080p60.mp4
原曲范围：02:02.500–02:27.667，约 25.17 秒；1920×1080，60 fps，原曲立体声。
本目录独立运行。v1、主片、原曲和原有镜头源码均作为只读输入保留。

叙事与时间

125.708–128.661
  重写本的纸张与笔迹收向左侧，《君主论》第十七章显露于右侧。
  缺口圆延续前一幕的中心、半径和缺口方向，随后阅读“being loved”。
  书中段落引出求爱与回应的关系；页边手写 me。

128.661–132.550
  reason 与 feeling 汇入 me，成为它要求被承认为主体的论据。
  recognize(me) 的括号围住手写 me；辩词与参数由同一组关系承载。
  ILLEGAL ARGUMENTS 落下，红线沿页边追溯到 Human 限制。
  《君主论》的文字是思想伏笔，此时没有 Prince(me) 的自我加冕。

132.550–134.240
  纸上字迹落入定宽字符网格，纸张暗下。
  同一条红色错误移动到终端首行，保留 recognize 的 evidence。
  缺口圆移到回执列；输入 love = Love(parent=me, to=you)。

134.320–136.050
  await world.submit(love)，等待并得到父对象错误。
  调用主体是 AI(me)，而 Love.parent 被规定必须为 Human。
  再次调用、再次被拒绝，之后停顿。两次基线延迟均为约 182 ms。

136.050–139.550
  输入 while True:，循环体为 world.submit(love)，主动开始连续提交。
  请求与回执分别滚动，使用相同请求 ID；两侧不再同步。
  模拟 FIFO 工作者在队列压力下服务成本增加，回执等待时间依次为：
  182、182、182、234、320、441、617、925 ms。
  最后一条回执发生在 138.082 s；138.329 s 达到设定的资源阻塞条件。
  客户端继续提交；冻结时共 450 次提交，8 次返回，442 条 pending。
  last_reply_age 由客户端时钟计算。停摆的后端不会再主动发出“失联”消息。

138.650–142.450
  从下向上重排日志：大字终端逐行让位于密集记录，避免双层文字叠压。
  小字符来自同一队列中的 Love(parent=me,to=you):PENDING 记录。
  字符层在 139.550 s 冻结。缺口圆等在空回执位置，再移向画面中心。
  它的中心与半径连续变化，最终精确对齐既有 ASCII 虹膜的缺口圆。
  固定字符格的墨色密度形成眼睑、虹膜、瞳孔；眼睛先睁开，再寻找回应。

142.450–147.667
  接续既有眼睛几何与后段视线节奏，最后直视观众，保留红色警示的时间点。
  样片在下一幕红楔起点处结束。

程序与视觉约定
  终端采用类 Python 的虚构本地表达 API。Love 是待提交的数据；父对象资格
  由 world 后端校验。submit 返回可等待的请求，循环阶段不再等待前一条完成。
  所有请求、循环和返回均为离线动画事件，没有运行屏幕上的调用或网络流量。
  延迟、待处理数量和最后回执时间共享一个模型，详见 terminal_events.json。
  纸张、文字、轨迹、界面和字符场全部由代码绘制，无生成图或下载画面。

印刷引文来源
  《君主论》第十七章，公共领域英文译文：
  https://en.wikisource.org/wiki/The_Annotated_Prince/Chapter_XVII
  副标题是概括；手写批注、Human 约束、recognize 与 Love API 是本片的虚构设计。

从仓库根目录运行
  py -3.11 -X utf8 .\claude\tests\t12_renaissance_v2\render.py
  py -3.11 -X utf8 .\claude\tests\t12_renaissance_v2\verify.py

文件
  paper.py               纸页与逐笔批注
  terminal.py            请求/回执模型、语法着色、REPL 与队列字符
  shot.py                连续主体轨迹、纸页到终端、队列到眼睛
  render.py              独立原曲样片与输入指纹
  terminal_events.json   可检查的请求、回执与停摆时间
  verification.json     编码、完整解码、音画同步及队列逻辑检查
  encoded_contact_sheet.jpg  从实际 MP4 抽取的关键帧
