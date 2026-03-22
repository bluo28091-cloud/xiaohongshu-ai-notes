#!/usr/bin/env python3
"""
Generate keyframe images for each scene using DashScope ImageSynthesis (text-to-image).

Usage:
    python generate_keyframes.py \
        --storyboard storyboard.json \
        --output_dir keyframes/ \
        --api_key sk-xxx \
        --n 2 --size 720x1280
"""

import argparse
import json
import os
import urllib.request

import dashscope
from dashscope import ImageSynthesis

dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

MODEL = "wanx2.1-t2i-turbo"
SUFFIX_MAP = {0: "a", 1: "b", 2: "c", 3: "d"}


def generate_images(prompt: str, n: int, size: str, api_key: str) -> list:
    w, h = size.split("x")
    dash_size = f"{w}*{h}"

    rsp = ImageSynthesis.call(
        api_key=api_key,
        model=MODEL,
        prompt=prompt,
        n=n,
        size=dash_size,
    )

    if rsp.status_code != 200:
        raise RuntimeError(
            f"ImageSynthesis error {rsp.status_code}: {rsp.code} - {rsp.message}"
        )

    urls = [r.url for r in rsp.output.results]
    return urls


def main():
    parser = argparse.ArgumentParser(description="Generate keyframe images from storyboard")
    parser.add_argument("--storyboard", required=True, help="Path to storyboard.json")
    parser.add_argument("--output_dir", required=True, help="Output directory for keyframe images")
    parser.add_argument("--api_key", default=None, help="DashScope API key")
    parser.add_argument("--n", type=int, default=2, help="Number of candidates per scene (1-4)")
    parser.add_argument("--size", default="720x1280", help="Image size WxH (default: 720x1280 portrait)")
    parser.add_argument("--scene", type=int, default=None, help="Only generate for scene N (1-based)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("Please provide --api_key or set DASHSCOPE_API_KEY env var")

    with open(args.storyboard, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = data["scenes"]
    os.makedirs(args.output_dir, exist_ok=True)

    targets = []
    for s in scenes:
        if s.get("source") != "ai_generate":
            continue
        if not s.get("keyframe_prompt"):
            continue
        if args.scene is not None and s["id"] != args.scene:
            continue
        targets.append(s)

    if not targets:
        print("No scenes to generate (check source='ai_generate' and keyframe_prompt).")
        return

    url_map = {}

    print(f"Generating keyframes for {len(targets)} scene(s), {args.n} candidate(s) each...\n")

    for scene in targets:
        sid = scene["id"]
        prompt = scene["keyframe_prompt"]
        print(f"[Scene {sid}] {prompt[:60]}...")

        urls = generate_images(prompt, args.n, args.size, api_key)

        for j, url in enumerate(urls):
            suffix = SUFFIX_MAP.get(j, str(j))
            filename = f"scene_{sid:02d}_{suffix}.png"
            filepath = os.path.join(args.output_dir, filename)
            urllib.request.urlretrieve(url, filepath)
            url_map[filename] = url
            print(f"  -> {filename}")

    # Save URL mapping so generate_video_clips.py can use public URLs
    map_path = os.path.join(args.output_dir, "urls.json")
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(url_map, f, indent=2, ensure_ascii=False)

    print(f"\nDone! URL mapping saved to {map_path}")
    print("Review the keyframes and update storyboard.json 'selected_keyframe' with the chosen filename.")


if __name__ == "__main__":
    main()
