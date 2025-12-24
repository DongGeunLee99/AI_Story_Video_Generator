"""TTS 관련 유틸리티"""

import json
import os
import re
from typing import Any, Dict, List, Tuple

from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.editor import AudioFileClip
from google.cloud import texttospeech_v1beta1 as texttospeech

from utils.auth import get_tts_client

# 설정 상수
VOICE_NAME = "ko-KR-Wavenet-C"
MAX_SUBTITLE_CHARS = 24
FPS = 24


def split_sentences(text: str) -> List[str]:
    """
    이미 normalize_text()를 거친 텍스트를
    문장 단위로 분리한다.

    - 한국어 / 영어 공통
    - 마침표(.), 느낌표(!), 물음표(?) 기준
    - 따옴표(" ") 포함 처리
    """
    pattern = r'([\.!?][""]?)'
    parts = re.split(pattern, text)

    sentences: List[str] = []

    for i in range(0, len(parts) - 1, 2):
        sentence = (parts[i] + parts[i + 1]).strip()
        if sentence:
            sentences.append(sentence)

    # 끝에 구두점 없는 마지막 문장 처리
    if len(parts) % 2 == 1:
        tail = parts[-1].strip()
        if tail:
            sentences.append(tail)

    return sentences


def chunk_text_by_bytes(text: str, max_bytes: int = 3000) -> List[str]:
    """UTF-8 바이트 길이를 기준으로 텍스트를 여러 청크로 나눕니다."""
    sentences = split_sentences(text)
    chunks: List[str] = []
    current = ""

    for sentence in sentences:
        candidate = (current + " " + sentence).strip()
        if len(candidate.encode("utf-8")) > max_bytes and current:
            chunks.append(current)
            current = sentence
        else:
            current = candidate

    if current:
        chunks.append(current)
    return chunks


def quantize_time(sec: float, fps: int = FPS) -> float:
    """FPS 단위로 시간을 양자화합니다."""
    return round(sec * fps) / fps


def split_segment_by_length(seg: Dict[str, Any], max_chars: int) -> List[Dict[str, Any]]:
    """길이가 너무 긴 한 세그먼트를 여러 줄로 분할합니다."""
    text, start, end = seg["text"], seg["start"], seg["end"]
    duration = max(end - start, 0.1)

    if len(text) <= max_chars:
        return [seg]

    tokens = text.split()
    chunks: List[str] = []
    current = ""
    for token in tokens:
        candidate = (current + " " + token).strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = token
        else:
            current = token if not current else candidate

    if current:
        chunks.append(current)

    if len(chunks) == 1 and len(chunks[0]) > max_chars:
        large_text = chunks[0]
        chunks = [
            large_text[index : index + max_chars]
            for index in range(0, len(large_text), max_chars)
        ]

    total_chars = sum(len(chunk) for chunk in chunks)
    results: List[Dict[str, Any]] = []
    current_time = start

    for index, chunk_text in enumerate(chunks):
        if index == len(chunks) - 1:
            next_start, next_end = current_time, end
        else:
            ratio = len(chunk_text) / total_chars
            delta = duration * ratio
            next_start, next_end = current_time, current_time + delta

        results.append(
            {
                "text": chunk_text,
                "start": quantize_time(next_start),
                "end": quantize_time(next_end),
            }
        )
        current_time = next_end

    return results


