#!/usr/bin/env python3
"""
Generate video clips from keyframe images using DashScope VideoSynthesis (image-to-video).

Usage:
    python generate_video_clips.py \
        --storyboard storyboard.json \
        --output_dir video_clips/ \
        --api_key sk-xxx \
        --resolution 720P
"""

import argparse
import json
import os
import shutil
import urllib.request

import dashscope
from dashscope import VideoSynthesis

dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

MODEL = "wan2.6-i2v-flash"


def resolve_image_url(image_ref: str, keyframes_dir: str = None) -> str:
    """Resolve an image reference to a public URL for VideoSynthesis.
    
    Accepts: a URL, a filename (looked up in keyframes/urls.json), or a local path.
    """
    if image_ref.startswith("http://") or image_ref.startswith("https://"):
        return image_ref

    # Try to look up in urls.json from keyframes directory
    if keyframes_dir:
        urls_json = os.path.join(keyframes_dir, "urls.json")
        if os.path.exists(urls_json):
            with open(urls_json, "r") as f:
                url_map = json.load(f)
            basename = os.path.basename(image_ref)
            if basename in url_map:
                return url_map[basename]

    raise ValueError(
        f"Cannot resolve '{image_ref}' to a public URL. "
        "Use a URL, or ensure keyframes/urls.json contains the mapping."
    )


def generate_video_clip(
    img_url: str,
    prompt: str,
    duration: int,
    resolution: str,
    api_key: str,
) -> str:
    duration = max(2, min(15, int(duration)))

    print(f"    Calling VideoSynthesis (may take 1-3 min)...")
    rsp = VideoSynthesis.call(
        api_key=api_key,
        model=MODEL,
        prompt=prompt,
        img_url=img_url,
        resolution=resolution,
        duration=duration,
        prompt_extend=True,
    )

    if rsp.status_code != 200:
        raise RuntimeError(
            f"VideoSynthesis error {rsp.status_code}: {rsp.code} - {rsp.message}"
        )

    return rsp.output.video_url


def main():
    parser = argparse.ArgumentParser(description="Generate video clips from keyframe images")
    parser.add_argument("--storyboard", required=True, help="Path to storyboard.json")
    parser.add_argument("--output_dir", required=True, help="Output directory for video clips")
    parser.add_argument("--api_key", default=None, help="DashScope API key")
    parser.add_argument("--keyframes_dir", default=None, help="Directory with keyframe images and urls.json")
    parser.add_argument("--resolution", default="720P", help="Video resolution: 480P, 720P, 1080P")
    parser.add_argument("--scene", type=int, default=None, help="Only generate for scene N (1-based)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("Please provide --api_key or set DASHSCOPE_API_KEY env var")

    with open(args.storyboard, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = data["scenes"]
    os.makedirs(args.output_dir, exist_ok=True)

    for scene in scenes:
        sid = scene["id"]
        if args.scene is not None and sid != args.scene:
            continue

        output_path = os.path.join(args.output_dir, f"scene_{sid:02d}.mp4")
        source = scene.get("source", "ai_generate")

        if source == "user_upload":
            asset = scene.get("asset_path", "")
            if asset and os.path.exists(asset):
                if asset.lower().endswith((".mp4", ".mov", ".avi", ".webm")):
                    shutil.copy2(asset, output_path)
                    print(f"[Scene {sid}] Copied user video: {asset}")
                    continue
                else:
                    print(f"[Scene {sid}] User asset is an image, will generate video from it")
                    scene["selected_keyframe"] = asset
            else:
                print(f"[Scene {sid}] User asset not found: {asset}, skipping")
                continue

        keyframe = scene.get("selected_keyframe")
        if not keyframe:
            print(f"[Scene {sid}] No selected_keyframe set, skipping")
            continue

        prompt = scene.get("keyframe_prompt") or scene.get("description", "")
        duration = scene.get("duration", 5)

        try:
            img_url = resolve_image_url(keyframe, args.keyframes_dir)
        except ValueError as e:
            print(f"[Scene {sid}] {e}")
            continue

        print(f"[Scene {sid}] Generating video ({duration}s, {args.resolution})")
        print(f"    Keyframe: {keyframe}")
        print(f"    Prompt: {prompt[:60]}...")

        try:
            video_url = generate_video_clip(
                img_url=img_url,
                prompt=prompt,
                duration=duration,
                resolution=args.resolution,
                api_key=api_key,
            )
            urllib.request.urlretrieve(video_url, output_path)
            print(f"    -> {os.path.basename(output_path)} OK\n")
        except Exception as e:
            print(f"    ERROR: {e}\n")

    print("Done! Review the video clips before final assembly.")


if __name__ == "__main__":
    main()
