import fitz


def extract_text_from_pdf(pdf_path, keywords=None):
    """
    PDF 파일에서 텍스트를 추출 (키워드 필터링 기능 추가)

    Args:
        pdf_path (str): PDF 파일 경로.
        keywords (list, optional): 검색할 키워드 리스트. None이면 전체 텍스트 반환.

    Returns:
        str: 추출된 텍스트 (키워드가 포함된 텍스트만 반환).
    """
    doc = fitz.open(pdf_path)
    full_text = []

    for page_num, page in enumerate(doc):
        # 블록 단위로 텍스트 추출
        blocks = page.get_text("blocks")
        if not blocks:
            continue

        # Y(위치), X(왼쪽) 순으로 정렬
        sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

        # 키워드가 포함된 블록 필터링
        page_text = []
        for block in sorted_blocks:
            block_text = block[4].strip()  # 블록 텍스트
            if not block_text:
                continue

            # 키워드 필터링 추가
            if keywords:
                if any(keyword.lower() in block_text.lower() for keyword in keywords):
                    page_text.append(block_text)
            else:
                # 키워드 없으면 전체 블록 추가
                page_text.append(block_text)

        # 페이지에 키워드와 관련된 텍스트가 있으면 추가
        if page_text:
            full_text.append(f"==== Page {page_num + 1} ====\n" + " ".join(page_text))

    return "\n\n".join(full_text) if full_text else "키워드와 일치하는 텍스트가 없습니다."



