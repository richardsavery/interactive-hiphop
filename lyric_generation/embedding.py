from gensim.test.utils import datapath, get_tmpfile
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec

import pickle

# GLOVE_FILE = "/Users/brianmodel/Desktop/gatech/VIP/interactive-hiphop/lyric_generation/glove.840B.300d.txt"
WORD2VEC_FILE = "/Users/brianmodel/Desktop/gatech/VIP/interactive-hiphop/lyric_generation/GoogleNews-vectors-negative300.bin"


def glove_to_word2vec():
    glove_file = datapath(GLOVE_FILE)
    tmp_file = get_tmpfile(WORD2VEC_FILE)
    _ = glove2word2vec(glove_file, tmp_file)
    # model = KeyedVectors.load_word2vec_format(tmp_file)


def get_embedding():
    return KeyedVectors.load_word2vec_format(WORD2VEC_FILE, binary=True)


model = get_embedding()
with open('word2vec.model', 'wb') as model_file:
    pickle.dump(model, model_file)
print(model)
