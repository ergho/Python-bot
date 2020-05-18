import re

def gen_trigrams(text: str) -> set:
    words = [f'  {x} ' for x in re.split(r'\W+', text.lower())]
    trigram = set()
    for word in words:
        for i in range(0, len(word) - 2):
            trigram.add(word[i:i+3])
    return trigram

def comparing(wordone: str, wordtwo: str) -> float:
    first_word = gen_trigrams(wordone)
    second_word = gen_trigrams(wordtwo)
    print(first_word)
    print(second_word)
    unique: float = len(first_word | second_word)
    equal: float = len(first_word & second_word)
    return equal / unique
