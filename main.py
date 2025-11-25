from korean_pronouncer import KoreanPronouncer

sentence = KoreanPronouncer("사과는 영어로 'apple'이라고 해")

print(sentence.transformed_sentence())
print(sentence.list_romanizer())
print(sentence.hangul_to_romanized())
sentence.all_in_one()
