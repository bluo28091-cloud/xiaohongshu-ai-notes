---
name: xiaohongshu-ai-notes
description: Search trending AI topics on Xiaohongshu, draft and publish notes (text or video) about latest AI technology and reviews. Use when the user wants to create Xiaohongshu content, publish AI-related notes, search for trending AI topics on RED/小红书, or make social media posts about AI.
---

# 小红书 AI 笔记制作与发布

自动搜索 AI 热门内容，撰写小红书笔记，制作封面和带解说的幻灯片视频，经主人审批后通过浏览器发布。

## 依赖安装

```bash
python3 -m pip install --user moviepy Pillow edge-tts
```

系统要求：Python 3.9+，macOS/Linux，ffmpeg（moviepy 自带 imageio-ffmpeg）。

## 工作目录

所有笔记产出文件存放在工作区 `output/` 目录下，按日期和主题组织：

```
output/
  2026-03-21_AI主题名/
    draft.md           # 内容方案
    note.md            # 笔记正文 / 视频描述
    cover.html         # 封面 HTML（浏览器打开截图）
    narration.json     # 解说词（视频笔记时）
    slides/            # 幻灯片图片 01.png ~ 08.png
    audio/             # 解说音频 narration_01.mp3 ~ 08.mp3
    video.mp4          # 无声视频
    video_narrated.mp4 # 带解说视频（最终版）
```

---

## 完整工作流程（三阶段）

### 阶段一：话题发现与推荐

1. **搜索热门 AI 内容**
   - 优先使用 `WebSearch` 搜索最新 AI 资讯、产品发布、技术热点
   - 若 `browser-use` 可用，在小红书 `https://www.xiaohongshu.com` 搜索关键词：`AI工具`、`AI教程`、`ChatGPT`、`AI绘画`、`AI视频`、`Sora`、`Claude`、`AI实测`、`AI效率` 等
   - 记录笔记标题、点赞数、评论数，重点关注 **近7天内** 互动量高的笔记

2. **分析并筛选3个候选主题**

   对每个候选主题评估：
   - **热度**：近期是否有多篇高互动笔记
   - **时效性**：是否与最新 AI 产品/功能发布相关
   - **可操作性**：是否能产出有价值的实测或教程内容
   - **差异化**：能否从独特角度切入

3. **提交给主人选择**

   使用 `AskQuestion` 工具向主人展示3个候选主题，格式如下：

   ```
   标题: 主题名称
   prompt: 以下是为您筛选的3个最可能爆火的小红书AI笔记主题，请选择：
   options:
     - 🔥 主题A：[标题] — [一句话说明热度依据和内容方向]
     - 🔥 主题B：[标题] — [一句话说明热度依据和内容方向]
     - 🔥 主题C：[标题] — [一句话说明热度依据和内容方向]
   ```

---

### 阶段二：内容策划与审批

1. **围绕选定主题深度搜集信息**
   - 使用 `WebSearch` 搜索该 AI 工具/技术的最新资讯、官方公告、评测文章
   - 使用 `browser-use` 子代理在小红书搜索同主题笔记，分析爆款笔记的内容结构和标题写法
   - 使用 `WebFetch` 抓取关键参考文章内容

2. **撰写笔记内容方案**

   创建方案文件 `output/[日期]_[主题名]/draft.md`，内容包括：

   ```markdown
   # 笔记内容方案

   ## 基本信息
   - 笔记类型：图文 / 视频
   - 目标标题：（2-3个备选标题，参考小红书爆款标题公式）
   - 话题标签：#标签1 #标签2 #标签3 ...（5-8个）

   ## 封面设计
   - 封面风格：[描述视觉风格]
   - 封面文案：[封面上的大字文案]
   - AI 绘图 prompt：[用于生成封面的英文 prompt]

   ## 正文大纲
   1. 开头钩子（引发好奇/痛点共鸣）
   2. 核心内容（分点论述）
   3. 实测/案例展示
   4. 总结与互动引导

   ## 视频分镜（仅视频笔记）
   | 序号 | 画面描述 | 配文 | 时长(秒) |
   |------|----------|------|----------|
   | 1    | ...      | ...  | 3-5      |
   | 2    | ...      | ...  | 3-5      |
   ```

3. **提交方案给主人审批**
   - 将方案内容直接展示给主人
   - 使用 `AskQuestion` 确认：`审批通过 / 需要修改 / 更换主题`
   - 若需修改，根据反馈调整后重新提交

---

### 阶段三：制作与发布

#### 3.1 制作封面

使用 AI 图片生成服务制作封面。参考 [cover-prompt-guide.md](cover-prompt-guide.md) 编写 prompt。

**封面设计原则**：
- 尺寸比例：3:4（竖版，小红书推荐）
- 配色鲜明，文字醒目
- 大标题 + 小副标题的排版
- 风格参考：科技感、简约、清新

若使用外部 AI 绘图服务，通过 `browser-use` 子代理操作对应平台生成图片并下载到 `output/[日期]_[主题名]/cover.png`。

#### 3.2 撰写正文

根据审批通过的方案撰写完整笔记正文，保存到 `output/[日期]_[主题名]/note.md`。

