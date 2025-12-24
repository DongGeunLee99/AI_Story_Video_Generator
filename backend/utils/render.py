"""비디오 렌더링 유틸리티"""

import json
import os
import subprocess
from moviepy.editor import AudioFileClip

FFMPEG = "ffmpeg"
FPS = 8
WIDTH = 960
HEIGHT = 540


def subtitle_json_to_ass(subs, ass_path):
    """자막 JSON을 ASS 형식으로 변환합니다."""
    def fmt(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = t % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("""[Script Info]
ScriptType: v4.00+.

[V4+ Styles]
Style: Default,Noto Sans CJK KR,48,&H00FFFFFF,&H00000000,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,0,2,10,10,10,1

[Events]
""")
        for s in subs:
            f.write(
                f"Dialogue: 0,{fmt(s['start'])},{fmt(s['end'])},Default,,0,0,0,,{s['text']}\n"
            )


def run_final_merge(
    output_dir,
    tts_audio_dir,            # 유지 (기존 인터페이스 호환)
    output_video,
    temp_raw_video,
    subtitle_json_path,
    final_audio_path,         # 최종 오디오 (TTS-only or TTS+BGM)
    generated_images_dir,
    chapters_json_path,
    font_path,
    width,
    height,
):
    """최종 비디오 렌더링을 수행합니다."""
    os.makedirs(output_dir, exist_ok=True)

    # ---------- 자막 ----------
    with open(subtitle_json_path, "r", encoding="utf-8") as f:
        subs = json.load(f)

    ass_path = os.path.join(output_dir, "subtitle.ass")
    subtitle_json_to_ass(subs, ass_path)

    # ---------- 오디오 길이 (최종 오디오 기준) ----------
    audio = AudioFileClip(final_audio_path)
    total_duration = audio.duration
    audio.close()

    # ---------- 챕터 ----------
    with open(chapters_json_path, "r", encoding="utf-8") as f:
        chapters = json.load(f)

    chapter_count = len(chapters)
    chapter_duration = total_duration / chapter_count

    # ---------- ffmpeg 입력 ----------
    cmd = [FFMPEG, "-y"]

    # 챕터별 이미지
    for i, ch in enumerate(chapters):
        img = f"{i+1}_{ch['chapter_title']}.png"
        img_path = os.path.join(generated_images_dir, img)
        cmd += ["-loop", "1", "-i", img_path]

    # 최종 오디오 (TTS-only or TTS+BGM)
    cmd += ["-i", final_audio_path]

    # ---------- filter_complex ----------
    filters = []

    # 1️⃣ 첫 이미지: 베이스
    filters.append(
        f"[0:v]scale={width}:{height},format=yuv420p[base]"
    )

    # 2️⃣ 나머지 이미지: 시간 조건 overlay
    for i in range(1, chapter_count):
        start = i * chapter_duration
        end = (i + 1) * chapter_duration
        filters.append(
            f"[base][{i}:v]overlay="
            f"enable='between(t,{start},{end})'[base]"
        )

    # 3️⃣ 자막
    filter_complex = ";".join(filters) + f";[base]subtitles={ass_path}[v]"

    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", f"{chapter_count}:a",
        "-c:v", "h264_nvenc",
        "-preset", "p4",
        "-cq", "18",
        "-c:a", "aac",
        "-shortest",
        output_video,
    ]

    subprocess.run(cmd, check=True)

