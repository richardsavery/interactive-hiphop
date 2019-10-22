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
        self.words = []
    
    def is_space_or_newline(self, char):
        return char == ' ' or char == '\n'
    
    def is_vowel(self, char):
        return char in self.vowel_set

    def clean_text(self):
        # Remove punctuation and line breaks
        self.text = re.sub(r'[\.,\n]', ' ', self.text)
        self.ipa_text = re.sub(r'[\.,\n]', ' ', self.ipa_text)

    def compute_vowel_representation(self):
        prev_space_idx = -1 # Index of the previous space char
        line_idx = 0 # Line index of the current character
        new_word_vowels = ""
        for i in range(len(self.ipa_text)):
            ch = self.ipa_text[i]

            if self.is_vowel(ch):
                self.vowels.append(ch)
                self.vowels_idx.append(i)
                new_word_vowels += ch
            elif i == len(self.ipa_text)-1 or self.is_space_or_newline(ch):
                if len(self.vowels) > 0 and not self.is_space_or_newline(self.ipa_text[i-1]):
                    word = self.ipa_text[prev_space_idx+1: i+1]
                    # word = self.ipa_text[prev_space_idx+1 : self.vowels_idx[-1] + 1]
                    
                    self.word_ends_idx.append(i-1)
                    # self.word_ends_idx.append(len(self.vowels)-1)

                    self.words.append(word)
                    self.vowels_by_word.append(new_word_vowels)
                    new_word_vowels = ""
                prev_space_idx = i

if __name__ == "__main__":
    f = open("../speech-to-text/sample1_IPA.txt", 'r').read()
