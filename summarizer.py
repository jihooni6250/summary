import logging
import asyncio
import openai
from openai import AsyncOpenAI

client = AsyncOpenAI()

logger = logging.getLogger(__name__)

async def call_openai_api(prompt, max_tokens=500, temperature=0.7, retries=3):
    """OpenAI API 호출 로직 (수정된 부분)"""
    for attempt in range(retries):
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response["choices"][0]["message"]["content"].strip()
        except openai.OpenAIError as e:
            logger.warning(f"OpenAI API 호출 실패 (시도 {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2)
            else:
                logger.error("OpenAI API 호출 최대 시도 초과")
                return "요약 생성 중 오류가 발생했습니다."

async def generate_summary(text, title, ocr_text, keywords, emphasis=None, exclude=None, max_tokens=500, temperature=0.7):
    """요약 생성 (강조/제외 옵션 추가)"""
    combined_text = f"{title}\n\n{text}\n\n{ocr_text}"
    prompt = f"다음 텍스트를 요약해 주세요.\n"
    if emphasis:
        prompt += f"다음 주제를 강조해 주세요: {', '.join(emphasis)}.\n"
    if exclude:
        prompt += f"다음 주제를 제외해 주세요: {', '.join(exclude)}.\n"
    prompt += f"텍스트:\n{combined_text}"
    return await call_openai_api(prompt, max_tokens=max_tokens, temperature=temperature)


# async def call_openai_api(prompt, max_tokens=500, temperature=0.7, retries=3):
#     for attempt in range(retries):
#         try:
#             response = await client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are a helpful assistant."},
#                     {"role": "user", "content": prompt},
#                 ],
#                 max_tokens=max_tokens,
#                 temperature=temperature,
#             )
#             return response.choices[0].message.content.strip()
#         except Exception as e:
#             logger.warning(f"OpenAI API 호출 실패 (시도 {attempt + 1}/{retries}): {e}")
#             if attempt < retries - 1:
#                 await asyncio.sleep(2)
#             else:
#                 logger.error("OpenAI API 호출 최대 시도 초과")
#                 return "요약 생성 중 오류가 발생했습니다."
#
# async def generate_summary(text, title, ocr_text, keywords, max_tokens=500, temperature=0.7):
#     """
#     OpenAI API를 호출하여 텍스트 요약을 생성합니다.
#
#     Args:
#         text (str): PDF에서 추출한 텍스트
#         title (str): PDF 제목
#         ocr_text (str): OCR을 통해 추출된 텍스트
#         keywords (list): 키워드 리스트
#         max_tokens (int): 생성할 최대 토큰 수
#         temperature (float): 생성의 무작위성 조정
#
#     Returns:
#         str: 생성된 요약 텍스트
#     """
#     combined_text = f"{title}\n\n{text}\n\n{ocr_text}"
#     prompt = f"다음 텍스트를 요약해 주세요. 중요한 키워드: {', '.join(keywords)}.\n텍스트:\n{combined_text}"
#     return await call_openai_api(prompt, max_tokens=max_tokens, temperature=temperature)

