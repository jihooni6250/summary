"""
파일 이름: extractor.py
설명: 이 파일은 PDF에서 텍스트, 제목, 이미지 데이터를 추출하고,
이미지에서 OCR을 사용해 텍스트를 추출하는 기능을 제공합니다.
"""

from pdf_text_extractor import extract_text_from_pdf
from pdf_title_extractor import extract_title_from_pdf
from pdf_image_extractor import extract_and_save_images
from ocr_processor import extract_text_from_image

def extract_pdf_content(pdf_path, save_dir=None):
    """
    PDF에서 텍스트, 제목, 이미지, 그리고 OCR 데이터를 추출합니다.

    Args:
        pdf_path (str): PDF 파일 경로
        save_dir (str, optional): 추출한 이미지를 저장할 디렉토리

    Returns:
        tuple: PDF 텍스트, 제목, OCR 텍스트 (이미지에서 추출)
    """
    # 텍스트 추출
    text = extract_text_from_pdf(pdf_path)

    # 제목 추출
    title = extract_title_from_pdf(pdf_path)

    # 이미지 추출 및 OCR 수행
    images_with_metadata = extract_and_save_images(pdf_path, save_dir=save_dir)
    ocr_texts = [extract_text_from_image(image) for image, _ in images_with_metadata]

    return text, title, " ".join(ocr_texts)
