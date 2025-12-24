"""TTS 파이프라인 - 텍스트를 음성으로 변환하고 자막 타이밍 정보를 생성합니다."""

import os
from typing import Optional

from utils.auth import setup_gcp_credentials
from utils.tts_utils import generate_tts_and_subtitle


def tts_pipe(
    input_text: str,
    output_dir: str,
    google_key_file: Optional[str] = None,
    voice_name: Optional[str] = None,
    speaking_rate: float = 1.0,
) -> tuple[str, str]:
    """
    TTS 및 자막 생성 파이프라인
    
    입력 텍스트를 음성으로 변환하고, 자막 타이밍 정보를 생성합니다.
    모든 경로 설정과 GCP 인증은 내부에서 처리됩니다.
    
    Args:
        input_text: 입력 텍스트
        output_dir: 출력 디렉터리 (절대 경로 권장)
        google_key_file: GCP 키 파일 경로 (None이면 환경변수에서 읽음)
        voice_name: TTS 음성 이름 (None이면 기본값 사용)
        speaking_rate: 말하기 속도 (기본값: 1.0)
        
    Returns:
        (tts_audio_path, subtitle_json_path) 튜플
        - tts_audio_path: 생성된 TTS 오디오 파일 경로
        - subtitle_json_path: 생성된 자막 JSON 파일 경로
    """
    # 출력 디렉터리 준비
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # TTS 오디오 및 자막 경로 설정
    tts_audio_dir = os.path.join(output_dir, "tts_audio")
    tts_output_path = os.path.join(tts_audio_dir, "final_combined_audio.mp3")
    subtitle_json_path = os.path.join(output_dir, "stt_subtitle_data.json")
    
    # GCP 인증 설정
    setup_gcp_credentials(key_file=google_key_file)
    
    # TTS 및 자막 생성 (GCP 인증은 이미 설정됨)
    generate_tts_and_subtitle(
        input_text=input_text,
        tts_audio_dir=tts_audio_dir,
        tts_output_path=tts_output_path,
        subtitle_json_path=subtitle_json_path,
        google_key_file=None,  # 호환성을 위해 전달하지만 사용되지 않음
        voice_name=voice_name,
        speaking_rate=speaking_rate,
    )
    
    return tts_output_path, subtitle_json_path
