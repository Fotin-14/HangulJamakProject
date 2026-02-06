from .rules_table import (
    ONSET_ROMA,
    VOWEL_ROMA,
    CODA_ROMA,
)

# ============================================
# 예외 단어 사전 (여기서 특정 단어 커스텀 가능!)
# ============================================
EXCEPTIONS = {
    # 초성 'ㅇ' + 종성 없음 (모음만)
    '아': 'ah',
    '안': 'ahn',
    '애': 'ae',
    '야': 'yah',
    '얘': 'yae',
    '어': 'uh',
    '에': 'eh',
    '여': 'yeo',
    '예': 'yeh',
    '오': 'oh',
    '와': 'wah',
    '왜': 'wae',
    '외': 'weh',
    '요': 'yo',
    '우': 'woo',
    '워': 'wo',
    '웨': 'weh',
    '위': 'we',
    '유': 'yoo',
    '으': 'eu',
    '의': 'ui',
    '이': 'e',
}

# 초성 리스트 (인덱스용)
ONSET_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
NUCLEUS_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
CODA_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']


class Syllable:
    """한글 음절 하나를 처리하는 클래스"""
    
    BASE = 0xAC00  # '가'
    
    def __init__(self, char):
        self.char = char
        self.onset = None    # 초성
        self.nucleus = None  # 중성
        self.coda = None     # 종성
        
        if self._is_hangul(char):
            self._decompose(char)
    
    def _is_hangul(self, char):
        """한글인지 확인"""
        return 0xAC00 <= ord(char) <= 0xD7A3
    
    def _get_roma_parts(self):
        """초성, 중성, 종성을 조건부로 로마자 변환"""

        onset_roma = ONSET_ROMA.get(self.onset, '')
        coda_roma = CODA_ROMA.get(self.coda, '')

        # ============ 중성 조건부 변환 ============

        # 'ㅗ' 처리
        if self.nucleus == 'ㅗ':
            if self.coda in ('ㄱ', 'ㄷ', 'ㅁ', 'ㅂ', 'ㅅ'):
                nucleus_roma = 'oh'
            elif self.coda in ('', 'ㄴ', 'ㄹ', 'ㅇ'):
                nucleus_roma = 'o'
            else:
                nucleus_roma = VOWEL_ROMA.get(self.nucleus, '')

        # 'ㅜ' 처리
        elif self.nucleus == 'ㅜ':
            if self.coda == '':
                nucleus_roma = 'u'
            else:
                nucleus_roma = 'oo'

        # 그 외 기본 처리
        else:
            nucleus_roma = VOWEL_ROMA.get(self.nucleus, '')

        return onset_roma, nucleus_roma, coda_roma
    
    def _decompose(self, char):
        """한글을 초성/중성/종성으로 분리"""
        code = ord(char) - self.BASE
        
        # 초성: 588 = 21 * 28
        onset_idx = code // 588
        # 중성: 28
        nucleus_idx = (code % 588) // 28
        # 종성
        coda_idx = code % 28
        
        self.onset = ONSET_LIST[onset_idx]
        self.nucleus = NUCLEUS_LIST[nucleus_idx]
        self.coda = CODA_LIST[coda_idx]
    
    def romanize(self):
        """로마자로 변환"""
        if self.onset is None:
            return self.char
        
        if self.char in EXCEPTIONS:
            return EXCEPTIONS[self.char]
    
        onset_roma, nucleus_roma, coda_roma = self._get_roma_parts()
        
        return onset_roma + nucleus_roma + coda_roma

def is_special_char(char):
    """특수기호인지 확인"""
    # 한글, 영문, 숫자가 아니면 특수기호
    if '가' <= char <= '힣':
        return False
    if 'a' <= char.lower() <= 'z':
        return False
    if '0' <= char <= '9':
        return False
    return True

def has_korean(text):
    """한글이 포함되어 있는지 확인"""
    for char in text:
        if '가' <= char <= '힣':
            return True
    return False

class Romanizer:
    """한글 문장을 로마자로 변환하는 클래스"""
    
    def __init__(self, text):
        self.text = text
    
    def romanize(self):
        """전체 텍스트를 로마자로 변환"""

        # 단어 단위로 예외 처리 확인
        words = self.text.split(' ')
        romanized_words = []

        for word in words:
            # 예외 사전에 있는지 확인
            if word in EXCEPTIONS:
                romanized_words.append(EXCEPTIONS[word])
            elif not has_korean(word):
                romanized_words.append(f"{word}")
            else:
                # 글자 단위로 변환
                romanized_chars = []
                for char in word:
                    syllable = Syllable(char)
                    romanized_chars.append(syllable.romanize())

                # ⭐ 특수기호 앞에는 '.' 안 붙이기
                result = ''
                for i, char in enumerate(romanized_chars):
                    if i == 0:
                        result += char
                    elif is_special_char(word[i]):
                        # 특수기호면 그냥 붙임
                        result += char
                    elif is_special_char(word[i-1]):
                        result += char
                    else:
                        # 일반 글자면 '.' 추가
                        result += '.' + char

                romanized_words.append(result)

        return '  '.join(romanized_words)

# 편의 함수
def romanize(text):
    """텍스트를 로마자로 변환 (단축 함수)"""
    r = Romanizer(text)
    return r.romanize()
