# 封面 AI 绘图 Prompt 指南

## 封面设计规范

- **比例**：3:4 竖版（1080×1440px）
- **构图**：上半部分为视觉主体，下半部分留白放标题文案
- **配色**：高对比度，避免暗沉。推荐：科技蓝、活力橙、清新绿、渐变紫
- **文案区**：封面上需要有醒目的中文大标题，建议在生成图片后用 HTML 叠加文字

## Prompt 构建公式

```
[主体描述] + [风格修饰] + [色调氛围] + [构图指示] + [画质修饰]
```

## 按笔记类型的 Prompt 模板

### 工具测评封面

```
A clean modern tech illustration showing [工具/概念的视觉隐喻],
minimalist flat design style, soft gradient background in [blue-purple / orange-pink / green-teal],
centered composition with space at bottom for text overlay,
professional and inviting, 3:4 aspect ratio, high quality digital art
```

示例：
```
A clean modern tech illustration showing a friendly robot assistant
holding a glowing laptop screen with sparkles,
minimalist flat design style, soft gradient background in blue-purple,
centered composition with space at bottom for text overlay,
professional and inviting, 3:4 aspect ratio, high quality digital art
```

### 教程类封面

```
A step-by-step tutorial style illustration showing [操作过程的简化视觉],
isometric / 2.5D design style, bright and cheerful color palette,
[主色调] dominant with white accents,
clean layout with visual hierarchy, space at bottom third for title text,
3:4 aspect ratio, crisp vector-style digital illustration
```

### 合集推荐封面

```
A collection/grid layout illustration showing [N] different [物品/图标] arranged neatly,
modern flat design, colorful with consistent style,
[配色方案] color scheme on clean background,
organized grid composition with breathing room,
space at bottom for text, 3:4 aspect ratio, polished digital art
```

### AI 绘画/创作类封面

```
A stunning [art style] artwork demonstrating AI-generated creativity,
[具体画面描述], vibrant colors, dramatic lighting,
cinematic composition, space at bottom for text overlay,
3:4 aspect ratio, masterpiece quality, trending on artstation
```

## 文字叠加方案

AI 生成的图片通常不擅长渲染中文，建议用 HTML 生成文字叠加层：

```html
<div style="width:1080px; height:1440px; position:relative;">
  <img src="cover_bg.png" style="width:100%; height:100%; object-fit:cover;" />
  <div style="
    position: absolute;
    bottom: 80px;
    left: 0;
    right: 0;
    text-align: center;
    padding: 40px;
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
  ">
    <h1 style="
      color: white;
      font-size: 72px;
      font-weight: 900;
      text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
      margin: 0 0 16px 0;
      line-height: 1.2;
    ">封面大标题</h1>
    <p style="
      color: rgba(255,255,255,0.9);
      font-size: 36px;
      margin: 0;
    ">副标题说明文字</p>
  </div>
</div>
```

用 `browser-use` 子代理在浏览器中打开此 HTML 并截图，即可得到带中文文字的封面图。

## 色彩搭配速查

| 主题类型 | 推荐主色 | 渐变方向 |
|----------|----------|----------|
| AI 工具测评 | #6366F1 靛蓝 → #8B5CF6 紫 | 左上→右下 |
| 效率提升 | #F97316 橙 → #EAB308 金 | 左→右 |
| 创意/绘画 | #EC4899 粉 → #8B5CF6 紫 | 左下→右上 |
| 编程/技术 | #06B6D4 青 → #3B82F6 蓝 | 上→下 |
| 免费资源 | #10B981 绿 → #06B6D4 青 | 左→右 |
| 对比测评 | #EF4444 红 → #6366F1 靛蓝 | 分屏 |
