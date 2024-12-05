from pdf_text_extractor import extract_text_from_pdf
from pdf_image_extractor import extract_images_from_pdf
from pdf_title_extractor import extract_pdf_title

def process_pdf(pdf_path):
    """PDF 텍스트, 이미지, 제목 추출 및 출력"""
    # 텍스트 추출
    text = extract_text_from_pdf(pdf_path)
    print("PDF 텍스트 추출 완료")

    # 이미지 추출
    images = extract_images_from_pdf(pdf_path)
    print(f"이미지 {len(images)}개 추출 완료")

    # 제목 추출
    title = extract_pdf_title(text)
    print(f"PDF 제목: {title}")

    return text, images, title

if __name__ == "__main__":
    pdf_path = "path/to/your/pdf/file.pdf"  # PDF 파일 경로
    text, images, title = process_pdf(pdf_path)

    # 출력 확인
    print("PDF 내용:")
    print(text[:500])  # 텍스트 앞부분 출력
    print("\n이미지 메타데이터:")
    for img, meta in images:
        print(meta)
    print(f"\n추출된 제목: {title}")
