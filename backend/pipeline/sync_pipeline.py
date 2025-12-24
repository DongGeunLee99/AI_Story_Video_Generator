"""BGM 동기화 및 믹싱 파이프라인 - TTS 오디오에 BGM을 믹싱합니다."""

import os
import subprocess
from typing import Optional

from utils.bgm_utils import get_bgm_path, volume_percent_to_db


def sync_pipe(
    tts_audio_path: str,
    output_dir: str,
    bgm_genre: Optional[str] = None,
    bgm_type: Optional[str] = None,
    bgm_volume: int = 0,
) -> str:
    """
    BGM 믹싱 파이프라인
    
    TTS 오디오에 BGM을 믹싱하여 최종 오디오를 생성합니다.
    BGM이 없거나 볼륨이 0이면 원본 TTS 오디오를 반환합니다.
    모든 경로 설정은 내부에서 처리됩니다.
    
    Args:
        tts_audio_path: TTS 오디오 파일 경로
        output_dir: 출력 디렉터리 (절대 경로 권장)
        bgm_genre: BGM 장르 (None이면 BGM 미사용)
        bgm_type: BGM 타입 (None이면 BGM 미사용)
        bgm_volume: BGM 볼륨 (0-100, 0이면 BGM 미사용)
        
    Returns:
        최종 오디오 파일 경로 (BGM이 있으면 믹싱된 파일, 없으면 TTS 파일)
    """
    # BGM이 없거나 볼륨이 0이면 원본 TTS 반환
    bgm_path = get_bgm_path(bgm_genre, bgm_type)
    if not bgm_path or bgm_volume <= 0:
        return tts_audio_path
    
    # 출력 디렉터리 준비
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # 믹싱된 오디오 경로 설정
    tts_audio_dir = os.path.join(output_dir, "tts_audio")
    os.makedirs(tts_audio_dir, exist_ok=True)
    mixed_audio_path = os.path.join(tts_audio_dir, "final_audio_with_bgm.m4a")
    
    # BGM 볼륨을 dB로 변환
    bgm_db = volume_percent_to_db(bgm_volume)
    
    # TTS + BGM 믹싱
    # BGM은 무한루프(-stream_loop -1)
    # duration=first → TTS 길이에 맞춰 자동 컷
    cmd = [
        "ffmpeg",
        "-y",
        "-i", tts_audio_path,
        "-stream_loop", "-1",
        "-i", bgm_path,
        "-filter_complex",
        f"[1:a]volume={bgm_db}dB[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2",
        "-c:a", "aac",
        "-b:a", "192k",
        mixed_audio_path,
    ]
    subprocess.run(cmd, check=True)
    
    print("🎧 BGM 믹싱 완료")
    return mixed_audio_path
