from phonetics import PhoneticAnalysis
from collections import defaultdict

class RhymeAnalysis(PhoneticAnalysis):
    def __init__(self, text, ipa_text):
        super().__init__(text, ipa_text)
        # self.clean_text()
        # self.words_orig = self.text.split()
        # self.compute_vowel_representation()

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
            rhyming_words.append(self.words_orig[self.words.index(word)])
        
        return set(rhyming_words)
    
    def get_rhyme_schemes(self, min_suffix_length=None):

        rhyming_words = defaultdict(list)

        for i, vowel_seq in enumerate(self.vowels_by_word):
            rhyming_words[vowel_seq].append(self.words_orig[i])

        if min_suffix_length is not None:
            return self.merge_rhyme_schemes_by_suffix(rhyming_words, min_suffix_length)

        return rhyming_words

    def merge_rhyme_schemes_by_suffix(self, rhyming_words, min_suffix_length):
        if min_suffix_length <= 0:
            raise ValueError('Suffix length must be positive')

        res = defaultdict(list)
        # print(rhyming_words)
        sorted_words = sorted(rhyming_words.items(), key=lambda entry: len(entry[0]), reverse=True)
        # print(sorted_words)
        for vowel_seq, words in sorted_words:
            vowels = vowel_seq.split(":")
            suffix = ":".join(vowels[-min_suffix_length:])

            if vowel_seq in res:
                res[vowel_seq].extend(words)
            else:
                res[suffix].extend(words)
            
        return res

    def get_rhyming_score(self, min_suffix_length=None):
        rhyme_schemes = self.get_rhyme_schemes(min_suffix_length=min_suffix_length)

        num_rhyming_words = 0

        for vowel_seq in rhyme_schemes:
            words = rhyme_schemes[vowel_seq]
            if len(words) > 1:
                num_rhyming_words += len(words)
        
        return float(num_rhyming_words) / len(self.words_orig)

def sort_rhyme_scheme_dict(rhyme_schemes):
    return sorted(rhyme_schemes.items(), key=lambda entry: len(entry[1]), reverse=True)

def print_rhyme_schemes(rhyme_schemes, min_seq_length=2, min_num_rhymes=2, suffixes=False):
    """
    min_seq_length: minimum number of syllables in the vowel sequence
    min_num_rhymes: minimum number of rhyming words for a given sequence
    """
    for vowel_seq, words in rhyme_schemes:
        if len(vowel_seq.split(":")) < min_seq_length:
            # ignore ':' symbol, we want multi-syllable rhymes
            continue
        if len(words) < min_num_rhymes:
            continue
        if suffixes:
            print("Words with vowel suffix '{0}':".format(vowel_seq))
        else:
            print("Words with vowel sequence '{0}':".format(vowel_seq))
        print(words)

def run_test():
    mosdef_text = open("./redefinition_mosdef.txt", 'r').read()
    mosdef_ipa = open("./redefinition_mosdef.txt.ipa", 'r').read()

    rhyme = RhymeAnalysis(mosdef_text, mosdef_ipa)
    rhyme_schemes = rhyme.get_rhyme_schemes()

    # sort rhyme schemes by decreasing number of words in a grouping
    rhyme_schemes = sort_rhyme_scheme_dict(rhyme_schemes)

    print("Re:Definition - Mos Def")
    print_rhyme_schemes(rhyme_schemes)

    rakim_text = open("./microphone_fiend.txt", 'r').read()
    rakim_ipa = open("./microphone_fiend.txt.ipa", 'r').read()

    rhyme2 = RhymeAnalysis(rakim_text, rakim_ipa)
    rhyme_schemes2 = rhyme2.get_rhyme_schemes()

    rhyme_schemes2 = sort_rhyme_scheme_dict(rhyme_schemes2)

    print("\nMicrophone Fiend - Rakim")
    print_rhyme_schemes(rhyme_schemes2)

