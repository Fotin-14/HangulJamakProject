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
        
        onset_roma = ONSET_ROMA.get(self.onset, '')
        nucleus_roma = VOWEL_ROMA.get(self.nucleus, '')
        coda_roma = CODA_ROMA.get(self.coda, '')
        
        return onset_roma + nucleus_roma + coda_roma


class Romanizer:
    """한글 문장을 로마자로 변환하는 클래스"""
    
    def __init__(self, text):
        self.text = text
    
    def romanize(self):
        """전체 텍스트를 로마자로 변환"""
        result = []
        
        # 단어 단위로 예외 처리 확인
        words = self.text.split(' ')
        romanized_words = []
        
        for word in words:
            # 예외 사전에 있는지 확인
            if word in EXCEPTIONS:
                romanized_words.append(EXCEPTIONS[word])
            else:
                # 글자 단위로 변환
                romanized_chars = []
                for char in word:
                    syllable = Syllable(char)
                    romanized_chars.append(syllable.romanize())
                romanized_words.append('∙'.join(romanized_chars))
        
        return ' '.join(romanized_words)


# 편의 함수
def romanize(text):
    """텍스트를 로마자로 변환 (단축 함수)"""
    r = Romanizer(text)
    return r.romanize()


# 테스트
if __name__ == '__main__':
    test_words = ['안녕하세요 선생님', '먹어', '좋아', '한글']
    for word in test_words:
        print(f'{word} → {romanize(word)}')