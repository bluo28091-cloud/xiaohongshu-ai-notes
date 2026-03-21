#!/usr/bin/env python3
"""
Generate narration audio for each slide using edge-tts,
then combine narration with slideshow video using moviepy.

Usage:
    python generate_narration.py \
        --narration narration.json \
        --video input.mp4 \
        --output output.mp4
"""

import argparse
import asyncio
import json
import os
import tempfile

import edge_tts
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    ImageClip,
    concatenate_audioclips,
    concatenate_videoclips,
    vfx,
)


VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "-5%"


async def generate_slide_audio(text: str, output_path: str):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(output_path)


async def generate_all_audio(narrations: list[dict], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    tasks = []
    for i, item in enumerate(narrations):
        path = os.path.join(output_dir, f"narration_{i + 1:02d}.mp3")
        tasks.append(generate_slide_audio(item["text"], path))
    await asyncio.gather(*tasks)
    return [os.path.join(output_dir, f"narration_{i + 1:02d}.mp3") for i in range(len(narrations))]


def build_narrated_video(slide_images: list[str], audio_files: list[str], output_path: str, padding: float = 0.8):
    clips = []
    for img_path, audio_path in zip(slide_images, audio_files):
        audio = AudioFileClip(audio_path)
        duration = audio.duration + padding
        clip = ImageClip(img_path, duration=duration).with_audio(audio)
        clips.append(clip)

    fade_dur = 0.4
    for i in range(len(clips)):
        effects = []
        if i > 0:
            effects.append(vfx.CrossFadeIn(fade_dur))
        if i < len(clips) - 1:
            effects.append(vfx.CrossFadeOut(fade_dur))
        if effects:
            clips[i] = clips[i].with_effects(effects)

    video = concatenate_videoclips(clips, padding=-fade_dur, method="compose")

    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )
    print(f"Done! Narrated video saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate narrated slideshow video")
    parser.add_argument("--narration", required=True, help="JSON file with narration texts")
    parser.add_argument("--slides_dir", required=True, help="Directory with slide images")
    parser.add_argument("--output", required=True, help="Output video path")
    parser.add_argument("--audio_dir", default=None, help="Directory to save audio files")
    parser.add_argument("--voice", default=VOICE, help=f"TTS voice (default: {VOICE})")
    args = parser.parse_args()

    with open(args.narration, "r", encoding="utf-8") as f:
        narrations = json.load(f)

    audio_dir = args.audio_dir or os.path.join(os.path.dirname(args.output), "audio")

    print(f"Generating {len(narrations)} narration clips with voice: {args.voice}")
    audio_files = asyncio.run(generate_all_audio(narrations, audio_dir))
    print("Audio generation complete!")

    import glob
    slide_images = sorted(glob.glob(os.path.join(args.slides_dir, "*.png")))

    if len(slide_images) != len(audio_files):
        print(f"Warning: {len(slide_images)} slides but {len(audio_files)} narrations. Using min.")
        count = min(len(slide_images), len(audio_files))
        slide_images = slide_images[:count]
        audio_files = audio_files[:count]

    print(f"Building narrated video with {len(slide_images)} slides...")
    build_narrated_video(slide_images, audio_files, args.output)


if __name__ == "__main__":
    main()
