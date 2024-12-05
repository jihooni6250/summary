import fitz
import io
from PIL import Image, UnidentifiedImageError
import hashlib
from multiprocessing import Pool


def process_page_images(args):
    """
    페이지 단위로 이미지를 처리
    Args:
        args (tuple): (페이지 번호, 이미지 정보 리스트).

    Returns:
        tuple: (페이지 번호, [(이미지 객체, 메타데이터)의 리스트]).
    """
    page_num, images_info = args
    images = []
    seen_hashes = set()  # 중복된 해시 저장소

    for img in images_info:
        xref = img['xref']
        base_image = img['base_image']
        image_bytes = base_image["image"]
        img_hash = hashlib.md5(image_bytes).hexdigest()  # 이미지의 MD5 해시 계산

        # 중복 여부 확인
        if img_hash in seen_hashes:
            print(f"Page {page_num + 1}: 중복된 이미지 생략")
            continue
        seen_hashes.add(img_hash)

        try:
            image = Image.open(io.BytesIO(image_bytes))

            # PIL에서 지원되지 않는 형식 변환
            if image.format not in ["JPEG", "PNG"]:
                image = image.convert("RGB")

            metadata = {
                "page": page_num,
                "size": (base_image["width"], base_image["height"]),
                "format": base_image["ext"],
            }
            images.append((image, metadata))

        except UnidentifiedImageError:
            print(f"Page {page_num + 1}: 식별할 수 없는 이미지 형식 생략")

    return page_num, images


def extract_images_parallel(pdf_path):
    """
    PDF의 모든 페이지를 병렬로 처리하여 이미지를 추출.
    Args:
        pdf_path (str): PDF 파일 경로.

    Returns:
        list: [(이미지 객체, 메타데이터)의 리스트].
    """
    doc = fitz.open(pdf_path)
    pages_data = []

    for page_num, page in enumerate(doc):
        images_info = []
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            images_info.append({
                "xref": xref,
                "base_image": base_image,
            })
        pages_data.append((page_num, images_info))

    with Pool() as pool:
        results = pool.map(process_page_images, pages_data)

    # 페이지 번호로 정렬된 이미지 리스트 반환
    sorted_results = sorted(results, key=lambda x: x[0])
    images_with_metadata = [item for _, images in sorted_results for item in images]
    return images_with_metadata


def save_images(images_with_metadata, save_dir):
    """
    추출된 이미지를 저장
    Args:
        images_with_metadata (list): (이미지 객체, 메타데이터)의 리스트.
        save_dir (str): 저장 디렉토리.
    """
    for image, metadata in images_with_metadata:
        page_num = metadata["page"]
        img_format = metadata["format"]
        save_ext = "png" if img_format not in ["jpeg", "png"] else img_format
        save_path = f"{save_dir}/page_{page_num + 1}_img.{save_ext}"
        image.save(save_path, format=save_ext.upper())
        print(f"저장됨: {save_path}")


def extract_and_save_images(pdf_path, save_dir=None):
    """
    PDF에서 병렬로 이미지를 추출하고 저장.
    Args:
        pdf_path (str): PDF 파일 경로.
        save_dir (str, optional): 이미지를 저장할 디렉토리. None이면 저장하지 않음.

    Returns:
        list: (이미지 객체, 메타데이터)의 리스트.
    """
    images_with_metadata = extract_images_parallel(pdf_path)

    # 저장 디렉토리가 제공되면 저장
    if save_dir:
        save_images(images_with_metadata, save_dir)

    return images_with_metadata
