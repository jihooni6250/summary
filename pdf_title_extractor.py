import fitz


def extract_title_from_pdf(pdf_path):
    """
    PDF에서 제목을 추출하는 개선된 함수
    """
    doc = fitz.open(pdf_path)
    first_page = doc[0]
    page_dict = first_page.get_text("dict")
    blocks = page_dict.get("blocks", [])

    if not blocks:
        return "제목을 찾을 수 없습니다."

    # 제목 후보 저장을 위한 리스트
    title_parts = []
    max_font_size = 0

    # 첫 번째 패스: 최대 폰트 크기 찾기
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                font_size = span.get("size", 0)
                if font_size > max_font_size:
                    max_font_size = font_size

    # 두 번째 패스: 최대 폰트 크기와 동일하거나 약간 작은 텍스트 수집
    threshold = max_font_size * 0.95  # 5% 이내의 차이는 허용

    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                font_size = span.get("size", 0)
                text = span.get("text", "").strip()

                if text and font_size >= threshold:
                    title_parts.append(text)

    # 수집된 텍스트 조각들을 하나의 제목으로 결합
    full_title = " ".join(title_parts)

    return full_title if full_title else "제목을 찾을 수 없습니다."
