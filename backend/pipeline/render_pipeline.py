"""비디오 렌더링 파이프라인 - 이미지, 오디오, 자막을 결합하여 최종 비디오를 생성합니다."""

import os
from typing import Optional

from utils.render import WIDTH, HEIGHT, run_final_merge


def _parse_resolution(resolution: str, fallback: tuple[int, int]) -> tuple[int, int]:
    """`123x456` 형태의 문자열을 (width, height) 튜플로 변환합니다."""
    try:
        width_str, height_str = resolution.lower().replace(" ", "").split("x")
        width_val, height_val = int(width_str), int(height_str)
        if width_val > 0 and height_val > 0:
            return width_val, height_val
    except Exception:
        pass
    return fallback


def ren_pipe(
    output_dir: str,
    subtitle_json_path: str,
    final_audio_path: str,
    chapters_json_path: str,
    font_path: Optional[str] = None,
    video_ratio: Optional[str] = None,
) -> str:
    """
    최종 비디오 렌더링 파이프라인
    
    이미지, 오디오, 자막을 결합하여 최종 비디오를 생성합니다.
    모든 경로 설정은 내부에서 처리됩니다.
    
    Args:
        output_dir: 출력 디렉터리 (절대 경로 권장, 이미지와 챕터 JSON이 여기에 있어야 함)
        subtitle_json_path: 자막 JSON 파일 경로
        final_audio_path: 최종 오디오 파일 경로 (TTS 또는 TTS+BGM)
        chapters_json_path: 챕터 JSON 파일 경로
        font_path: 폰트 파일 경로 (None이면 시스템 기본값 사용)
        video_ratio: 비디오 해상도 (예: "1536x1024", None이면 기본값 사용)
        
    Returns:
        생성된 비디오 파일 경로
    """
    # 출력 디렉터리 준비
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # 비디오 경로 설정
    output_video = os.path.join(output_dir, "final_synced_output.mp4")
    temp_raw_video = os.path.join(output_dir, "temp_raw_video.avi")
    
    # 폰트 경로 설정 (기본값)
    if font_path is None:
        font_path = (
            r"C:\Windows\Fonts\malgun.ttf"
            if os.name == "nt"
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        )
    
    # 해상도 파싱
    render_width, render_height = _parse_resolution(
        video_ratio or "1536x1024",
        fallback=(WIDTH, HEIGHT),
    )
    
    # 최종 비디오 렌더링
    run_final_merge(
        output_dir=output_dir,
        tts_audio_dir=os.path.join(output_dir, "tts_audio"),  # 호환성을 위해 유지
        output_video=output_video,
        temp_raw_video=temp_raw_video,
        subtitle_json_path=subtitle_json_path,
        final_audio_path=final_audio_path,
        generated_images_dir=output_dir,  # 이미지는 output_dir에 저장됨
        chapters_json_path=chapters_json_path,
        font_path=font_path,
        width=render_width,
        height=render_height,
    )
    
    return output_video
