from fastapi import FastAPI
from korean_pronouncer import KoreanPronouncer
from pydantic import BaseModel

app = FastAPI()

class SentenceInput(BaseModel):
    """
    요청 바디에서 'sentence' 키의 문자열을 받기 위한 모델
    """
    sentence: str
    
@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/pronounce")
def get_pronunciation_info(input_data: SentenceInput):
    """
    입력된 한국어 문장에 대해 음운 변동, 로마자 표기, 종합 결과를 반환합니다.
    """
    
    # 1. Pydantic 모델에서 입력 문장을 추출
    input_sentence = input_data.sentence
    
    # 2. KoreanPronouncer 인스턴스 생성 및 기능 실행
    try:
        pronouncer = KoreanPronouncer(input_sentence)
        result = pronouncer.hangul_to_romanized()     
        return result
        
    except Exception as e:
        # 오류 발생 시 오류 메시지 반환
        return {"error": f"처리에 실패했습니다: {e}"}