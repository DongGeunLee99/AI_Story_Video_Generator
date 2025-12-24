"""BGM 관련 유틸리티"""

import os
from typing import Optional
from pathlib import Path


def get_bgm_base_dir() -> str:
    """
    BGM mp3 파일들이 존재하는 디렉터리.
    - Modal 환경: /root/backend/assets/bgm
    - 로컬 환경: (현재 파일 기준) ../backend/assets/bgm
    - 환경변수 BGM_DIR 로 오버라이드 가능
    """
    # Modal 환경 체크
    if os.path.exists("/root/backend/assets/bgm"):
        default_dir = "/root/backend/assets/bgm"
    else:
        # 로컬 환경
        here = Path(__file__).resolve().parent.parent.parent / "backend" / "assets" / "bgm"
        default_dir = str(here)
    
    return os.environ.get("BGM_DIR", default_dir)


def get_bgm_path(bgm_genre: Optional[str], bgm_type: Optional[str]) -> Optional[str]:
    """
    프론트에서 오는 (bgmGenre, bgmType)를 실제 mp3 파일 경로로 매핑.
    - none: None 반환
    - nature: 한글 타입명 매핑
    - 그 외: bgm_{genre}_{type}.mp3 (소문자)
    """
    if not bgm_genre or bgm_genre == "none":
        return None

    base_dir = get_bgm_base_dir()

    if bgm_genre == "nature":
        mapping = {
            "빗소리": "bgm_ambient_rain.mp3",
            "모닥불 소리": "bgm_ambient_fireplace.mp3",
            "시냇물 소리": "bgm_ambient_stream.mp3",
            "풀벌레 소리": "bgm_ambient_crickets.mp3",
        }
        filename = mapping.get(bgm_type or "")
    else:
        # 예: bright + A => bgm_bright_a.mp3
        if not bgm_type:
            return None
        filename = f"bgm_{bgm_genre}_{bgm_type}".lower() + ".mp3"

    if not filename:
        return None

    full_path = os.path.join(base_dir, filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError(
            f"BGM 파일을 찾을 수 없습니다: {full_path}\n"
            f"→ BGM_DIR={base_dir} 경로에 파일이 있는지 확인하세요."
        )
    return full_path


def volume_percent_to_db(percent: int) -> float:
    """
    0~100(퍼센트) → dB 변환 (ffmpeg volume 필터용)
    - 0 이하면 -60dB (사실상 무음)
    - 100 이면 0dB
    """
    if percent <= 0:
        return -60.0
    # -30dB ~ 0dB 스케일 (추천 범위: 25~35% ≈ -22~-20dB)
    return -30.0 + (percent / 100.0) * 30.0

