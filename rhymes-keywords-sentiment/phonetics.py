import pronouncing
import ipapy
import re

class PhoneticAnalysis:
    def __init__(self, text, ipa_text):
        self.text = text
        self.ipa_text = ipa_text
        self.vowel_set = set(u'iɪeɛɜæaəɑɒɔʌoʊu') # may be incomplete
        self.vowels = []   # list of vowels from text
        self.vowels_by_word = [] # list of vowels for each word
        self.vowels_idx = []    # indices of vowels in self.text
        self.word_ends_idx = [] # list of indices pointing to word ends
        self.words = [] # ipa words
        self.clean_text()
        self.words_orig = self.text.split() # plaintext words
        self.compute_vowel_representation()

    def add_text(self, text, ipa):
        if type(text) is list:
            text = " ".join(text)
        if type(ipa) is list:
            ipa = " ".join(ipa)
        self.text += " " + text
        self.ipa_text += " " + ipa
        self.words_orig.extend(text.split())
        self.clean_text()
        self.compute_vowel_representation_batch(ipa)
    
    def is_space_or_newline(self, char):
        return char == ' ' or char == '\n'
    
    def is_vowel(self, char):
        return char in self.vowel_set

    def is_consonant(self, char):
        return not self.is_vowel(char) and not self.is_space_or_newline(char)

    def clean_text(self):
        # Remove punctuation and line breaks
        self.text = re.sub(r'[\.,\n]', ' ', self.text)
        self.ipa_text = re.sub(r'[\.,\n]', ' ', self.ipa_text)

    def compute_vowel_representation_batch(self, ipa):
        prev_space_idx = -1 # Index of the previous space char
        line_idx = 0 # Line index of the current character
        new_word_vowels = ""
        for i in range(len(ipa)):
            ch = ipa[i]

            if self.is_vowel(ch):
                self.vowels.append(ch)
                self.vowels_idx.append(i)
                new_word_vowels += ch
            elif self.is_consonant(ch):
                if new_word_vowels and new_word_vowels[-1] != ":":
                    new_word_vowels += ":"
            elif i == len(ipa)-1 or self.is_space_or_newline(ch):
                if len(self.vowels) > 0 and not self.is_space_or_newline(ipa[i-1]):
                    word = ipa[prev_space_idx+1: i+1]
                    
                    self.word_ends_idx.append(i-1)

                    self.words.append(word)
                    if new_word_vowels and new_word_vowels[-1] == ":":
                        new_word_vowels = new_word_vowels[:-1]
                    self.vowels_by_word.append(new_word_vowels)
                    new_word_vowels = ""
                prev_space_idx = i

    def compute_vowel_representation(self):
        self.compute_vowel_representation_batch(self.ipa_text)
                

if __name__ == "__main__":
    text = open("./redefinition_mosdef.txt").read()
    ipa = open("./redefinition_mosdef.txt.ipa", 'r').read()
    ph = PhoneticAnalysis(text, ipa)
    ph.compute_vowel_representation()
    print(ph.vowels_by_word)