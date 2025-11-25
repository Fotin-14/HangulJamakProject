from typing import List
from .rules_table import (
    CHO_LIST,
    JUNG_LIST,
    JONG_LIST,
    HOT_BATCHIM,
    SSANG_BATCHIM,
    GYEOB_BATCHIM,
    FINAL_NEUTRAL_MAP,
    SPLIT_FINAL_FOR_LIAISON,
    ASP_MAP,
    ASP_MAP2,
    PALATALIZATION_MAP,
    TENSE_MAP,
    NASALIZE_FINAL,
    VOWEL_ROMA,
    ONSET_ROMA,
    CODA_ROMA
)

#---------------rules----------------
def rule8(jong: str) -> str:
    return FINAL_NEUTRAL_MAP[jong]

def rule11_cf(jong, tag):
    if tag.startswith('V'):
        jong = 'ㄹ'
        return jong

def rule12(jong, next_cho):
    if jong == 'ㅎ':
        if next_cho in ASP_MAP:
            return ('', ASP_MAP[next_cho])
        elif next_cho == 'ㅅ':
            return ('', 'ㅆ')
        elif next_cho == 'ㄴ':
            return ('ㄴ', '')
        else:
            return ('', '')
    elif jong in ['ㄶ', 'ㅀ']:
        if next_cho in ASP_MAP:
            return (ASP_MAP2[jong], ASP_MAP[next_cho])
        elif next_cho == 'ㅅ':
            return (ASP_MAP2[jong], 'ㅆ')
        else:
            return ('', ASP_MAP2[jong])
    else:
        if jong in {'ㄱ','ㄷ','ㅂ','ㅈ'}:
            return ('', ASP_MAP[jong])
        else:
            return (ASP_MAP2[jong], ASP_MAP[jong])

def rule17(jong, next_cho, next_jung):
    if jong == 'ㄷ' and next_cho == 'ㅎ' and next_jung == 'ㅣ':
        jong = ''
        next_cho = 'ㅊ'
        return (jong, next_cho)
    elif jong == 'ㄷ':
        jong = ''
        next_cho = 'ㅈ'
        return (jong, next_cho)
    elif jong == 'ㅌ':
        jong = ''
        next_cho = 'ㅊ'
        return (jong, next_cho)
    else:
        jong = 'ㄹ'
        next_cho = 'ㅊ'
        return (jong, next_cho)
    
def rule18(jong):
    if FINAL_NEUTRAL_MAP[jong] == 'ㄱ':
        return 'ㅇ'
    elif FINAL_NEUTRAL_MAP[jong] == 'ㄷ':
        return 'ㄴ'
    else:
        return 'ㅁ'
    
def rule19(next_cho: str) -> str:
    next_cho = 'ㄴ'
    return next_cho

def rule20(jong, next_cho):
    if jong in {'ㄴ', 'ㄹ'}:
        return 'ㄹ'
    elif jong in {'ㅀ', 'ㄾ'} and next_cho == 'ㄴ':
        jong = 'ㄹ'
        next_cho = 'ㄹ'
        return (jong, next_cho)
    
def rule23(jong, next_cho):
    return (FINAL_NEUTRAL_MAP[jong], TENSE_MAP[next_cho])

def rule24(jong, tag, next_cho, next_jung, next_tag):
    if next_cho == 'ㄱ' and next_jung == 'ㅣ' and next_tag == 'VV':
        return jong, next_cho
    elif FINAL_NEUTRAL_MAP[jong] in ['ㄴ','ㅁ']  and tag.startswith('V') and next_cho in TENSE_MAP:
        return (FINAL_NEUTRAL_MAP[jong], TENSE_MAP[next_cho])
    else:
        return jong, next_cho
    
def rule29():
    return 'ㄴ'

def rule30(next_cho):
    if next_cho in TENSE_MAP:
        return ('', TENSE_MAP[next_cho])
    else:
        return 'ㄴ'
#------------------------------------

