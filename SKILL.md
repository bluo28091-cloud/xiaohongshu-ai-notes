---
name: xiaohongshu-ai-notes
description: Search trending AI topics on Xiaohongshu, draft and publish notes (text or video) about latest AI technology and reviews. Use when the user wants to create Xiaohongshu content, publish AI-related notes, search for trending AI topics on RED/小红书, or make social media posts about AI.
---

# 小红书 AI 笔记制作与发布

自动搜索 AI 热门内容，撰写视频文案，通过 AI 文生图 + 图生视频制作高质量视频笔记，配合 AI 解说，经主人审批后发布。

## 依赖安装

```bash
python3 -m pip install --user dashscope moviepy Pillow
```

系统要求：Python 3.9+，macOS/Linux，ffmpeg（moviepy 自带 imageio-ffmpeg）。
需要 DashScope API Key（阿里云百炼），支持文生图、图生视频、语音合成。

## 工作目录

```
output/
  [日期]_[主题名]/
    draft.md              # 视频文案（含分镜）
    note.md               # 小红书笔记描述文案
    storyboard.json       # 分镜数据（结构化）
    keyframes/            # AI 生成的关键帧图片（每场景多张候选）
    user_assets/          # 主人上传的图片和视频
    video_clips/          # 图生视频输出的视频片段
    audio/                # 解说音频
    final.mp4             # 最终视频
```

---

## 完整工作流程（五阶段）

### 阶段一：话题发现与推荐

1. **搜索热门 AI 内容**
   - 使用 `WebSearch` 搜索最新 AI 资讯、产品发布、技术热点
   - 若 `browser-use` 可用，在小红书搜索 `AI工具`、`AI实测`、`AI效率` 等关键词
   - 重点关注近 7 天内互动量高的内容

2. **筛选 3 个候选主题**，评估热度、时效性、可操作性、差异化

3. **提交给主人选择**，使用 `AskQuestion` 展示 3 个候选

---

### 阶段二：文案创作与审批

1. **深度搜集信息**
   - `WebSearch` 搜索该主题的最新资讯、官方公告、评测
   - `WebFetch` 抓取关键参考文章
   - 若 `browser-use` 可用，在小红书分析同主题爆款笔记

2. **撰写视频文案**，创建 `output/[日期]_[主题名]/draft.md`：

   ```markdown
   # 视频文案

   ## 基本信息
   - 目标标题：（2-3个备选）
   - 话题标签：#标签1 #标签2 ...（5-8个）

   ## 分镜脚本
   | 场景 | 画面描述 | 解说词 | 关键帧提示词 | 时长 |
   |------|----------|--------|--------------|------|
   | 1    | 开场：展示产品界面 | "大家好..." | modern AI dashboard... | 5s |
   | 2    | 功能演示 | "这个功能..." | screen recording of... | 8s |
   | ...  | ... | ... | ... | ... |

   ## 素材来源
   对每个场景标注素材来源偏好：
   - AI 生成（文生图 → 图生视频）
   - 网页截图（指定 URL）
   - 主人上传
   ```

3. **同时创建 `storyboard.json`**（供脚本使用）：

   ```json
   {
     "title": "视频标题",
     "scenes": [
       {
         "id": 1,
         "description": "场景画面描述",
         "narration": "这个场景的解说词",
         "keyframe_prompt": "English prompt for text-to-image generation, detailed scene description",
         "duration": 5,
         "source": "ai_generate"
       },
       {
         "id": 2,
         "description": "展示产品截图",
         "narration": "解说词...",
         "keyframe_prompt": null,
         "duration": 8,
         "source": "user_upload",
         "asset_path": "user_assets/demo_screenshot.png"
       }
     ]
   }
   ```

   `source` 可选值：`ai_generate` | `web_screenshot` | `user_upload`

4. **提交文案给主人审批**
   - 展示完整分镜脚本
   - `AskQuestion`：`审批通过 / 需要修改 / 更换主题`

---

### 阶段三：视觉素材准备

#### 3.1 生成关键帧图片

对 `source` 为 `ai_generate` 的场景，用文生图 API 生成候选关键帧：

```bash
python3 xiaohongshu-ai-notes/scripts/generate_keyframes.py \
  --storyboard "output/[日期]_[主题名]/storyboard.json" \
  --output_dir "output/[日期]_[主题名]/keyframes/" \
  --api_key $DASHSCOPE_API_KEY \
  --n 2 \
  --size 720x1280
```

每个场景生成 n 张候选图片，保存为 `keyframes/scene_01_a.png`、`scene_01_b.png` 等。

#### 3.2 网页截图素材

对 `source` 为 `web_screenshot` 的场景，使用 `browser-use` 子代理打开指定 URL 截取页面截图，保存到 `keyframes/` 目录。

#### 3.3 主人审核素材

将每个场景的候选关键帧展示给主人：
- 展示所有候选图片路径
- 主人选择最满意的一张，或上传自己的图片/视频
- 主人上传的素材放入 `user_assets/` 目录
- 更新 `storyboard.json` 中每个场景的 `selected_keyframe` 字段

使用 `AskQuestion` 逐场景确认，或一次性展示所有场景：

```
场景1候选：keyframes/scene_01_a.png, scene_01_b.png
场景2候选：keyframes/scene_02_a.png, scene_02_b.png
options:
  - 使用候选 A
  - 使用候选 B
  - 我要上传自己的素材
```

---

### 阶段四：视频生成

#### 4.1 图生视频

对每个场景的确认关键帧，调用图生视频 API 生成视频片段：

