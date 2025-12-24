"""Modal 서버리스 함수로 래핑된 비디오 생성 파이프라인
- 오로지 Modal 관련 기능만 포함
"""

import os
import sys
import modal
import tempfile
import base64
from pathlib import Path
from typing import Dict, Optional

# ------------------------------------------------------------------------------------
# 1) backend 경로 설정
# ------------------------------------------------------------------------------------

backend_dir = Path(__file__).parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

sys.path.insert(0, "/root/backend")

# ------------------------------------------------------------------------------------
# 2) Modal App
# ------------------------------------------------------------------------------------

app = modal.App("video-generation-pipeline")

# ------------------------------------------------------------------------------------
# 3) Modal Image (CUDA / NVENC 전제)
# ------------------------------------------------------------------------------------

image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.2.0-runtime-ubuntu22.04",
        add_python="3.11",
    )
    .apt_install(
        "ffmpeg",
        "libgl1",
        "fonts-dejavu-core",
        "fonts-noto-cjk",
        "fontconfig",
    )
    .pip_install(
        "openai==2.8.1",
        "google-cloud-texttospeech==2.33.0",
        "moviepy==1.0.3",
        "numpy==1.26.4",
        "Pillow==10.1.0",
        "python-dotenv==1.0.1",
        "fastapi[standard]",
    )
    .add_local_dir(backend_dir, "/root/backend", copy=True)
)

# ------------------------------------------------------------------------------------
# 4) backend import
# ------------------------------------------------------------------------------------

from main_ import full_pipeline

# ------------------------------------------------------------------------------------
# 5) create_video
# ------------------------------------------------------------------------------------

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("openai-secret"),
        modal.Secret.from_name("gcp-secret"),
    ],
    gpu=modal.gpu.A10G(),
    timeout=3600,
)
def create_video(
    manuscript: str,
    manuscript_source: Optional[str] = None,
    tts_voice: Optional[str] = None,
    bgm_genre: Optional[str] = None,
    bgm_type: Optional[str] = None,
    tts_volume: Optional[int] = 100,
    tts_speed: Optional[int] = None,
    bgm_volume: Optional[int] = 30,
    video_ratio: Optional[str] = None,
    img_size: str = "1536x1024",
    img_quality: str = "low",
) -> Dict[str, str]:

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, "outputs")
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        result = full_pipeline(
            manuscript=manuscript,
            manuscript_source=manuscript_source,
            tts_voice=tts_voice,
            bgm_genre=bgm_genre,
            bgm_type=bgm_type,
            tts_volume=tts_volume,
            tts_speed=tts_speed,
            bgm_volume=bgm_volume,
            video_ratio=video_ratio,
            output_dir=output_dir,
            font_path=font_path,
            img_size=img_size,
            img_quality=img_quality,
        )

        response = {
            "output_video_path": result["output_video"],
            "chapters_json_path": result["chapters_json"],
            "subtitle_json_path": result["subtitle_json"],
            "final_audio_path": result["final_audio"],
        }

        if os.path.exists(result["output_video"]):
            with open(result["output_video"], "rb") as f:
                video_data = f.read()
                response["output_video_base64"] = base64.b64encode(video_data).decode()
                response["output_video_size"] = len(video_data)

        return response

# ------------------------------------------------------------------------------------
# 6) Web Endpoint (Next.js)
# ------------------------------------------------------------------------------------

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("openai-secret"),
        modal.Secret.from_name("gcp-secret"),
    ],
    gpu=modal.gpu.A10G(),
    timeout=3600,
)
@modal.web_endpoint(method="POST")
def web_create_video(request: Dict) -> Dict:
    """Modal 웹 엔드포인트: 비디오 생성"""
    try:
        manuscript = request.get("manuscript")
        if not manuscript:
            return {"status": "error", "error": "manuscript 필드가 필요합니다."}

        result = create_video.remote(
            manuscript=manuscript,
            manuscript_source=request.get("manuscript_source"),
            tts_voice=request.get("tts_voice"),
            bgm_genre=request.get("bgm_genre"),
            bgm_type=request.get("bgm_type"),
            tts_volume=request.get("tts_volume", 100),
            tts_speed=request.get("tts_speed"),
            bgm_volume=request.get("bgm_volume", 30),
            video_ratio=request.get("video_ratio"),
            img_size=request.get("img_size", "1536x1024"),
            img_quality=request.get("img_quality", "low"),
        )

        return {"status": "success", "result": result}

    except Exception as e:
        return {"status": "error", "error": str(e)}

# ------------------------------------------------------------------------------------
# 7) 로컬 테스트
# ------------------------------------------------------------------------------------

if __name__ == "__main__":
    with app.run():
        print(create_video.remote(manuscript="테스트 원고입니다."))

