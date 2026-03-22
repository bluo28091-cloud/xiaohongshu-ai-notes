#!/usr/bin/env python3
"""
Generate narration audio and assemble final video from video clips + narration.

Supports two input modes:
  1. --storyboard + --clips_dir: reads scenes from storyboard.json, uses video clips
  2. --narration + --slides_dir: legacy mode, uses static slide images

Usage:
    # New workflow (video clips):
    python generate_narration.py \
        --storyboard storyboard.json \
        --clips_dir video_clips/ \
        --output final.mp4 \
        --api_key sk-xxx --voice Cherry --speed 1.5

    # Test single scene audio:
    python generate_narration.py \
        --storyboard storyboard.json \
        --api_key sk-xxx --voice Cherry --speed 1.5 --test 1

    # Legacy mode (static images):
    python generate_narration.py \
        --narration narration.json \
        --slides_dir slides/ \
        --output video.mp4 \
        --api_key sk-xxx
"""

import argparse
import glob
import json
import os
import subprocess
import tempfile
import urllib.request

import dashscope
from moviepy import (
    AudioFileClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
    vfx,
)

dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

MODEL = "qwen3-tts-instruct-flash"
DEFAULT_VOICE = "Cherry"
DEFAULT_INSTRUCTIONS = "语速适中偏快，语调自然活泼，像一位科技博主在分享好物。"
DEFAULT_SPEED = 1.5


def _get_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def speed_up_audio(input_path: str, output_path: str, speed: float):
    if abs(speed - 1.0) < 0.01:
        if input_path != output_path:
            os.replace(input_path, output_path)
        return
    subprocess.run(
        [_get_ffmpeg(), "-y", "-i", input_path, "-filter:a", f"atempo={speed}",
         "-vn", output_path],
        capture_output=True, check=True,
    )


def generate_slide_audio(
    text: str, output_path: str, api_key: str,
    voice: str = DEFAULT_VOICE,
    instructions: str = DEFAULT_INSTRUCTIONS,
    speed: float = DEFAULT_SPEED,
):
    response = dashscope.MultiModalConversation.call(
        model=MODEL,
        api_key=api_key,
        text=text,
        voice=voice,
        language_type="Chinese",
        instructions=instructions,
        optimize_instructions=True,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Qwen3-TTS API error {response.status_code}: "
            f"{response.code} - {response.message}"
        )

    audio_url = response.output.audio.url
    if abs(speed - 1.0) < 0.01:
        urllib.request.urlretrieve(audio_url, output_path)
    else:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        urllib.request.urlretrieve(audio_url, tmp_path)
        speed_up_audio(tmp_path, output_path, speed)
        os.unlink(tmp_path)
    print(f"  -> {os.path.basename(output_path)} OK ({speed}x)")


def generate_all_audio(narrations: list, output_dir: str, api_key: str,
                       voice: str = DEFAULT_VOICE,
                       instructions: str = DEFAULT_INSTRUCTIONS,
                       speed: float = DEFAULT_SPEED):
    os.makedirs(output_dir, exist_ok=True)
    audio_files = []
    for i, item in enumerate(narrations):
        text = item["text"] if isinstance(item, dict) else item
        path = os.path.join(output_dir, f"narration_{i + 1:02d}.wav")
        print(f"[{i + 1}/{len(narrations)}] Generating: {text[:30]}...")
        generate_slide_audio(text, path, api_key, voice, instructions, speed)
        audio_files.append(path)
    return audio_files


def build_video_from_clips(
    clip_paths: list, audio_files: list, output_path: str, padding: float = 0.3,
):
    """Assemble final video from video clips + narration audio."""
    clips = []
    for clip_path, audio_path in zip(clip_paths, audio_files):
        audio = AudioFileClip(audio_path)
        video = VideoFileClip(clip_path)

        # Match video duration to audio: trim or loop
        target_dur = audio.duration + padding
        if video.duration >= target_dur:
            video = video.subclipped(0, target_dur)
        else:
            # Loop the video to fill narration duration
            loops_needed = int(target_dur / video.duration) + 1
            video = concatenate_videoclips([video] * loops_needed).subclipped(0, target_dur)

        video = video.with_audio(audio)
        clips.append(video)

    fade_dur = 0.3
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
        output_path, fps=24, codec="libx264", audio_codec="aac",
        threads=4, preset="medium",
    )
    print(f"Done! Final video saved to {output_path}")


