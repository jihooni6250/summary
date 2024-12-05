import pytesseract
from PIL import Image, ImageOps, ImageFilter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"


def preprocess_image(image):
    """이미지 전처리 개선"""
    # 이미지 크기 정규화 (300 DPI 기준)
    desired_dpi = 300
    current_dpi = image.info.get('dpi', (72, 72))[0]
    if current_dpi < desired_dpi:
        scale_factor = desired_dpi / current_dpi
        new_size = tuple(int(dim * scale_factor) for dim in image.size)
        image = image.resize(new_size, Image.LANCZOS)

    # 그레이스케일 변환
    gray_image = image.convert("L")

    # 노이즈 제거 (단일 단계로 수정)
    denoised = gray_image.filter(ImageFilter.MedianFilter(3))

    # 대비 및 밝기 최적화
    enhanced = ImageOps.autocontrast(denoised, cutoff=2)
    enhanced = ImageOps.equalize(enhanced)

    # 적응형 이진화
    binary = enhanced.point(lambda x: 0 if x < 127 else 255, '1')

    # 모폴로지 연산 수정
    kernel_size = 3
    binary = binary.filter(ImageFilter.MaxFilter(kernel_size))

    # 기울기 보정
    try:
        osd = pytesseract.image_to_osd(binary)
        angle = float(re.search(r'Rotate: (\d+)', osd).group(1))
        if angle > 0:
            binary = binary.rotate(angle, expand=True, fillcolor=255)
    except:
        pass

    return binary


def extract_text_from_image(image, lang='kor+eng'):
    """개선된 OCR 텍스트 추출"""
    try:
        processed_image = preprocess_image(image)

        # 다양한 PSM 모드 시도
        psm_modes = [6, 3, 4, 11]
        results = []

        for psm in psm_modes:
            config = f'--oem 3 --psm {psm} -c preserve_interword_spaces=1 -c tessedit_char_blacklist=|~_^°'

            # 원본 이미지로 시도
            results.append(pytesseract.image_to_string(image, lang=lang, config=config))
            # 전처리된 이미지로 시도
            results.append(pytesseract.image_to_string(processed_image, lang=lang, config=config))

        # 결과 중 가장 좋은 것 선택 (특수문자 비율이 적고 길이가 긴 것)
        filtered_results = [r for r in results if len(r.strip()) > 0]
        if not filtered_results:
            return "텍스트를 추출할 수 없습니다."

        text = max(filtered_results,
                   key=lambda x: (len(x.strip()),
                                  -len(re.findall(r'[^a-zA-Z0-9가-힣\s]', x))))

        return post_process_text(text)
    except Exception as e:
        return f"OCR 오류 발생: {str(e)}"


def post_process_text(text):
    """텍스트 후처리 개선"""
    # 기본 정규화
    text = normalize_text(text)

    # 한글 자모음 결합 오류 수정
    text = re.sub(r'([ㄱ-ㅎ])([ㅏ-ㅣ])', lambda m: chr(
        ord('가') + ((ord(m.group(1)) - ord('ㄱ')) * 28 * 21) + ((ord(m.group(2)) - ord('ㅏ')) * 28)), text)

    # 숫자 형식 통일
    text = re.sub(r'[oO]', '0', text)  # O를 0으로
    text = re.sub(r'[lI]', '1', text)  # l이나 I를 1로

    # 불필요한 줄바꿈 제거
    text = re.sub(r'\n+', ' ', text)

    return text.strip()

def normalize_text(text):
    """텍스트 정규화"""
    # 여러 공백을 하나로 통일
    text = re.sub(r'\s+', ' ', text)
    # 앞뒤 공백 제거
    return text.strip()


def calculate_text_similarity(text1, text2):
    """TF-IDF 기반 텍스트 유사도 계산"""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]