def algorithm(word: List[List[str]]) -> List[List[str]]:
    for i in range(len(word)):
        cho, jung, jong, tag = word[i]
        if i+1 < len(word):
            next_cho, next_jung, _, next_tag = word[i+1]
        elif i+1 == len(word):
            next_cho = 't'
        # test
        # print(f"jong: {jong}, next_cho: {next_cho}")

        if jong != '' and jong in JONG_LIST:
            if next_cho == 't':
                word[i][2] = FINAL_NEUTRAL_MAP[jong]

            if next_cho in CHO_LIST:  # 다음 초성 = 자음
                if jong in HOT_BATCHIM:
                    if jong == 'ㄱ' and next_cho == 'ㄹ':
                        word[i+1][0] = rule19(next_cho)
                    elif jong == 'ㄱ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)
                    elif jong == 'ㄱ' and next_cho in ['ㄴ','ㅁ']:
                        word[i][2] = rule18(jong)
                    elif jong == 'ㄱ' and next_cho == 'ㅎ':
                        word[i][2], word[i+1][0] = rule12(jong, next_cho)
                        
                    elif jong == 'ㄴ' and next_cho == 'ㄹ':
                        word[i][2] = rule20(jong, next_cho)
                    elif jong == 'ㄴ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule24(jong, tag, next_cho, next_jung, next_tag)

                    elif jong == 'ㄷ' and next_cho in ['ㄴ', 'ㅁ']:
                        word[i][2] = rule18(jong)
                    elif jong == 'ㄷ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)
                    elif jong == 'ㄷ' and next_cho == 'ㅎ' and next_jung == 'ㅣ':
                        word[i][2], word[i+1][0] = rule17(jong, next_cho, next_jung)
                    elif jong == 'ㄷ' and next_cho == 'ㅎ':
                        word[i][2], word[i+1][0] = rule12(jong, next_cho)

                    elif jong == 'ㄹ' and next_cho == 'ㄴ': 
                        word[i+1][0] = rule20(jong, next_cho)

                    elif jong == 'ㅁ' and next_cho == 'ㄹ':
                        word[i+1][0] = rule19(next_cho)
                    elif jong == 'ㅁ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule24(jong, tag, next_cho, next_jung, next_tag)

                    elif jong == 'ㅂ' and next_cho in {'ㄴ', 'ㅁ'}:
                        word[i][2] = rule18(jong)
                    elif jong == 'ㅂ' and next_cho == 'ㄹ':
                        word[i+1][0] = rule19(next_cho)
                    elif jong == 'ㅂ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)
                    elif jong == 'ㅂ' and next_cho == 'ㅎ':
                        word[i][2], word[i+1][0] = rule12(jong, next_cho)

                    elif jong in {'ㅋ','ㅅ','ㅊ','ㅌ','ㅍ'} and next_cho in {'ㄴ', 'ㅁ'}:
                        word[i][2] = rule18(jong)
                    elif jong in {'ㅋ','ㅅ','ㅊ','ㅌ','ㅍ'} and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)

                    elif jong == 'ㅅ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule30(next_cho)
                    elif jong == 'ㅅ' and next_cho in {'ㄴ', 'ㅁ'}:
                        word[i+1][0] = rule30(next_cho)

                    elif jong == 'ㅇ' and next_cho == 'ㄹ':
                        word[i+1][0] = rule19(next_cho)
                    elif jong == 'ㅇ' and next_cho == 'ㅇ':
                        continue

                    elif jong == 'ㅈ' and next_cho in {'ㄴ', 'ㅁ'}:
                        word[i][2] = rule18(jong)
                    elif jong == 'ㅈ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)
                    elif jong == 'ㅈ' and next_cho == 'ㅎ':
                        word[i][2], word[i+1][0] = rule12(jong, next_cho)

                    elif jong == 'ㅎ' and next_cho in {'ㄱ','ㄷ','ㅈ','ㅅ','ㄴ'}:
                        word[i][2], word[i+1][0] = rule12(jong, next_cho)

                elif jong in GYEOB_BATCHIM:
                    if jong == 'ㄳ' and next_cho in ['ㄴ','ㅁ']:
                        word[i][2] = rule18(jong)
                    elif jong == 'ㄳ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)
                    elif jong == 'ㄵ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule24(jong, tag, next_cho, next_jung, next_tag)
                    elif jong == 'ㄵ' and next_cho == 'ㅎ':
                        word[i][2], word[i+1][0] = rule12(jong, next_cho)
                    elif jong == 'ㄵ':
                        word[i][2] = 'ㄴ'
                    
                    elif jong == 'ㄶ':
                         word[i][2], word[i+1][0] = rule12(jong, next_cho)

                    elif jong == 'ㄺ' and next_cho in ['ㄴ','ㅁ']:
                        word[i][2] = rule18(jong)
                    elif jong == 'ㄺ' and next_cho == 'ㄱ' and tag.startswith('V'):
                        word[i][2] = rule11_cf(jong, tag)
                        word[i+1][0] = TENSE_MAP[next_cho]
                    elif jong == 'ㄺ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)
                    elif jong == 'ㄺ' and next_cho == 'ㅎ':
                        word[i][2], word[i+1][0] = rule12(jong, next_cho)
                    elif jong == 'ㄺ':
                        word[i][2] = FINAL_NEUTRAL_MAP[jong]

                    elif jong == 'ㄻ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule24(jong, tag, next_cho, next_jung, next_tag)

                    elif (cho == 'ㄴ' and jung == 'ㅓ' and jong == 'ㄼ') or (cho == 'ㅂ' and jung == 'ㅏ' and jong == 'ㄼ'):
                        if next_cho in TENSE_MAP:
                            word[i][2] = 'ㅂ'
                            word[i+1][0] = TENSE_MAP[next_cho]
                        elif next_cho == 'ㅎ':
                            word[i][2], word[i+1][0] = rule12(jong, next_cho)
                        else:
                            word[i][2] = 'ㅂ'
                    elif jong == 'ㄼ' and next_cho in ['ㄴ','ㅁ']:
                        word[i][2] = rule18(jong)
                    elif jong == 'ㄼ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)
                    elif jong == 'ㄼ' and next_cho == 'ㅎ':
                        word[i][2], word[i+1][0] = rule12(jong, next_cho)

                    elif jong == 'ㄾ' and next_cho == 'ㄴ':
                        word[i][2], word[i+1][0] = rule20(jong, next_cho)
                    elif jong == 'ㄾ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)

                    elif jong == 'ㄿ' and next_cho in ['ㄴ','ㅁ']:
                        word[i][2] = rule18(jong)
                    elif jong == 'ㄿ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)
                    
                    elif jong == 'ㅀ' and next_cho in ['ㄱ','ㄷ','ㅈ','ㅅ']:
                         word[i][2], word[i+1][0] = rule12(jong, next_cho)
                    elif jong == 'ㅀ' and next_cho == 'ㄴ':
                        word[i][2], word[i+1][0] = rule20(jong, next_cho)

                    elif jong == 'ㅄ' and next_cho in ['ㄴ','ㅁ']:
                        word[i][2] = rule18(jong)
                    elif jong == 'ㅄ' and next_cho in TENSE_MAP:
                        word[i][2], word[i+1][0] = rule23(jong, next_cho)
                    elif jong in {'ㄳ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅄ'} or tag == 't':
                        word[i][2] = rule8(jong)
                else:
                    if jong in {'ㄲ', 'ㅆ'}:
                        if next_cho in ['ㄴ','ㅁ']:
                            word[i][2] = rule18(jong)
                        elif next_cho in TENSE_MAP:
                            word[i][2], word[i+1][0] = rule23(jong, next_cho)
                        else:
                            word[i][2] = FINAL_NEUTRAL_MAP[jong]

            if next_cho == "ㅇ":  # 다음 초성 = 모음 
                if jong in HOT_BATCHIM:
                    if jong == 'ㅎ':
                        word[i][2] = ''
                    elif jong in {'ㄷ','ㅌ'} and next_jung == 'ㅣ':
                        word[i][2], word[i+1][0] = rule17(jong, next_cho, next_jung)
                    elif jong == 'ㅅ' and next_jung == 'ㅣ' and tag.startswith('N') and next_tag.startswith('N'):
                        word[i][2] = 'ㄴ'
                        word[i+1][0] = rule30(next_cho)
                    else:
                        if next_jung in {'ㅏ','ㅓ','ㅗ','ㅜ','ㅟ'} and not next_tag.startswith(('J', 'E', 'X')):
                            word[i][2] = ''
                            word[i+1][0] = FINAL_NEUTRAL_MAP[jong]
                        else:
                            word[i][2] = ''
                            word[i+1][0] = jong
                    
                elif jong in GYEOB_BATCHIM:
                    if jong in {'ㄶ', 'ㅀ'}:
                        word[i][2], word[i+1][0] = rule12(jong, next_cho)
                    elif jong == 'ㄾ' and next_jung == 'ㅣ':
                        word[i][2], word[i+1][0] = rule17(jong, next_cho, next_jung)
                    elif next_jung in {'ㅏ','ㅓ','ㅗ','ㅜ','ㅟ','ㅣ'} and not next_tag.startswith(('J', 'E', 'X')):
                            word[i][2] = ''
                            word[i+1][0] = FINAL_NEUTRAL_MAP[jong]
                    else:
                        word[i][2], word[i+1][0] = SPLIT_FINAL_FOR_LIAISON[jong]
                elif jong in SSANG_BATCHIM:
                    word[i][2] = ''
                    word[i+1][0] = jong
                else:
                    if next_jung in {'ㅏ','ㅓ','ㅗ','ㅜ','ㅟ'}:
                        word[i][2] = ''
                        word[i+1][0] = FINAL_NEUTRAL_MAP[jong]
                    elif next_jung in {'ㅣ','ㅑ','ㅕ','ㅛ','ㅠ'}:
                        if jong == 'ㄹ':
                            word[i+1][0] = 'ㄹ'
                        else:
                            word[i+1][0] = 'ㄴ'
            elif next_cho == 'ㅇ' and next_jung in {'ㅣ','ㅑ','ㅕ','ㅛ','ㅠ'} and next_tag.startswith("N"):
                word[i+1][0] = rule29()
                
        else:
            continue
    return word     