def run_test_batch():
    text_lines = open("./redefinition_mosdef.txt", 'r').readlines()
    ipa_lines = open("./redefinition_mosdef.txt.ipa", 'r').readlines()

    # sort_rhymes = lambda rhyme_schemes: sorted(rhyme_schemes.items(), key=lambda entry: len(entry[1]), reverse=True)

    ra = RhymeAnalysis(text=text_lines[0], ipa_text=ipa_lines[0])
    rhyme_schemes = sort_rhyme_scheme_dict(ra.get_rhyme_schemes())

    print("Only line 1")
    print_rhyme_schemes(rhyme_schemes)

    ra.add_text(text_lines[1], ipa_lines[1])
    rhyme_schemes = sort_rhyme_scheme_dict(ra.get_rhyme_schemes())

    print("\nLines 1-2")
    print_rhyme_schemes(rhyme_schemes)

    ra.add_text(text_lines[2:4], ipa_lines[2:4])
    rhyme_schemes = sort_rhyme_scheme_dict(ra.get_rhyme_schemes())

    print("\nLines 1-4")
    print_rhyme_schemes(rhyme_schemes)

    ra.add_text(text_lines[4:], ipa_lines[4:])
    rhyme_schemes = sort_rhyme_scheme_dict(ra.get_rhyme_schemes())

    print("\nAll lines")
    print_rhyme_schemes(rhyme_schemes)

def run_test_suffixes():
    mosdef_text = open("./redefinition_mosdef.txt", 'r').read()
    mosdef_ipa = open("./redefinition_mosdef.txt.ipa", 'r').read()

    rhyme = RhymeAnalysis(mosdef_text, mosdef_ipa)
    rhyme_schemes = rhyme.get_rhyme_schemes()

    # sort rhyme schemes by decreasing number of words in a grouping
    rhyme_schemes = sort_rhyme_scheme_dict(rhyme_schemes)

    print("Re:Definition - Mos Def")
    print_rhyme_schemes(rhyme_schemes)
    
    print('\nSuffixes')
    suffixes = rhyme.get_rhyme_schemes(min_suffix_length=2)
    sorted_suffixes = sort_rhyme_scheme_dict(suffixes)
    print_rhyme_schemes(sorted_suffixes, suffixes=True)

    print(rhyme.get_rhyming_score())

def run_test_comprehensive():
    print("Re:Definition - Mos Def\n")

    mosdef_text = open("./redefinition_mosdef.txt", 'r').read()
    mosdef_ipa = open("./redefinition_mosdef.txt.ipa", 'r').read()

    rhyme_mos = RhymeAnalysis(mosdef_text, mosdef_ipa)
    rhyme_schemes = rhyme_mos.get_rhyme_schemes()

    # sort rhyme schemes by decreasing number of words in a grouping
    rhyme_schemes = sort_rhyme_scheme_dict(rhyme_schemes)

    print_rhyme_schemes(rhyme_schemes)

    rhyme_score = rhyme_mos.get_rhyming_score()
    print('\nRhyme score: {0}'.format(rhyme_score))
    
    print('\nSuffixes')
    suffixes = rhyme_mos.get_rhyme_schemes(min_suffix_length=2)
    sorted_suffixes = sort_rhyme_scheme_dict(suffixes)
    print_rhyme_schemes(sorted_suffixes, suffixes=True)

    rhyme_score = rhyme_mos.get_rhyming_score(min_suffix_length=2)
    print('\nRhyme score: {0}'.format(rhyme_score))

    print('\n==========\n')

    print("Rakim - Microphone Fiend")

    rakim_text = open("./microphone_fiend.txt", 'r').read()
    rakim_ipa = open("./microphone_fiend.txt.ipa", 'r').read()

    rhyme_rak = RhymeAnalysis(rakim_text, rakim_ipa)
    rhyme_schemes = rhyme_rak.get_rhyme_schemes()
    rhyme_schemes = sort_rhyme_scheme_dict(rhyme_schemes)

    print_rhyme_schemes(rhyme_schemes)

    rhyme_score = rhyme_rak.get_rhyming_score()
    print('\nRhyme score: {0}'.format(rhyme_score))

    print('\nSuffixes')
    suffixes = rhyme_rak.get_rhyme_schemes(min_suffix_length=2)
    sorted_suffixes = sort_rhyme_scheme_dict(suffixes)
    print_rhyme_schemes(sorted_suffixes, suffixes=True)

    rhyme_score = rhyme_rak.get_rhyming_score(min_suffix_length=2)
    print('\nRhyme score: {0}'.format(rhyme_score))

if __name__ == "__main__":
    run_test_comprehensive()