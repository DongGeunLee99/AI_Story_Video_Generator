"""Text-to-Image 파이프라인 - 텍스트를 챕터로 분할하고 각 챕터에 대한 이미지를 생성합니다."""

import json
import os
import time
from typing import Any, Dict, List, Optional

from utils.auth import get_openai_client
from utils.img_gen_prompt import (
    collect_meta_from_chapter,
    build_prompt_from_meta,
    generate_and_save_image,
    get_default_img_prompt,
)
from utils.time_utils import log_time_status


def t2i_pipe(
    input_text: str,
    output_dir: str,
    img_prompt_json: Optional[str] = None,
    img_size: str = "1536x1024",
    img_quality: str = "low",
    total_start: Optional[float] = None,
) -> tuple[List[Dict[str, Any]], str]:
    """
    Text-to-Image 파이프라인
    
    입력 텍스트를 챕터로 분할하고, 각 챕터에 대한 이미지를 생성합니다.
    모든 경로 설정과 클라이언트 초기화는 내부에서 처리됩니다.
    
    Args:
        input_text: 입력 텍스트
        output_dir: 출력 디렉터리 (절대 경로 권장)
        img_prompt_json: 이미지 프롬프트 JSON (None이면 기본값 사용)
        img_size: 이미지 크기 (기본값: "1536x1024")
        img_quality: 이미지 품질 (기본값: "low")
        total_start: 전체 시작 시간 (선택사항, 로깅용)
        
    Returns:
        (chapters, chapters_json_path) 튜플
        - chapters: 챕터 리스트
        - chapters_json_path: 챕터 JSON 파일 경로
    """
    if total_start is None:
        total_start = time.time()
    
    # 출력 디렉터리 준비
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # 이미지 프롬프트 설정
    if img_prompt_json is None:
        img_prompt_json = get_default_img_prompt()
    
    # OpenAI 클라이언트 초기화
    client = get_openai_client()
    
    # 챕터 JSON 경로 설정
    chapters_json_path = os.path.join(output_dir, "chapters_output.json")
    
    # 1) 모델 호출
    log_time_status(total_start, "모델 호출 시작")
    inference_input = img_prompt_json + "\n\n" + input_text
    
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=inference_input,
            timeout=300
        )
    except Exception:
        raise RuntimeError("Inference TIME_OUT")
    
    # 모델 응답 텍스트 추출 및 저장
    model_response_text = response.output_text[8:-3:]
    output_txt_path = os.path.join(output_dir, "model_response_output.txt")
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(model_response_text)
    print(f"✅ 모델 응답 텍스트 저장 완료: {output_txt_path}")
    log_time_status(total_start, "모델 호출 완료")
    
    # 2) JSON 파싱
    log_time_status(total_start, "JSON으로 변환 시작")
    import re
    
    # Responses API 구조에서 모든 text 수집
    text_chunks = []
    if hasattr(response, "output"):
        for msg in response.output:
            if hasattr(msg, "content"):
                for c in msg.content:
                    if hasattr(c, "text") and c.text:
                        text_chunks.append(c.text)
    
    if not text_chunks:
        raise ValueError("모델 응답에 텍스트가 없습니다.")
    
    raw_text = "\n".join(text_chunks).strip()
    
    # ```json 코드블록 제거
    raw_text = re.sub(r"```json\s*", "", raw_text, flags=re.IGNORECASE)
    raw_text = re.sub(r"\s*```", "", raw_text)
    
    # JSON 중괄호 블록 추출
    match = re.search(r"\{[\s\S]*\}", raw_text)
    if not match:
        raise ValueError(
            "모델 응답에서 JSON 블록을 찾을 수 없습니다.\n\n"
            f"원본 응답:\n{raw_text}"
        )
    
    json_text = match.group(0)
    
    # JSON 파싱
    try:
        story_json = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"JSON 파싱 실패: {e}\n\n"
            f"추출된 JSON:\n{json_text}"
        )
    
    log_time_status(total_start, "JSON으로 변환 완료")
    
    # 3) 챕터 처리
    log_time_status(total_start, "챕터 구분 시작")
    chapters = story_json.get("chapters", [])
    if not chapters:
        raise ValueError("챕터 데이터가 없습니다.")
    
    print(f"챕터 수: {len(chapters)}")
    os.makedirs(os.path.dirname(chapters_json_path), exist_ok=True)
    with open(chapters_json_path, "w", encoding="utf-8") as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)
    log_time_status(total_start, "챕터 구분 완료")
    
    # 4) 이미지 생성
    log_time_status(total_start, "이미지 생성 시작")
    for ch in chapters:
        meta = collect_meta_from_chapter(ch)
        prompt = build_prompt_from_meta(meta)
        filename = f"{ch['chapter_number']}_{ch.get('chapter_title', 'chapter')}.png"
        
        log_time_status(total_start, f"이미지 이름: {filename}")
        
        saved_path = generate_and_save_image(
            client,
            prompt,
            save_dir=output_dir,
            filename=filename,
            size=img_size,
            quality=img_quality
        )
        
        log_time_status(total_start, f"저장 완료: {saved_path}")
    
    log_time_status(total_start, "이미지 생성 완료")
    print("🖼 이미지 생성 완료")
    
    return chapters, chapters_json_path
