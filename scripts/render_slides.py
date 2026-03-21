#!/usr/bin/env python3
"""
Generate slide images directly with Pillow. No browser needed.
Usage:
    python render_slides.py --output ./slides/ --font_dir /System/Library/Fonts
"""

import argparse
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1440


def find_font(font_dir, names):
    for name in names:
        for root, _, files in os.walk(font_dir):
            for f in files:
                if name.lower() in f.lower():
                    return os.path.join(root, f)
    return None


def load_fonts(font_dir):
    cjk_names = ["PingFang", "Hiragino Sans", "STHeiti", "NotoSansSC", "NotoSansCJK", "Arial Unicode"]
    path = find_font(font_dir, cjk_names)
    if not path:
        path = find_font(font_dir, ["Arial", "Helvetica"])
    if not path:
        return {}
    fonts = {}
    for size in [20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 44, 56, 64, 72, 80, 96, 120, 160]:
        try:
            fonts[size] = ImageFont.truetype(path, size)
        except Exception:
            fonts[size] = ImageFont.load_default()
    return fonts


# ── Drawing helpers ──

def gradient_bg(draw, colors, direction="diagonal"):
    c1, c2 = colors
    for y in range(H):
        r = int(c1[0] + (c2[0] - c1[0]) * y / H)
        g = int(c1[1] + (c2[1] - c1[1]) * y / H)
        b = int(c1[2] + (c2[2] - c1[2]) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def draw_rounded_rect(draw, bbox, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw, y, text, font, fill="white"):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=font, fill=fill)
    return bbox[3] - bbox[1]


def deco_line(draw):
    for x in range(W):
        ratio = x / W
        r = int(99 + (6 - 99) * ratio)
        g = int(102 + (182 - 102) * ratio)
        b = int(241 + (212 - 241) * ratio)
        draw.line([(x, H - 5), (x, H)], fill=(r, g, b))


BG1 = (7, 11, 26)
BG2 = (23, 17, 74)
ACCENT = (129, 140, 248)
CYAN = (34, 211, 238)
DIM = (160, 160, 200)
CARD_BG = (20, 20, 50)
CARD_BORDER = (50, 50, 90)


# ── Slides ──

