from phonetics import PhoneticAnalysis
from collections import defaultdict

class RhymeAnalysis(PhoneticAnalysis):
    def __init__(self, text, ipa_text):
        super().__init__(text, ipa_text)
        self.clean_text()
        self.ipa_words = self.ipa_text.split()
        self.words_orig = self.text.split()
        self.compute_vowel_representation()

    def get_rhyme_schemes_for_all_vowels(self):
        rhymes = {}

        for vowel in list(self.vowel_set):
            rhymes_for_vowel = self.find_rhymes_for_vowel(vowel)
            rhymes[vowel] = rhymes_for_vowel
        
        return rhymes

    def find_rhymes_for_vowel(self, vowel):
        rhyming_vowel_idxs = [ self.vowels_idx[i] for i in range(len(self.vowels_idx)) if self.vowels[i] == vowel ]

        rhyming_words = []
        rhyming_word_indices = []

        for vow_idx in rhyming_vowel_idxs:
            start = end = vow_idx
            # move start and end pointers to their respective word boundaries
            while start > 1 and not self.is_space_or_newline(self.ipa_text[start-1]):
                start -= 1
            while end < len(self.ipa_text)-1 and not self.is_space_or_newline(self.ipa_text[end+1]):
                end += 1

            word = self.ipa_text[start: end+1]#.strip()
            rhyming_words.append(self.words_orig[self.ipa_words.index(word)])
        
        return set(rhyming_words)
    
    def get_rhyme_schemes(self):
        rhyming_words = defaultdict(list)

        for i, vowel_seq in enumerate(self.vowels_by_word):
            rhyming_words[vowel_seq].append(self.words_orig[i])

        return rhyming_words

if __name__ == "__main__":
    text = open("./redefinition_mosdef.txt", 'r').read()
    ipa = open("./redefinition_mosdef.txt.ipa", 'r').read()

    rhyme = RhymeAnalysis(text, ipa)
    rhyme_schemes = rhyme.get_rhyme_schemes()

    # sort rhyme schemes by decreasing number of words in a grouping
    sorted_rhyme_schemes = sorted(rhyme_schemes.items(), key=lambda entry: len(entry[1]), reverse=True)

    for vowel_seq, words in sorted_rhyme_schemes[:10]:
        print("Words with vowel sequence '{0}'".format(vowel_seq))
        print(words)
