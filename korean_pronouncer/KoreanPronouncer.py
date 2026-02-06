import os
import sys
from konlpy.tag import Mecab
from typing import List, Tuple
from .custom_romanizer import Romanizer
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
        self.str = str
        self._mecab = _mecab_instance

    def __str__(self):
        return f"입력된 문장: '{self.str}'"
    
    '''
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
    '''
    
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
        rows: List[str] = []
    
        # Compound 태그 처리 (C_2_3 형태)
        if tag.startswith("C_"):
            # "C_2_3" → [2, 3]
            counts = list(map(int, tag[2:].split('_')))
            
            char_idx = 0
            for morph_idx, count in enumerate(counts, start=1):
                morph_tag = f"NNG_C{morph_idx}"
                for _ in range(count):
                    if char_idx < len(word):
                        ch = word[char_idx]
                        if self._is_hangul_syll(ch):
                            cho, jung, jong = self._decompose(ch)
                            rows.append([cho, jung, jong, morph_tag])
                        else:
                            rows.append([ch, "", "", morph_tag])
                        char_idx += 1
        else:
            # 기존 로직
            for ch in word:
                if self._is_hangul_syll(ch):
                    cho, jung, jong = self._decompose(ch)
                    rows.append([cho, jung, jong, tag])
                else:
                    rows.append([ch, "", "", tag])
        
        return rows
    
    def _extend_tokens(self, tokens: List[Tuple[str, str]]) -> List[List[str]]:
        merged: List[List[str]] = []
        for token in tokens:
            merged.extend(self._token_to_jamo(token))
        return merged
    
    def _split_sentence(self) -> List[List[str]]:
        all_results = []

        full_tokens = self._mecab.pos(self.str)

        words = self.str.split()

        token_idx = 0
        for word in words:
            word_length = len(word)

            current_tokens = []
            char_count = 0

            while token_idx < len(full_tokens) and char_count < word_length:
                surface, tag = full_tokens[token_idx]
                char_count += len(surface)
                token_idx += 1

                if tag == "NNG_C":
                    new_tag = self._get_compound_tag(surface)
                    current_tokens.append((surface, new_tag))
                else:
                    current_tokens.append((surface, tag))

            result = self._extend_tokens(current_tokens)
            all_results.append(result)

        return all_results
    # -----------------------------------------------------------------------
    def _get_compound_tag(self, word: str) -> str:
        """
        Compound 단어의 형태소별 음절 수로 태그 생성
        ex) 신문열람소 → C_2_3 (신문=2, 열람소=3)
        """
        raw_output = self._mecab.tagger.parse(word)

        for line in raw_output.strip().split('\n'):
            if line == 'EOS' or line == '':
                continue
            
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            
            features = parts[1].split(',')

            # Compound 확인 (인덱스 4)
            if len(features) > 4 and features[4] == 'Compound':
                if len(features) > 7:
                    compound_info = features[7]  # 신문/NNG/*+열람소/NNG/*

                    # 각 형태소 음절 수 계산
                    syllable_counts = []
                    for part in compound_info.split('+'):
                        morph_word = part.split('/')[0]  # "신문", "열람소"
                        syllable_counts.append(str(len(morph_word)))

                    # C_2_3 형태로 반환
                    return "C_" + "_".join(syllable_counts)

        return "NNG_C"  # fallback
    # -----------------------------------------------------------------------

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
    
    def _phonetic_transformer(self):
        modified_stc: List = []
        split_to_jamo = self._split_sentence()

        for word in split_to_jamo:
            modified_stc.append(algorithm(word))

        return modified_stc
    
    def transformed_sentence(self):
        return self._recombine_korean(self._phonetic_transformer())

    def hangul_to_romanized(self):
        result = self.transformed_sentence()
        converted_result = Romanizer(result).romanize()
        return converted_result

    def all_in_one(self):
        result = self.transformed_sentence()
        converted_result = self.hangul_to_romanized()
    
        # 단어별로 분리
        original_words = self.str.split()
        transformed_words = result.split()
    
        # 단어별로 짝지어서 출력
        paired = [f"{orig}[{trans}]" for orig, trans in zip(original_words, transformed_words)]
        paired_output = " ".join(paired)
    
        print("\n-------------------------")
        print(paired_output)
        print(f"자막: {converted_result}")
    