def synthesize_chunk(
    client,
    chunk_text: str,
    chunk_index: int,
    offset: float,
    tts_audio_dir: str,
    voice_name: str,
    speaking_rate: float,
) -> Tuple[float, List[Dict[str, Any]]]:
    """SSML `<mark>`를 사용해 청크 단위 TTS를 생성합니다."""
    sentences = split_sentences(chunk_text)
    if not sentences:
        return 0.0, []

    ssml_parts = ["<speak>"]
    marks: List[Tuple[str, str]] = []

    for index, sentence in enumerate(sentences):
        name = f"c{chunk_index}_s{index}"
        marks.append((name, sentence))
        ssml_parts.append(
            f"<mark name='{name}'/>{sentence}<break time='0.8s'/>"
        )

    ssml_parts.append("</speak>")
    ssml_str = "".join(ssml_parts)

    request = texttospeech.SynthesizeSpeechRequest(
        input=texttospeech.SynthesisInput(ssml=ssml_str),
        voice=texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        ),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
        ),
        enable_time_pointing=[
            texttospeech.SynthesizeSpeechRequest.TimepointType.SSML_MARK
        ],
    )

    try:
        response = client.synthesize_speech(request=request)
    except Exception as exc:
        print(f"❌ TTS 실패: {exc}")
        return 0.0, []

    os.makedirs(tts_audio_dir, exist_ok=True)
    out_path = os.path.join(tts_audio_dir, f"chunk_{chunk_index}.mp3")

    with open(out_path, "wb") as file:
        file.write(response.audio_content)

    clip = AudioFileClip(out_path)
    duration = clip.duration
    clip.close()

    time_map = {tp.mark_name: float(tp.time_seconds) for tp in response.timepoints}

    segments: List[Dict[str, Any]] = []
    for name, sent_text in marks:
        if name not in time_map:
            continue
        start = quantize_time(offset + time_map[name])
        segments.append({"text": sent_text.strip(), "start": start})

    segments.sort(key=lambda item: item["start"])

    for index, segment in enumerate(segments):
        if index < len(segments) - 1:
            segment["end"] = segments[index + 1]["start"]
        else:
            segment["end"] = quantize_time(offset + duration)

    return duration, segments


def generate_tts_and_subtitle(
    input_text: str,
    tts_audio_dir: str,
    tts_output_path: str,
    subtitle_json_path: str,
    google_key_file: str = None,
    voice_name: str = None,
    speaking_rate: float = 1.0,
) -> None:
    """
    입력 텍스트로부터 TTS 오디오와 자막 JSON 파일을 생성합니다.
    
    주의: GCP 인증은 이미 설정되어 있어야 합니다.
    google_key_file 파라미터는 호환성을 위해 유지되지만 사용되지 않습니다.
    """
    print(f"🎤 speaking_rate applied = {speaking_rate}")
    chunks = chunk_text_by_bytes(input_text)
    client = get_tts_client()

    os.makedirs(tts_audio_dir, exist_ok=True)
    os.makedirs(os.path.dirname(tts_output_path), exist_ok=True)

    all_segments: List[Dict[str, Any]] = []
    audio_paths: List[str] = []
    offset = 0.0

    selected_voice = voice_name or VOICE_NAME

    for index, chunk in enumerate(chunks):
        duration, segments = synthesize_chunk(
            client,
            chunk,
            index,
            offset,
            tts_audio_dir,
            selected_voice,
            speaking_rate,
        )
        audio_paths.append(os.path.join(tts_audio_dir, f"chunk_{index}.mp3"))
        all_segments.extend(segments)
        offset += duration

    refined: List[Dict[str, Any]] = []
    for segment in all_segments:
        refined.extend(split_segment_by_length(segment, MAX_SUBTITLE_CHARS))

    clean: List[Dict[str, Any]] = []
    trash = {'"', """, """, "'", "''", ".", "..", "...", "...."}
    for segment in refined:
        text = segment["text"].strip()
        if not text or text in trash:
            continue
        clean.append(segment)

    clips: List[AudioFileClip] = []
    for path in audio_paths:
        if not os.path.exists(path):
            print(f"⚠️ 오디오 파일이 존재하지 않아 건너뜁니다: {path}")
            continue
        clips.append(AudioFileClip(path))

    if not clips:
        print("❌ 병합할 오디오 클립이 없습니다.")
        return

    final_audio = concatenate_audioclips(clips)
    final_audio.write_audiofile(tts_output_path)

    os.makedirs(os.path.dirname(subtitle_json_path), exist_ok=True)
    with open(subtitle_json_path, "w", encoding="utf-8") as file:
        json.dump(clean, file, ensure_ascii=False, indent=4)

    print(
        f"🎉 완료! 자막 {len(clean)}개 생성, TTS 저장됨 → {tts_output_path}"
    )

