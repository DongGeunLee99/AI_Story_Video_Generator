"""이미지 생성용 프롬프트 구성 및 저장 유틸리티"""

import base64
import json
import os
from typing import Any, Dict


def get_default_img_prompt() -> str:
    """기본 이미지 프롬프트 JSON 템플릿을 반환합니다."""
    default_prompt = {
        "task": "chapter_segmentation_with_visual_prompts",
        "description": "주어진 긴 서사 텍스트를 여러 개의 챕터로 구조화하여 나누고, 각 챕터마다 서사 요약과 이미지 생성을 위한 안전한 시각 메타 정보를 생성합니다.",
        "instructions": {
            "step_1": "제공된 전체 텍스트를 처음부터 끝까지 주의 깊게 읽습니다.",
            "step_2": "서사의 기승전결, 인물의 심리 변화, 장소 이동, 사건 전환, 분위기 변화 등 자연스러운 분기 지점을 식별합니다.",
            "step_3": "텍스트를 2~3개의 챕터로 나누되, 지나치게 세분화하지 않습니다.",
            "step_4": "각 챕터마다 아래 텍스트 관련 필드를 생성합니다.",
            "text_fields": {
                "chapter_number": "1부터 시작하는 순차적 번호. 정수로 표기합니다.",
                "chapter_title": "챕터의 핵심 주제나 분위기를 담은 간결한 한국어 제목.",
                "chapter_summary": "해당 챕터의 주요 사건과 서사를 5~7문장으로 요약합니다. 원문에 없는 내용을 추가하지 않습니다.",
                "chapter_start_sentence": "해당 챕터가 시작되는 원문의 첫 문장을 그대로 적습니다."
            },
            "step_5": "각 챕터마다 아래 이미지 프롬프트용 필드를 생성합니다. 모든 필드는 영어로 작성하며, 안전한 콘텐츠만 포함합니다.",
            "visual_fields": {
                "Era/Style": "서사의 시대감, 미술 스타일, 카메라 감각 등을 1~2문장으로 묘사합니다. 성적 암시가 가능한 표현은 절대 사용하지 않습니다.",
                "Scene": "챕터를 대표하는 하나의 장면을 1~2문장으로 설명합니다. 인물의 동작과 배치를 묘사하되, 신체적 노출 또는 성적 해석이 가능한 표현은 제외합니다.",
                "Environment": "배경, 조명, 기후, 공간감을 1~2문장으로 구체적으로 묘사합니다.",
                "Mood/Tone": "장면 전반의 감정적 분위기를 1문장 이상으로 묘사합니다.",
                "Symbolic_imagery": "상징적 모티프(예: 그림자, 바람, 문서, 도구 등)를 1문장 이상으로 설명합니다.",
                "Context_bleed": "정치적/심리적 긴장을 포함하되, 위험하거나 과도한 폭력·성적 맥락을 포함하지 않는 방식으로 1~2문장으로 묘사합니다.",
                "Output_requirements": "이미지 생성 시 안전한 조건을 명시합니다. 예: '1536x1024, high detail, cinematic depth of field, no nudity, no sexual content, no graphic violence, no text, restrained realism'"
            },
            "step_6": "모든 챕터는 동일한 구조와 일관된 서사 톤을 유지해야 합니다.",
            "step_7": "원문에 존재하지 않는 설정이나 사건, 인물, 결말 등을 임의로 추가하지 않습니다. 해석만 허용됩니다.",
            "step_8": "최종 출력은 'output_format'의 JSON 구조를 엄격히 따릅니다.",
            "step_9": "JSON 외에 여분의 설명 문장은 출력하지 않습니다."
        },
        "output_format": {
            "chapters": [
                {
                    "chapter_number": 1,
                    "chapter_title": "[string]",
                    "chapter_summary": "[string]",
                    "chapter_start_sentence": "[string]",
                    "Era/Style": "[English sentences]",
                    "Scene": "[English sentences]",
                    "Environment": "[English sentences]",
                    "Mood/Tone": "[English sentences]",
                    "Symbolic_imagery": "[English sentences]",
                    "Context_bleed": "[English sentences]",
                    "Output_requirements": "[English sentences]"
                }
            ]
        }
    }
    return json.dumps(default_prompt, ensure_ascii=False, indent=2)


def collect_meta_from_chapter(chapter: Dict[str, Any]) -> Dict[str, str]:
    """챕터 응답에서 이미지 프롬프트에 필요한 메타 필드를 추출합니다.

    Args:
        chapter: 모델 응답의 단일 챕터 딕셔너리.

    Returns:
        이미지 생성에 필요한 키만 모은 딕셔너리.
    """
    return {
        "Era/Style": chapter.get("Era/Style", ""),
        "Scene": chapter.get("Scene", ""),
        "Environment": chapter.get("Environment", ""),
        "Mood/Tone": chapter.get("Mood/Tone", ""),
        "Symbolic_imagery": chapter.get("Symbolic_imagery", ""),
        "Context_bleed": chapter.get("Context_bleed", ""),
        "Output_requirements": chapter.get("Output_requirements", ""),
    }


def build_prompt_from_meta(meta: Dict[str, str]) -> str:
    """챕터 메타 데이터를 이미지 생성용 프롬프트 문자열로 변환합니다.

    Args:
        meta: `collect_meta_from_chapter`에서 생성된 메타 데이터.

    Returns:
        사람이 읽기 쉬운 형태의 프롬프트 문자열.
    """
    return (
        f"[시대/스타일]: {meta.get('Era/Style', '')}\n"
        f"[장면]: {meta.get('Scene', '')}\n"
        f"[환경]: {meta.get('Environment', '')}\n"
        f"[무드/톤]: {meta.get('Mood/Tone', '')}\n"
        f"[상징 이미지]: {meta.get('Symbolic_imagery', '')}\n"
        f"[컨텍스트 블리드]: {meta.get('Context_bleed', '')}\n"
        f"[출력 요구사항]: {meta.get('Output_requirements', '')}"
    )


def generate_and_save_image(
    client: Any,
    prompt: str,
    save_dir: str,
    filename: str,
    size: str,
    quality: str,
) -> str:
    """OpenAI 이미지 API를 호출하여 이미지를 생성하고 디스크에 저장합니다.

    Args:
        client: OpenAI 이미지 생성을 위한 클라이언트 인스턴스.
        prompt: 이미지 생성에 사용할 텍스트 프롬프트.
        save_dir: 이미지 저장 디렉터리 경로.
        filename: 저장할 파일 이름.
        size: 생성 이미지 해상도 옵션 (예: `"1280x720"`).
        quality: 이미지 퀄리티 옵션 (예: `"low"`).

    Returns:
        생성된 이미지의 전체 파일 경로.
    """
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    print("size", size)

    result = client.images.generate(
        model="gpt-image-1-mini",
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )

    image_b64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_b64)

    with open(save_path, "wb") as f:
        f.write(image_bytes)

    return save_path

