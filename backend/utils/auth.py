"""통합 인증 모듈 - OpenAI 및 GCP 인증을 중앙에서 관리합니다."""

import os
from typing import Optional
from openai import OpenAI
from google.cloud import texttospeech_v1beta1 as texttospeech
from dotenv import load_dotenv

load_dotenv()

# GCP 인증 관련 상수
GCP_KEY_PATH = "/root/.gcp/service_account.json"


def setup_gcp_credentials(key_file: Optional[str] = None) -> str:
    """GCP 인증을 설정하고 키 파일 경로를 반환합니다.
    
    Modal 환경에서는 환경변수에서 읽어서 파일로 저장하고,
    로컬 환경에서는 직접 경로를 사용합니다.
    
    Args:
        key_file: GCP 키 파일 경로 (선택사항)
        
    Returns:
        GCP 키 파일 경로
        
    Raises:
        RuntimeError: GCP 인증 정보가 설정되지 않은 경우
        FileNotFoundError: 키 파일이 존재하지 않는 경우
    """
    # Modal 환경: 환경변수에서 JSON 문자열 읽기
    gcp_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if gcp_json and not os.path.exists(gcp_json):
        # 환경변수가 JSON 문자열인 경우 (Modal Secret)
        os.makedirs("/root/.gcp", exist_ok=True)
        if not os.path.exists(GCP_KEY_PATH):
            with open(GCP_KEY_PATH, "w") as f:
                f.write(gcp_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH
        return GCP_KEY_PATH
    
    # 로컬 환경 또는 이미 파일 경로가 설정된 경우
    if key_file:
        key_path = os.path.abspath(key_file)
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"GCP 키 파일 없음: {key_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
        return key_path
    
    # 환경변수에 이미 경로가 설정된 경우
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    
    raise RuntimeError("GCP Secret(GOOGLE_APPLICATION_CREDENTIALS)가 설정되지 않았습니다.")


def get_openai_client() -> OpenAI:
    """OpenAI 클라이언트 인스턴스를 반환합니다.
    
    환경 변수 `T2I_APP_API_KEY`에서 API 키를 읽어 사용합니다.
    
    Returns:
        OpenAI: 인증된 OpenAI 클라이언트
        
    Raises:
        ValueError: API 키가 설정되지 않은 경우
    """
    api_key = os.getenv("T2I_APP_API_KEY")
    if not api_key:
        raise ValueError("환경변수 T2I_APP_API_KEY가 설정되어 있지 않습니다.")
    
    return OpenAI(api_key=api_key)


def get_tts_client() -> texttospeech.TextToSpeechClient:
    """Google Cloud Text-to-Speech 클라이언트 인스턴스를 반환합니다.
    
    Returns:
        texttospeech.TextToSpeechClient: TTS 클라이언트
    """
    return texttospeech.TextToSpeechClient()

