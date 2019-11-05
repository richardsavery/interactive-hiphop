# Markov Chain Rhyming Line Generator

This class exposes an interface to generate rhyming couplets or a rhyming line given the first line.
It expects a newline separated corpus for initialization.

The API is as follows:

`generate_line_pair()` - Generates a rhyming line pair, if possible, based on Markov models of the input corpus.

`generate_rhyming_line(line, word_to_rhyme=None)` - Generates a rhyming line based on either the passed-in line or a single word to rhyme with, if possible. If `word_to_rhyme` is not None, the rhyming line will be generated based on the word, not the line. Otherwise, the rhyming line will be based on the last word of the passed-in line.