def build_video_from_images(
    image_paths: list, audio_files: list, output_path: str, padding: float = 0.8,
):
    """Legacy: assemble video from static images + narration audio."""
    clips = []
    for img_path, audio_path in zip(image_paths, audio_files):
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
        output_path, fps=24, codec="libx264", audio_codec="aac",
        threads=4, preset="medium",
    )
    print(f"Done! Final video saved to {output_path}")


def load_narrations_from_storyboard(storyboard_path: str) -> list:
    with open(storyboard_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [{"text": s["narration"], "id": s["id"]} for s in data["scenes"]]


def main():
    parser = argparse.ArgumentParser(description="Generate narration and assemble final video")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--storyboard", help="Path to storyboard.json (new workflow)")
    group.add_argument("--narration", help="Path to narration.json (legacy)")
    parser.add_argument("--clips_dir", default=None, help="Directory with video clips (new workflow)")
    parser.add_argument("--slides_dir", default=None, help="Directory with slide images (legacy)")
    parser.add_argument("--output", default=None, help="Output video path")
    parser.add_argument("--audio_dir", default=None, help="Directory to save audio files")
    parser.add_argument("--api_key", default=None, help="DashScope API key")
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--instructions", default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--speed", type=float, default=DEFAULT_SPEED)
    parser.add_argument("--test", type=int, default=None, metavar="N",
                        help="Only generate audio for scene N (1-based), skip video")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("Please provide --api_key or set DASHSCOPE_API_KEY env var")

    # Load narrations
    if args.storyboard:
        narrations = load_narrations_from_storyboard(args.storyboard)
        base_dir = os.path.dirname(args.storyboard)
    else:
        with open(args.narration, "r", encoding="utf-8") as f:
            narrations = json.load(f)
        base_dir = os.path.dirname(args.narration)

    audio_dir = args.audio_dir or (
        os.path.join(os.path.dirname(args.output), "audio") if args.output
        else os.path.join(base_dir, "audio")
    )

    # Test mode
    if args.test is not None:
        idx = args.test - 1
        if idx < 0 or idx >= len(narrations):
            raise ValueError(f"--test {args.test} out of range (1-{len(narrations)})")
        os.makedirs(audio_dir, exist_ok=True)
        item = narrations[idx]
        text = item["text"] if isinstance(item, dict) else item
        path = os.path.join(audio_dir, f"test_scene_{args.test:02d}.wav")
        print(f"[TEST] Scene {args.test}: {text[:40]}...")
        print(f"  Voice: {args.voice} | Speed: {args.speed}x")
        print(f"  Instructions: {args.instructions}")
        generate_slide_audio(text, path, api_key, args.voice, args.instructions, args.speed)
        print(f"\nTest audio saved to: {path}")
        return

    # Generate all audio
    print(f"Generating {len(narrations)} narration clips via Qwen3-TTS")
    print(f"  Voice: {args.voice} | Speed: {args.speed}x")
    audio_files = generate_all_audio(
        narrations, audio_dir, api_key, args.voice, args.instructions, args.speed,
    )
    print("Audio generation complete!\n")

    if not args.output:
        print("No --output provided, skipping video assembly.")
        return

    # Assemble video
    if args.clips_dir:
        clip_files = sorted(glob.glob(os.path.join(args.clips_dir, "*.mp4")))
        if len(clip_files) != len(audio_files):
            print(f"Warning: {len(clip_files)} clips but {len(audio_files)} narrations. Using min.")
            count = min(len(clip_files), len(audio_files))
            clip_files = clip_files[:count]
            audio_files = audio_files[:count]
        print(f"Assembling {len(clip_files)} video clips with narration...")
        build_video_from_clips(clip_files, audio_files, args.output)

    elif args.slides_dir:
        slide_images = sorted(glob.glob(os.path.join(args.slides_dir, "*.png")))
        if len(slide_images) != len(audio_files):
            print(f"Warning: {len(slide_images)} slides but {len(audio_files)} narrations. Using min.")
            count = min(len(slide_images), len(audio_files))
            slide_images = slide_images[:count]
            audio_files = audio_files[:count]
        print(f"Assembling {len(slide_images)} slides with narration...")
        build_video_from_images(slide_images, audio_files, args.output)

    else:
        print("No --clips_dir or --slides_dir provided, skipping video assembly.")
        print("Audio files are saved in:", audio_dir)


if __name__ == "__main__":
    main()
