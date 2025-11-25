import os
import sys
from konlpy.tag import Mecab
from typing import List, Tuple
from korean_romanizer.romanizer import Romanizer
from .rules_table import (
    CHO_LIST,
    JUNG_LIST,
    JONG_LIST,
    VOWEL_ROMA,
    ONSET_ROMA,
    CODA_ROMA,
)
from .rules import algorithm

BASE = 0xAC00
N_CHO = 19
N_JUNG = 21
N_JONG = 28
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
dicpath = os.path.join(project_root, 'mecab', 'mecab-ko-dic').replace('\\', '/')
null_device = 'nul' if sys.platform == 'win32' else '/dev/null'

try:
    _mecab_instance = Mecab(dicpath=f'{dicpath} -r {null_device}')
except Exception as e:
    print(f"MeCab 로딩 실패: {e}")
    raise e

class KoreanPronouncer:
    def __init__(self, str):
        print("\n** 객체 생성과 동시에 문장 입력 완료 **\n")
        
        self.str = str
        self._mecab = _mecab_instance

    def __str__(self):
        return f"입력된 문장: '{self.str}'"
    
    def _normalize_tag(self, tag: str) -> str:
        if tag in ("VV", "VV+ETM", "XSV+ETM", "VV+EC", "VX+EC"):
            return tag
        if tag.startswith("N"):
            return "N"  #체언
        elif tag.startswith("V"):
            return "V"  # 용언
        elif tag.startswith("M"):
            return "M"  # 수식언
        elif tag == "IC":
            return "I"  # 감탄사
        elif tag.startswith("J"):
            return "J"  # 조사
        elif tag.startswith("E"):
            return "E"  # 어미
        elif tag.startswith("X"):
            return "X"  # 접사
        elif tag.startswith("S"):
            return "S"  # 기호
        else:
            return "UNK"  # 알 수 없는 태그
    
    def _is_hangul_syll(self, ch: str) -> bool:
        o = ord(ch)
        return BASE <= o <= 0xD7A3

    def _decompose(self, ch: str) -> Tuple[str, str, str]:
        """완성형 한글 1글자를 (초성, 중성, 종성) 자모로 분해"""
        assert self._is_hangul_syll(ch)
        o = ord(ch) - BASE
        cho = o // (N_JUNG * N_JONG)
        jung = (o % (N_JUNG * N_JONG)) // N_JONG
        jong = (o % (N_JUNG * N_JONG)) % N_JONG
        return CHO_LIST[cho], JUNG_LIST[jung], JONG_LIST[jong]

    def _compose(self, cho: str, jung: str, jong: str = "") -> str:
        """(초성, 중성, 종성) 자모를 완성형 한글 1글자로 합성"""
        try:
            cho_idx = CHO_LIST.index(cho)
            jung_idx = JUNG_LIST.index(jung)
            # 종성이 없으면 빈 문자열('')이므로 0번째 인덱스
            jong_idx = JONG_LIST.index(jong)

            code = BASE + (cho_idx * N_JUNG + jung_idx) * N_JONG + jong_idx
            return chr(code)
        except ValueError as e:
            # 유효하지 않은 자모가 입력될 경우 예외 처리
            print(f"Error in compose: Invalid jamo provided. {e}")
            return ""
        
    def _token_to_jamo(self, token: Tuple[str, str]) -> List[str]:
        word, tag = token
        norm_tag = self._normalize_tag(tag)
        rows: List[str] = []

        for ch in word:
            if self._is_hangul_syll(ch):
                cho, jung, jong = self._decompose(ch)  # (초성, 중성, 종성) 문자열
                rows.append([cho, jung, jong, norm_tag])
            else:
                # 숫자/영문/기호/공백 등 비한글 처리
                rows.append([ch, "", "", norm_tag])
        return rows
    
    def _extend_tokens(self, tokens: List[Tuple[str, str]]) -> List[List[str]]:
        merged: List[List[str]] = []
        for token in tokens:
            merged.extend(self._token_to_jamo(token))
        return merged
    
    def _split_sentence(self) -> List[List[str]]:
        all_results = []
    
        words = self.str.split()
        nested_list = [[word] for word in words]
        for text in nested_list:
            result = self._extend_tokens(self._mecab.pos(text[0]))
            all_results.append(result)
    
        return all_results
    
    def _recombine_korean(self, input_data: list) -> str:
    
        final_word = ""
        
        for part in input_data:
            for syllable_jamo_list in part:
            
                jamo_only = syllable_jamo_list[:3] 
                
                cho = jamo_only[0]
                jung = jamo_only[1]
                jong = jamo_only[2] if len(jamo_only) > 2 and jamo_only[2] else ""
                
                combined_char = self._compose(cho, jung, jong) if cho in CHO_LIST else cho
                
                final_word += combined_char
                
            if part != input_data[-1]:
                 final_word += " "
                 
        return final_word
    def _romanize_syllable(self, cho: str, jung: str, jong: str) -> str:
        """
        초성, 중성, 종성을 받아 로마자로 변환합니다.
        """
        # 중성(jung)이 비어있으면 비한글 문자이므로 cho에 담긴 문자를 그대로 반환
        if not jung and not jong:
            return cho
        # 1. 초성 (Onset) 처리
        # ONSET_ROMA에 정의된 대로 초성 'ㅇ'은 빈 문자열로 처리됩니다.
        roman_cho = ONSET_ROMA.get(cho, cho)
        # 2. 중성 (Vowel) 처리
        roman_jung = VOWEL_ROMA.get(jung, jung)
        # 3. 종성 (Coda) 처리
        if not jong:
            roman_jong = ""
        else:
            # CODA_ROMA 테이블을 사용하여 종성 처리 (중화된 발음을 사용)
            roman_jong = CODA_ROMA.get(jong, jong)
        return roman_cho + roman_jung + roman_jong
    
    def _phonetic_transformer(self):
        modified_stc: List = []
        split_to_jamo = self._split_sentence()

        for word in split_to_jamo:
            modified_stc.append(algorithm(word))

        return modified_stc
    
    def transformed_sentence(self):
        return self._recombine_korean(self._phonetic_transformer())
    
    def list_romanizer(self) -> List[str]:
        romanized_list: List[str] = []
        modified_stc = self._phonetic_transformer()

        for i, part in enumerate(modified_stc):

            for syllable_jamo_list in part:
                jamo_only = syllable_jamo_list[:3]

                cho = jamo_only[0]
                jung = jamo_only[1]
                jong = jamo_only[2] if len(jamo_only) > 2 and jamo_only[2] else ""

                combined_romanized = self._romanize_syllable(cho, jung, jong) if cho in ONSET_ROMA else cho
                
                romanized_list.append(combined_romanized)

            if i < len(modified_stc) - 1:
                romanized_list.append(" ")
                
        return romanized_list

    def hangul_to_romanized(self):
        result = self.transformed_sentence()
        converted_result = Romanizer(result).romanize()
        return converted_result

    def all_in_one(self):
        result = self.transformed_sentence()
        converted_result = self.hangul_to_romanized()

        print("\n-------------------------")
        print(f"기존 문장: {self.str}")
        print(f"발음 규칙 적용: {result}")
        print(f"자막 : {converted_result}")
    
