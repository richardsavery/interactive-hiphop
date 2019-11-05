import markovify
import pronouncing

class MarkovRhymeGenerator:
    def __init__(self, corpus):
        corpus = corpus.lower()
        self._corpus_words = set(corpus.replace('\n', ' ').split(' '))
        self._forward_model = self._initialize_forward_model(corpus)
        self._backward_model = self._initialize_backward_model(corpus)
    
    def _initialize_forward_model(self, corpus):
        return markovify.Text(corpus, state_size=3)

    def _initialize_backward_model(self, corpus):
        reversed_lines = [' '.join(line.split(' ')[::-1]) for line in corpus.split('\n')]
        reversed_corpus = '\n'.join(line for line in reversed_lines)
        return markovify.Text(reversed_corpus, state_size=3)
    
    def _get_rhyming_line(self, word_to_rhyme):
        rhyming_words = pronouncing.rhymes(word_to_rhyme)
        for word in rhyming_words:
            if word in self._corpus_words:
                backwards_line = self._backward_model.make_sentence_with_start(word)
                line = ' '.join(backwards_line.split(' ')[::-1])
                return line
        return None

    
    def generate_line_pair(self):
        first_line = self._forward_model.make_sentence()
        word_to_rhyme = first_line.split(' ')[-1]
        second_line = _get_rhyming_line(word_to_rhyme)
        if second_line is not None:
            return (first_line, second_line)
        return None
    
    def generate_rhyming_line(self, line, word_to_rhyme=None):
        if word_to_rhyme is None:
            word_to_rhyme = line.split(' ')[-1]
        rhyming_line = _get_rhyming_line(word_to_rhyme)
        return rhyming_line
    
    