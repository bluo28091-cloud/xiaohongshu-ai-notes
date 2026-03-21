#!/usr/bin/env python3
"""
Generate a slideshow video from images with transitions and optional background music.
Compatible with moviepy 2.x.
Usage:
    python generate_slideshow.py \
        --slides_dir ./slides/ \
        --output ./video.mp4 \
        --duration 4 \
        --transition fade \
        --music ./bgm.mp3
"""

import argparse
import glob
import os
import sys

from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_audioclips,
    concatenate_videoclips,
    vfx,
)


def build_slideshow(slides_dir, duration_per_slide, transition, target_size=(1080, 1440)):
    patterns = ["*.png", "*.jpg", "*.jpeg", "*.webp"]
    image_files = []
    for pat in patterns:
        image_files.extend(glob.glob(os.path.join(slides_dir, pat)))
    image_files.sort()

    if not image_files:
        print(f"Error: No images found in {slides_dir}")
        sys.exit(1)

    print(f"Found {len(image_files)} slides:")
    for f in image_files:
        print(f"  - {os.path.basename(f)}")

    fade_dur = min(0.5, duration_per_slide / 4) if transition == "fade" else 0

    clips = []
    for i, img_path in enumerate(image_files):
        clip = ImageClip(img_path, duration=duration_per_slide).resized(target_size)
        if transition == "fade":
            effects = []
            if i > 0:
                effects.append(vfx.CrossFadeIn(fade_dur))
            if i < len(image_files) - 1:
                effects.append(vfx.CrossFadeOut(fade_dur))
            if effects:
                clip = clip.with_effects(effects)
        clips.append(clip)

    if transition == "fade" and len(clips) > 1:
        return concatenate_videoclips(clips, padding=-fade_dur, method="compose")
    else:
        return concatenate_videoclips(clips, method="compose")


def add_background_music(video, music_path):
    if not os.path.exists(music_path):
        print(f"Warning: Music file not found: {music_path}, skipping BGM.")
        return video

    audio = AudioFileClip(music_path)

    if audio.duration < video.duration:
        loops_needed = int(video.duration / audio.duration) + 1
        audio = concatenate_audioclips([audio] * loops_needed)

    audio = audio.subclipped(0, video.duration).with_volume_scaled(0.3)
    return video.with_audio(audio)


def main():
    parser = argparse.ArgumentParser(description="Generate slideshow video from images")
    parser.add_argument("--slides_dir", required=True, help="Directory containing slide images")
    parser.add_argument("--output", required=True, help="Output video file path")
    parser.add_argument("--duration", type=float, default=4.0, help="Duration per slide in seconds (default: 4)")
    parser.add_argument("--transition", choices=["fade", "none"], default="fade", help="Transition type (default: fade)")
    parser.add_argument("--music", default=None, help="Path to background music file")
    parser.add_argument("--width", type=int, default=1080, help="Video width (default: 1080)")
    parser.add_argument("--height", type=int, default=1440, help="Video height (default: 1440)")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second (default: 24)")

    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    print(f"Building slideshow from: {args.slides_dir}")
    video = build_slideshow(
        args.slides_dir,
        args.duration,
        args.transition,
        target_size=(args.width, args.height),
    )

    if args.music:
        print(f"Adding background music: {args.music}")
        video = add_background_music(video, args.music)

    print(f"Rendering video to: {args.output}")
    video.write_videofile(
        args.output,
        fps=args.fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )
    print("Done!")


if __name__ == "__main__":
    main()
