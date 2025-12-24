"""시간 관련 유틸리티"""

import time


def log_time_status(start_time: float, message: str) -> None:
    """경과 시간과 함께 상태 메시지를 출력합니다.

    Args:
        start_time: 기준 시작 시각(Unix timestamp).
        message: 함께 출력할 상태 메시지.
    """
    elapsed = time.time() - start_time
    print(f"[{elapsed:6.2f}초] {message}")


def format_hms(seconds: float) -> str:
    """초 단위 시간을 사람 친화적인 문자열로 변환합니다.

    Args:
        seconds: 변환할 시간(초).

    Returns:
        `"H시간 M분 S.S초"` 또는 `"M분 S.S초"` 형태의 문자열.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remain = seconds % 60
    if hours > 0:
        return f"{hours}시간 {minutes}분 {remain:.1f}초"
    return f"{minutes}분 {remain:.1f}초"


def run_stage(stage_name: str, func, *args) -> float:
    """단계 실행 래퍼.

    Args:
        stage_name: 단계 이름
        func: 실행할 함수
        *args: 함수에 전달할 인자들

    Returns:
        실행에 소요된 시간(초)
    """
    print(f"\n▶ {stage_name} 시작...")

    start = time.perf_counter()
    func(*args)
    end = time.perf_counter()

    elapsed = end - start
    print(f"✔ {stage_name} 완료: {elapsed:.2f}초 ({format_hms(elapsed)})")

    return elapsed