**小红书笔记写作规范**：
- 标题：20字以内，含数字/emoji/悬念词
- 正文：控制在 500-800 字
- 段落短小，多用换行
- 适当使用 emoji 增加可读性（但不过度）
- 结尾加互动引导（如"你觉得呢？评论区聊聊"）
- 末尾附话题标签

详细模板参考 [note-templates.md](note-templates.md)。

#### 3.3 制作视频（视频笔记时）

视频制作分三步：生成幻灯片图片 → 生成解说音频 → 合成视频。

**Step 1：生成幻灯片图片**

使用 `render_slides.py`（基于 Pillow，无需浏览器）直接生成幻灯片 PNG：

```bash
python3 xiaohongshu-ai-notes/scripts/render_slides.py \
  --output "output/[日期]_[主题名]/slides/" \
  --font_dir /System/Library/Fonts
```

该脚本需要根据每篇笔记的内容修改，包含 8 个 `slide_N()` 函数，每个函数用 Pillow 绘制一页幻灯片（1080×1440）。修改时注意：
- 使用 `gradient_bg()` 绘制渐变背景
- 使用 `draw_rounded_rect()` 绘制卡片
- 使用 `center_text()` 绘制居中文字
- 保持 `BG1/BG2/ACCENT/CYAN/DIM` 等统一配色

**Step 2：生成解说音频**

创建 `narration.json`，每张幻灯片对应一段解说词：

```json
[
  {"slide": 1, "text": "第一页的解说词..."},
  {"slide": 2, "text": "第二页的解说词..."}
]
```

**Step 3：合成带解说视频**

使用 `generate_narration.py`（基于 edge-tts + moviepy 2.x）一键生成：

```bash
python3 xiaohongshu-ai-notes/scripts/generate_narration.py \
  --narration "output/[日期]_[主题名]/narration.json" \
  --slides_dir "output/[日期]_[主题名]/slides/" \
  --output "output/[日期]_[主题名]/video_narrated.mp4" \
  --audio_dir "output/[日期]_[主题名]/audio/"
```

该脚本会自动：
- 用 edge-tts 的 `zh-CN-XiaoxiaoNeural` 语音合成每段解说
- 每页幻灯片时长自动匹配解说长度 + 0.8秒间隔
- 添加淡入淡出转场
- 合成为最终 MP4 视频

若只需无声视频，使用 `generate_slideshow.py`：

```bash
python3 xiaohongshu-ai-notes/scripts/generate_slideshow.py \
  --slides_dir "output/[日期]_[主题名]/slides/" \
  --output "output/[日期]_[主题名]/video.mp4" \
  --duration 4 --transition fade
```

#### 3.4 预览确认

将所有产出物展示给主人：
- 封面图（直接展示图片路径）
- 笔记正文（直接展示文本）
- 视频文件路径（如适用）
- 使用 `AskQuestion`：`确认发布 / 需要修改 / 取消发布`

#### 3.5 浏览器自动发布

主人确认后，使用 `browser-use` 子代理执行发布：

1. 打开 `https://creator.xiaohongshu.com/publish/publish`
2. 若未登录，提示主人扫码登录，等待登录完成
3. 选择笔记类型（图文/视频）
4. **图文笔记发布流程**：
   - 上传封面图和其他配图
   - 填写标题
   - 填写正文内容
   - 添加话题标签
5. **视频笔记发布流程**：
   - 上传视频文件
   - 设置封面
   - 填写标题和描述
   - 添加话题标签
6. 点击「发布」按钮
7. 确认发布成功，截图保存发布状态

---

## 注意事项

- **登录态**：发布前确保小红书创作者中心已登录。若未登录，提示主人扫码并等待。
- **内容安全**：不生成违规内容，遵守小红书社区规范。
- **频率控制**：单日发布不超过3篇，避免被限流。
- **原创性**：所有内容必须原创，禁止搬运。仅参考其他笔记的选题和结构。
- **出错恢复**：任何步骤失败时，保存当前进度到文件，告知主人失败原因。

## 技术说明

- **幻灯片渲染**：使用 Pillow 纯 Python 绘制，不依赖浏览器或 Playwright。通过 `ImageDraw` 绘制渐变背景、圆角矩形卡片、SVG 风格图标和中文文字。
- **语音合成**：使用 `edge-tts` 库调用微软 Edge TTS 服务，支持多种中文语音（默认 XiaoxiaoNeural），可调节语速。
- **视频合成**：使用 MoviePy 2.x API（`from moviepy import ...`），支持 `CrossFadeIn`/`CrossFadeOut` 转场效果。注意 moviepy 2.x 不使用 `moviepy.editor` 子模块。
- **字体加载**：macOS 下从 `/System/Library/Fonts` 加载系统字体，优先查找 `PingFang.ttc`；Linux 下查找 `NotoSansCJK`。

## 相关文件

- [note-templates.md](note-templates.md) — 笔记正文模板和爆款标题公式
- [cover-prompt-guide.md](cover-prompt-guide.md) — 封面 AI 绘图 prompt 指南
- `scripts/render_slides.py` — Pillow 幻灯片图片渲染脚本（需按笔记内容定制）
- `scripts/generate_narration.py` — 解说音频生成 + 带解说视频合成脚本
- `scripts/generate_slideshow.py` — 无声幻灯片视频生成脚本
- `scripts/requirements.txt` — Python 依赖列表
