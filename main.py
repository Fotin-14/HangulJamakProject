from korean_pronouncer import KoreanPronouncer

sentence = KoreanPronouncer("아 이 진짜 짜증나게 하네")

print(sentence.transformed_sentence())
# print(sentence.list_romanizer())
print(sentence.hangul_to_romanized())
sentence.all_in_one()
