"""
파일 이름: main.py
설명: 이 파일은 PDF 요약 프로세스의 진입점입니다.
각 모듈을 호출하여 최종적으로 요약을 출력합니다.
"""

import asyncio
from PyQt5.QtWidgets import QApplication, QFileDialog
from extractor import extract_pdf_content
from text_processing import clean_text, analyze_key_sections
from summarizer import generate_summary
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def summarize_pdf(pdf_path, save_dir=None, keywords=None):
    """
    PDF 파일을 요약합니다. 비동기 방식으로 실행합니다.

    Args:
        pdf_path (str): PDF 파일 경로
        save_dir (str, optional): 추출된 이미지를 저장할 디렉토리
        keywords (list, optional): 키워드 리스트

    Returns:
        str: 생성된 요약 텍스트
    """
    # PDF 데이터 추출
    text, title, ocr_text = extract_pdf_content(pdf_path)

    # 텍스트 클렌징
    cleaned_text = clean_text(text + " " + ocr_text)

    # 키워드 분석
    extracted_keywords = analyze_key_sections(cleaned_text)
    if keywords:
        extracted_keywords.extend(keywords)

    # 요약 생성
    summary = await generate_summary(cleaned_text, title, ocr_text, extracted_keywords)
    return summary


def select_pdf_file():
    """PDF 파일 경로를 파일 선택 창을 통해 입력받습니다."""
    app = QApplication([])
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(
        None, "Select PDF File", "", "PDF Files (*.pdf);;All Files (*)", options=options
    )
    return file_path


def main():
    """메인 함수 실행"""
    # PDF 파일 경로 선택
    pdf_path = select_pdf_file()
    if not pdf_path:
        print("PDF 파일을 선택하지 않았습니다.")
        return

    # asyncio를 사용해 비동기 방식으로 요약 실행
    summary = asyncio.run(summarize_pdf(pdf_path))
    print("\n=== 최종 요약 ===\n")
    print(summary)


if __name__ == "__main__":
    main()
