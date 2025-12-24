"""텍스트 정규화 유틸리티"""


def normalize_text(text: str) -> str:
    """
    파이프라인 전체에서 공통으로 사용하는 텍스트 정규화
    """
    return (
        text.replace("\n", " ")
            .replace("…", "...")
            .replace("'", "'")
            .replace("'", "'")
            .replace(""", '"')
            .replace(""", '"')
            .strip()
    )

