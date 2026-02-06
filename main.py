from korean_pronouncer import KoreanPronouncer
from korean_pronouncer import rules

text = "누구 눈물 뭄바이 굿 울"
sentence = KoreanPronouncer(text)
mecab = sentence._mecab

sentence.all_in_one()
# print(sentence.hangul_to_romanized())
# print(mecab.pos(text))
# print(mecab.tagger.parse(text))
# print(sentence._split_sentence())
