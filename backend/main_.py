"""메인 파이프라인 - 전체 비디오 생성 프로세스를 조율합니다."""

import os
import time
from typing import Dict, Optional

from pipeline.t2i_pipeline import t2i_pipe
from pipeline.tts_pipeline import tts_pipe
from pipeline.sync_pipeline import sync_pipe
from pipeline.render_pipeline import ren_pipe
from utils.text_normalizer import normalize_text
from utils.time_utils import format_hms


def full_pipeline(
    manuscript: str,
    manuscript_source: Optional[str] = None,
    tts_voice: Optional[str] = None,
    bgm_genre: Optional[str] = None,
    bgm_type: Optional[str] = None,
    tts_volume: Optional[int] = 100,
    tts_speed: Optional[int] = None,
    bgm_volume: Optional[int] = 30,
    video_ratio: Optional[str] = None,
    output_dir: Optional[str] = None,
    google_key_file: Optional[str] = None,
    font_path: Optional[str] = None,
    img_prompt_json: Optional[str] = None,
    img_size: str = "1536x1024",
    img_quality: str = "low",
) -> Dict[str, str]:
    """
    전체 비디오 생성 파이프라인
    
    각 파이프라인 스테이지를 순차적으로 호출하여 최종 비디오를 생성합니다.
    
    Args:
        manuscript: 원고 텍스트
        manuscript_source: 원고 출처 (선택사항, 현재 미사용)
        tts_voice: TTS 음성 이름 (선택사항)
        bgm_genre: BGM 장르 (선택사항)
        bgm_type: BGM 타입 (선택사항)
        tts_volume: TTS 볼륨 (0-100, 기본값: 100, 현재 미사용)
        tts_speed: TTS 속도 (0-100, 기본값: 100)
        bgm_volume: BGM 볼륨 (0-100, 기본값: 30)
        video_ratio: 비디오 해상도 (예: "1536x1024")
        output_dir: 출력 디렉터리
        google_key_file: GCP 키 파일 경로
        font_path: 폰트 파일 경로
        img_prompt_json: 이미지 프롬프트 JSON (선택사항)
        img_size: 이미지 크기 (기본값: "1536x1024")
        img_quality: 이미지 품질 (기본값: "low")
        
    Returns:
        생성된 파일 경로들을 담은 딕셔너리
    """
    print("🎚 TTS SPEED =", tts_speed)
    print("🔊 TTS VOLUME =", tts_volume)
    print("🎵 BGM VOLUME =", bgm_volume)

    total_start = time.time()

    # 출력 디렉터리 설정
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "outputs")
    output_dir = os.path.abspath(output_dir)

    # 텍스트 정규화
    txt_content = normalize_text(manuscript)
    if not txt_content:
        raise ValueError("manuscript가 비어있습니다.")

    # TTS 속도 변환 (100 → 1.0)
    tts_rate = (tts_speed or 100) / 100.0

    # 1) 이미지 생성 (T2I)
    print("\n▶ T2I 파이프라인 시작...")
    t2i_start = time.time()
    chapters, chapters_json_path = t2i_pipe(
        input_text=txt_content,
        output_dir=output_dir,
        img_prompt_json=img_prompt_json,
        img_size=img_size,
        img_quality=img_quality,
        total_start=total_start,
    )
    t2i_elapsed = time.time() - t2i_start
    print(f"✔ T2I 파이프라인 완료: {format_hms(t2i_elapsed)}")

    # 2) TTS + 자막 생성
    print("\n▶ TTS + 자막 파이프라인 시작...")
    tts_start = time.time()
    tts_audio_path, subtitle_json_path = tts_pipe(
        input_text=txt_content,
        output_dir=output_dir,
        google_key_file=google_key_file,
        voice_name=tts_voice,
        speaking_rate=tts_rate,
    )
    tts_elapsed = time.time() - tts_start
    print(f"✔ TTS + 자막 파이프라인 완료: {format_hms(tts_elapsed)}")

    # 3) BGM 믹싱
    print("\n▶ BGM 믹싱 파이프라인 시작...")
    sync_start = time.time()
    final_audio_path = sync_pipe(
        tts_audio_path=tts_audio_path,
        output_dir=output_dir,
        bgm_genre=bgm_genre,
        bgm_type=bgm_type,
        bgm_volume=bgm_volume or 0,
    )
    sync_elapsed = time.time() - sync_start
    print(f"✔ BGM 믹싱 파이프라인 완료: {format_hms(sync_elapsed)}")

    # 4) 최종 렌더링
    print("\n▶ 렌더링 파이프라인 시작...")
    render_start = time.time()
    output_video = ren_pipe(
        output_dir=output_dir,
        subtitle_json_path=subtitle_json_path,
        final_audio_path=final_audio_path,
        chapters_json_path=chapters_json_path,
        font_path=font_path,
        video_ratio=video_ratio,
    )
    render_elapsed = time.time() - render_start
    print(f"✔ 렌더링 파이프라인 완료: {format_hms(render_elapsed)}")

    total_elapsed = time.time() - total_start

    print("\n====================================")
    print("🎉 전체 파이프라인 완료")
    print("====================================")
    print(f"🖼 T2I 단계: {format_hms(t2i_elapsed)}")
    print(f"🎤 TTS + 자막 단계: {format_hms(tts_elapsed)}")
    print(f"🎧 BGM 믹싱 단계: {format_hms(sync_elapsed)}")
    print(f"🎬 렌더링 단계: {format_hms(render_elapsed)}")
    print(f"⏱ 전체 소요 시간: {format_hms(total_elapsed)}")
    print("====================================\n")

    return {
        "output_video": output_video,
        "chapters_json": chapters_json_path,
        "subtitle_json": subtitle_json_path,
        "tts_audio": tts_audio_path,
        "final_audio": final_audio_path,
    }


if __name__ == "__main__":
    # 로컬 테스트용
    import sys

    if len(sys.argv) > 1:
        txt_file = sys.argv[1]
        with open(txt_file, "r", encoding="utf-8") as f:
            manuscript = f.read()
    else:
        manuscript = "테스트 원고입니다."

    full_pipeline(
        manuscript=manuscript,
        output_dir="./outputs",
        google_key_file="./dg0188.json" if os.path.exists("./dg0188.json") else None,
        bgm_genre="nature",
        bgm_type="빗소리",
        bgm_volume=30,
    )
