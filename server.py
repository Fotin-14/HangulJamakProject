import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from korean_pronouncer import KoreanPronouncer
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentenceInput(BaseModel):
    sentence: str
    
@app.get("/")
def read_root():
    return {"message": "Hangul Jamak Server"}

@app.post("/pronounce")
def get_pronunciation_info(input_data: SentenceInput):
    
    input_sentence = input_data.sentence
    
    try:
        pronouncer = KoreanPronouncer(input_sentence)
        result = pronouncer.hangul_to_romanized()     
        return {"romaji": result}
        
    except Exception as e:
        return {"error": f"처리에 실패했습니다: {e}"}
    
@app.post("/pronounce_advanced_version")
def split_to_list(input_data: SentenceInput):

    input_sentence = input_data.sentence

    try:
        pronouncer = KoreanPronouncer(input_sentence)
        result = pronouncer.list_romanizer()     
        return {"romaji": result}
    
    except Exception as e:
        return {"error": f"처리에 실패했습니다: {e}"}
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)