def slide_1(fonts):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    gradient_bg(d, [BG1, BG2])

    draw_rounded_rect(d, (W - 260, 40, W - 50, 100), 30, fill=(239, 68, 68))
    d.text((W - 240, 50), "AI 实测", font=fonts.get(28), fill="white")

    labels = ["写方案", "做视频", "析数据", "约会议"]
    box_w, box_h, gap = 130, 130, 32
    total = len(labels) * box_w + (len(labels) - 1) * gap
    sx = (W - total) // 2
    for i, label in enumerate(labels):
        x = sx + i * (box_w + gap)
        y = 340
        draw_rounded_rect(d, (x, y, x + box_w, y + box_h), 24, fill=CARD_BG, outline=CARD_BORDER, width=1)
        center_x = x + box_w // 2
        bbox = d.textbbox((0, 0), label, font=fonts.get(24))
        tw = bbox[2] - bbox[0]
        d.text((center_x - tw // 2, y + 50), label, font=fonts.get(24), fill=DIM)

    center_text(d, 580, "一个人", fonts.get(96), fill=ACCENT)
    center_text(d, 700, "= 一个团队？", fonts.get(96), fill="white")

    for x in range(W):
        ratio = x / W
        r = int(99 + (6 - 99) * ratio)
        g = int(102 + (182 - 102) * ratio)
        b = int(241 + (212 - 241) * ratio)
        d.line([(x, 880), (x, 883)], fill=(r, g, b))

    center_text(d, 940, "钉钉 AI「悟空」实测", fonts.get(38), fill=DIM)
    deco_line(d)
    return img


def slide_2(fonts):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    gradient_bg(d, [BG1, BG2])

    d.text((100, 200), "WHAT IS WUKONG", font=fonts.get(24), fill=ACCENT)
    d.text((100, 280), "悟空", font=fonts.get(80), fill="white")
    d.text((100, 390), "不是聊天 AI", font=fonts.get(72), fill="white")

    d.text((100, 540), "它是一个能直接帮你干活的", font=fonts.get(36), fill=DIM)
    d.text((100, 600), "AI 员工团队", font=fonts.get(44), fill="white")

    draw_rounded_rect(d, (80, 730, W - 80, 950), 28, fill=CARD_BG, outline=CARD_BORDER, width=1)
    d.text((140, 770), "你说一句 → 它直接执行", font=fonts.get(34), fill=CYAN)
    d.text((140, 840), "写方案、做视频、约会议、分析数据", font=fonts.get(30), fill=DIM)

    d.text((W - 200, H - 80), "02 / 08", font=fonts.get(22), fill=(60, 60, 100))
    deco_line(d)
    return img


def make_scene_slide(fonts, num, tag, title, cmd, results, verdict, page):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    gradient_bg(d, [BG1, BG2])

    d.text((100, 120), num, font=fonts.get(120), fill=(40, 40, 80))

    draw_rounded_rect(d, (100, 280, 300, 330), 25, fill=ACCENT)
    bbox = d.textbbox((0, 0), tag, font=fonts.get(22))
    tw = bbox[2] - bbox[0]
    d.text((200 - tw // 2, 288), tag, font=fonts.get(22), fill="white")

    d.text((100, 370), title, font=fonts.get(64), fill="white")

    draw_rounded_rect(d, (80, 490, W - 80, 660), 20, fill=CARD_BG, outline=CARD_BORDER, width=1)
    d.line([(84, 494), (84, 656)], fill=ACCENT, width=4)
    d.text((120, 510), "我的指令", font=fonts.get(20), fill=ACCENT)
    y_cmd = 550
    for line in cmd.split("\n"):
        d.text((120, y_cmd), line, font=fonts.get(32), fill=(220, 220, 240))
        y_cmd += 44

    y = 700
    for r in results:
        d.text((120, y), "→", font=fonts.get(28), fill=CYAN)
        d.text((170, y), r, font=fonts.get(30), fill=DIM)
        y += 52

    draw_rounded_rect(d, (80, y + 30, W - 80, y + 120), 20, fill=(15, 30, 45), outline=(30, 60, 80), width=1)
    center_text(d, y + 50, verdict, fonts.get(34), fill=CYAN)

    d.text((W - 200, H - 80), page, font=fonts.get(22), fill=(60, 60, 100))
    deco_line(d)
    return img


def slide_3(fonts):
    return make_scene_slide(fonts, "01", "实测场景", "内容创作",
        "帮我做一个讲 AI 工具\n推荐的视频脚本",
        ["自动生成选题分析", "完整脚本大纲", "口播稿 + 字幕文件"],
        "以前 2 小时 → 现在 5 分钟", "03 / 08")


def slide_4(fonts):
    return make_scene_slide(fonts, "02", "实测场景", "跨境电商选品",
        "帮我找下一季可能在\n北美爆款的宠物用品",
        ["自动对接 1688 数据", "分析市场趋势", "生成选品报告 + 竞品分析"],
        "连竞品分析都帮你做了", "04 / 08")


def slide_5(fonts):
    return make_scene_slide(fonts, "03", "实测场景", "企业办公",
        "帮我约小王\n明天下午 3 点开会",
        ["自动查双方忙闲时间", "避开冲突创建日程", "发送会议通知"],
        "再也不用拉群问\"你几点有空\"", "05 / 08")


def slide_6(fonts):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    gradient_bg(d, [BG1, BG2])

    d.text((90, 160), "最让我惊喜的", font=fonts.get(56), fill="white")
    d.text((90, 240), "3 个细节", font=fonts.get(64), fill=ACCENT)

    items = [
        ("1", "底层真的重构了", "CLI 化改造，AI 直接调用功能\n不是模拟鼠标点击"),
        ("2", "权限安全可控", "你看不到的数据 AI 也碰不到\n所有操作有日志可查"),
        ("3", "费用完全透明", "Token 消耗实时可见\n像管预算一样管 AI"),
    ]

    y = 400
    for num, title, desc in items:
        draw_rounded_rect(d, (80, y, W - 80, y + 200), 24, fill=CARD_BG, outline=CARD_BORDER, width=1)
        draw_rounded_rect(d, (110, y + 30, 170, y + 90), 16, fill=ACCENT)
        bbox = d.textbbox((0, 0), num, font=fonts.get(32))
        nw = bbox[2] - bbox[0]
        d.text((140 - nw // 2, y + 38), num, font=fonts.get(32), fill="white")

        d.text((200, y + 36), title, font=fonts.get(32), fill="white")
        desc_y = y + 90
        for line in desc.split("\n"):
            d.text((200, desc_y), line, font=fonts.get(26), fill=DIM)
            desc_y += 38
        y += 240

    d.text((W - 200, H - 80), "06 / 08", font=fonts.get(22), fill=(60, 60, 100))
    deco_line(d)
    return img


def slide_7(fonts):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    gradient_bg(d, [BG1, BG2])

    center_text(d, 140, "OVERALL RATING", fonts.get(28), fill=ACCENT)
    center_text(d, 220, "8.5", fonts.get(160), fill=ACCENT)
    center_text(d, 420, "/ 10", fonts.get(36), fill=(60, 60, 100))

    lx, rx = 60, W // 2 + 20
    bw = W // 2 - 80
    draw_rounded_rect(d, (lx, 530, lx + bw, 900), 20, fill=CARD_BG, outline=(34, 80, 50), width=1)
    center_x_l = lx + bw // 2
    bbox = d.textbbox((0, 0), "优 点", font=fonts.get(24))
    d.text((center_x_l - (bbox[2] - bbox[0]) // 2, 555), "优 点", font=fonts.get(24), fill=(34, 197, 94))
    pros = ["一句话执行复杂任务", "覆盖十大行业场景", "安全可控可审计"]
    py = 620
    for p in pros:
        d.text((lx + 40, py), f"· {p}", font=fonts.get(26), fill=DIM)
        py += 52

    draw_rounded_rect(d, (rx, 530, rx + bw, 900), 20, fill=CARD_BG, outline=(80, 40, 40), width=1)
    center_x_r = rx + bw // 2
    bbox = d.textbbox((0, 0), "不 足", font=fonts.get(24))
    d.text((center_x_r - (bbox[2] - bbox[0]) // 2, 555), "不 足", font=fonts.get(24), fill=(248, 113, 113))
    cons = ["仅限钉钉生态", "部分功能需企业版", "复杂任务偶需修正"]
    cy = 620
    for c in cons:
        d.text((rx + 40, cy), f"· {c}", font=fonts.get(26), fill=DIM)
        cy += 52

    center_text(d, 980, "适合", fonts.get(30), fill=DIM)
    center_text(d, 1040, "创业者 · 小团队 · 创作者 · 电商卖家", fonts.get(30), fill="white")

    d.text((W - 200, H - 80), "07 / 08", font=fonts.get(22), fill=(60, 60, 100))
    deco_line(d)
    return img


def slide_8(fonts):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    gradient_bg(d, [BG1, BG2])

    cx, cy_c = W // 2, 440
    r = 80
    d.ellipse((cx - r, cy_c - r, cx + r, cy_c + r), fill=ACCENT)
    heart = "♥"
    bbox = d.textbbox((0, 0), heart, font=fonts.get(64))
    hw = bbox[2] - bbox[0]
    d.text((cx - hw // 2, cy_c - 40), heart, font=fonts.get(64), fill="white")

    center_text(d, 600, "关注我", fonts.get(72), fill="white")
    center_text(d, 700, "获取更多 AI 干货", fonts.get(72), fill="white")

    center_text(d, 860, "AI 工具实测 · 效率提升技巧", fonts.get(34), fill=DIM)
    center_text(d, 920, "每周更新 不踩坑指南", fonts.get(34), fill=DIM)

    btn_text = "点 击 关 注"
    bbox = d.textbbox((0, 0), btn_text, font=fonts.get(32))
    btn_w = bbox[2] - bbox[0] + 120
    btn_h = 80
    btn_x = (W - btn_w) // 2
    btn_y = 1040
    draw_rounded_rect(d, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), 40, fill=ACCENT)
    d.text((btn_x + 60, btn_y + 16), btn_text, font=fonts.get(32), fill="white")

    deco_line(d)
    return img


def main():
    parser = argparse.ArgumentParser(description="Render slides as PNG with Pillow")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--font_dir", default="/System/Library/Fonts", help="System fonts directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    fonts = load_fonts(args.font_dir)
    if not fonts:
        print("Warning: No suitable font found, using defaults")

    slides = [slide_1, slide_2, slide_3, slide_4, slide_5, slide_6, slide_7, slide_8]

    for i, fn in enumerate(slides, 1):
        img = fn(fonts)
        path = os.path.join(args.output, f"{i:02d}.png")
        img.save(path, "PNG")
        print(f"Saved slide {i} -> {path}")

    print(f"\nDone! {len(slides)} slides saved to {args.output}")


if __name__ == "__main__":
    main()