```bash
python3 xiaohongshu-ai-notes/scripts/generate_video_clips.py \
  --storyboard "output/[日期]_[主题名]/storyboard.json" \
  --output_dir "output/[日期]_[主题名]/video_clips/" \
  --api_key $DASHSCOPE_API_KEY \
  --resolution 720P
```

该脚本会：
- 读取 `storyboard.json` 中每个场景的 `selected_keyframe` 和 `keyframe_prompt`
- 对每张关键帧调用 DashScope `VideoSynthesis`（`wan2.6-i2v-flash`）
- 输出 `video_clips/scene_01.mp4`、`scene_02.mp4` 等
- 若主人上传的素材本身就是视频，直接复制到 `video_clips/`

**注意**：图生视频为异步任务，单个场景可能需要 1-3 分钟。脚本会自动等待。

#### 4.2 确认解说配置

使用 `AskQuestion` 让主人选择：

**可选音色**（Qwen3-TTS）：
- Cherry — 年轻女声，活泼自然
- Serena — 成熟女声，知性温和
- Ethan — 年轻男声，阳光有力
- Chelsie — 甜美女声，亲和力强

**语气风格**（自然语言描述）：
- "语速快，语调活泼，像科技博主分享好物"
- "语速适中，语调沉稳专业，像新闻播报"
- "语速偏快，语调轻松有趣，像朋友聊天"

用 `--test` 生成一条样本试听：
```bash
python3 xiaohongshu-ai-notes/scripts/generate_narration.py \
  --storyboard "output/[日期]_[主题名]/storyboard.json" \
  --audio_dir "output/[日期]_[主题名]/audio_test/" \
  --api_key $DASHSCOPE_API_KEY \
  --voice Cherry --speed 1.5 \
  --instructions "语速快，语调活泼" \
  --test 1
```

#### 4.3 合成最终视频

```bash
python3 xiaohongshu-ai-notes/scripts/generate_narration.py \
  --storyboard "output/[日期]_[主题名]/storyboard.json" \
  --clips_dir "output/[日期]_[主题名]/video_clips/" \
  --output "output/[日期]_[主题名]/final.mp4" \
  --audio_dir "output/[日期]_[主题名]/audio/" \
  --api_key $DASHSCOPE_API_KEY \
  --voice Cherry --speed 1.5 \
  --instructions "语速快，语调活泼"
```

该脚本会：
- 用 Qwen3-TTS 合成每段解说（音色和语气由主人选定）
- 用 ffmpeg `atempo` 调整到指定倍速（默认 1.5x）
- 将视频片段与解说音频对齐拼接
- 添加转场效果
- 输出最终 MP4

---

### 阶段五：预览与发布

#### 5.1 预览确认

展示给主人：
- 最终视频路径
- 笔记描述文案
- `AskQuestion`：`确认发布 / 需要修改 / 取消`

#### 5.2 撰写笔记描述

根据文案撰写小红书笔记描述，保存到 `note.md`：
- 标题：20字以内，含数字/emoji/悬念词
- 描述：200-400 字，简洁有力
- 末尾附话题标签

详细模板参考 [note-templates.md](note-templates.md)。

#### 5.3 浏览器自动发布

主人确认后，使用 `browser-use` 子代理执行发布：

1. 打开 `https://creator.xiaohongshu.com/publish/publish`
2. 若未登录，提示主人扫码登录
3. 上传视频文件
4. 设置封面（可从关键帧中选取）
5. 填写标题和描述
6. 添加话题标签
7. 点击发布，确认成功

---

## 注意事项

- **API 费用**：文生图和图生视频会消耗 DashScope 额度，注意控制生成次数
- **登录态**：发布前确保小红书创作者中心已登录
- **内容安全**：不生成违规内容，遵守小红书社区规范
- **频率控制**：单日发布不超过 3 篇
- **原创性**：所有内容必须原创，禁止搬运
- **出错恢复**：任何步骤失败时，保存进度到文件，告知主人失败原因
- **图生视频耗时**：单个场景 1-3 分钟，8 个场景约 10-20 分钟，需提前告知主人

## 技术说明

- **文生图**：DashScope `ImageSynthesis`，模型 `wanx2.1-t2i-turbo`，支持 720x1280 竖版
- **图生视频**：DashScope `VideoSynthesis`，模型 `wan2.6-i2v-flash`，支持 2-15 秒、720P/1080P，异步任务自动等待
- **语音合成**：Qwen3-TTS（`qwen3-tts-instruct-flash`），指令控制语气风格，音色和语气由主人选择，`--test` 快速试听。ffmpeg `atempo` 调速（默认 1.5x）
- **视频合成**：MoviePy 2.x API，`CrossFadeIn`/`CrossFadeOut` 转场。注意 moviepy 2.x 不使用 `moviepy.editor`
- **API 地域**：北京地域 `https://dashscope.aliyuncs.com/api/v1`，API Key 以 `sk-` 开头

## 相关文件

- [note-templates.md](note-templates.md) — 笔记模板和爆款标题公式
- [cover-prompt-guide.md](cover-prompt-guide.md) — 封面 AI 绘图 prompt 指南
- `scripts/generate_keyframes.py` — 文生图关键帧生成脚本
- `scripts/generate_video_clips.py` — 图生视频片段生成脚本
- `scripts/generate_narration.py` — 解说音频 + 最终视频合成脚本
- `scripts/render_slides.py` — Pillow 幻灯片渲染（备用方案）
- `scripts/generate_slideshow.py` — 无声幻灯片视频（备用方案）
- `scripts/requirements.txt` — Python 依赖列表
