# 三维风（铜辉三维）· 代码建模真三维知识讲解片

用纯代码做“真三维”的 vibe 知识讲解视频：VTK 代码建模 + PBR 金属材质 + 离屏 EGL 渲染，PIL 叠加金线 HUD 标注、字幕、大数字，ffmpeg 编码。适合古代机械、器物、科技原理（范例：唐代一行与梁令瓒《水运浑天》，124 秒，26 镜）。

## 环境
```bash
sudo apt-get install -y libosmesa6 libegl1 libgl1 libegl-mesa0
pip install vtk numpy pillow
```
VTK 会自动用 vtkEGLRenderWindow（Mesa 软件渲染），无需显卡。1920×1080 约 1.1 秒/帧。

## 文件（引擎/）
- `g3d.py`：三维引擎。Stage（离屏渲染、透明背景 RGBA 截图、灯光、相机、project 3D→屏幕坐标）；几何体 ring_solid（齿轮/开孔环板）、torus、lathe 车削、tube、box、cone；PBR 材质表 bronze/gold/lacquer/wood/patina 等。
- `model.py`：示例模型 Device（浑象天球+星宿、日月双环、子午环、木柜地平、两个报时木人、水轮/齿轮/水流、围观人群），提供 pose()（天球角、日月位置、水轮角、木人手臂、水流）、xray()（柜体半透明、齿轮发光）、patina()（铜锈渐变）。
- `comp.py`：2D 合成。background（暗色渐变+星点+同心纹样）、contact_shadow、compose（辉光）、vignette、chrome（左上栏目、右上年份胶囊）、subtitle（底部居中双行，〖金〗重点、【红】否定、「青」第二主体）、callout（编号金线标注）、bignum、title（金属渐变大标题）、onomat 拟声字、ring_burst 声波环、quote_card 古文引语卡。
- `film.py`：镜头表 SH（每镜：字幕、相机 a→b 轨道参数 f/d/el/az/fov、mood、xray、strikes 敲击时刻等）+ 每镜 overlay。命令：`python3 film.py info`、`python3 film.py still 12.5 30`（抽帧）、`python3 film.py render 起始帧 结束帧`（多路并行）。
- `sfx.py`：按镜头表合成音效（鼓、钟、水流、齿轮滴答、转场 whoosh），输出 sfx.wav。
- `stills.py`：先出剧照用。

## 流程
1. 史实核查（web 搜索+古籍原文），“世界第一”类说法要核准再写。
2. 改 model.py 建新题目的模型；改 film.py 镜头表与 overlay；先 still 抽帧拼联系表检查（遮挡、出框、过暗）。
3. 两路并行 render → `python3 sfx.py` → ffmpeg：
   `ffmpeg -framerate 24 -i frames/%05d.jpg -i sfx.wav -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -shortest out.mp4`

## 画面规范
- 深色背景 + 一个发光金属主体；暖主光+冷轮廓光+程序生成环境贴图 IBL。
- 每镜轨道相机慢推/慢绕，0.25 秒淡入；时长 max(4, 1.3+字数×0.16) 秒。
- 讲原理用 X 光剖视；数据用大数字计数；古文必须紧跟白话；右上年份+出处小字。
- 默认不加背景音乐，只配合成音效。

## 踩坑
- VTK 的 SetVisibility 不接受 numpy.bool_，要先 bool()/float()。
- ffmpeg 输出到网络盘偶发尾部 IO 错误：先写 /tmp 再拷回。
