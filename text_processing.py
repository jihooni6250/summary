"""
파일 이름: text_processing.py
설명: 이 파일은 텍스트를 정리(클렌징)하고,
TF-IDF 분석을 통해 중요한 키워드를 추출하는 기능을 제공합니다.
"""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def advanced_clean_text(text):
    """텍스트 클렌징 (수식, 페이지 번호 등 제거)"""
    # 페이지 번호 제거
    text = re.sub(r'\bPage\s?\d+\b', '', text)
    # 수식 제거
    text = re.sub(r'\$.*?\$', '', text)  # LaTeX 형식
    # 중복 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_text(text):
    """기존 클렌징 함수와 통합"""
    cleaned = advanced_clean_text(text)
    return cleaned

def extract_key_sentences(text, num_sentences=3):
    """중요 문장을 TF-IDF로 추출"""
    sentences = text.split(". ")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)

    # 모든 문장의 TF-IDF 평균 계산
    sentence_scores = np.array(tfidf_matrix.mean(axis=1)).flatten()
    ranked_sentences = [sentences[i] for i in sentence_scores.argsort()[-num_sentences:][::-1]]
    return ranked_sentences

def split_by_topics(text, keywords):
    """키워드별로 텍스트를 분리"""
    topics = {}
    for keyword in keywords:
        pattern = re.compile(rf"(?i)\b{keyword}\b.*?(?=\b{keyword}\b|$)", re.DOTALL)
        match = pattern.findall(text)
        if match:
            topics[keyword] = " ".join(match)
    return topics


#
# import re
# from sklearn.feature_extraction.text import TfidfVectorizer
#
# def clean_text(text):
#     """
#     텍스트를 정리하여 불필요한 줄바꿈, 공백, 특수문자를 제거합니다.
#
#     Args:
#         text (str): 원본 텍스트
#
#     Returns:
#         str: 정리된 텍스트
#     """
#     text = re.sub(r'\n+', ' ', text)  # 줄바꿈 제거
#     text = re.sub(r'\s+', ' ', text)  # 중복 공백 제거
#     text = re.sub(r'[^\w\s가-힣]', '', text)  # 특수문자 제거
#     return text.strip()
#
def analyze_key_sections(text, max_features=10):
    """
    TF-IDF를 사용해 텍스트에서 중요한 키워드를 추출합니다.

    Args:
        text (str): 정리된 텍스트
        max_features (int): 추출할 최대 키워드 개수

    Returns:
        list: 추출된 키워드 리스트
    """
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform([text])
    return vectorizer.get_feature_names_out()
