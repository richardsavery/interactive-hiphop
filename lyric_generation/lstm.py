import numpy as np
from keras.models import Sequential, load_model
from keras.layers import Dense, Embedding, Dropout, LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.callbacks import ModelCheckpoint
import pickle
import os

# from sklearn.preprocessing import LabelEncoder
# from sklearn.preprocessing import OneHotEncoder
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical

from .data_util import get_verses

curr_directory = os.path.dirname(os.path.realpath(__file__))


class LSTM_Generator:
    def __init__(self):
        self.verses = get_verses()
        self.seq_length_pred = 10
        self.model_path = os.path.join(curr_directory, "model.h5")

    def train(self):
        self.max_len = max(map(lambda x: len(x), self.verses))
        self.embed()
        print("----------------------------------------")
        print("Data Loaded")
        print("----------------------------------------")
        self.create_model()
        print("----------------------------------------")
        print("Model Created")
        print("----------------------------------------")
        pickle.dump(self.tokenizer, open("tokenizer.pkl", "wb"))
        self.fit()
        print("----------------------------------------")
        print("Model Trained")
        print("----------------------------------------")
        self.model.save(self.model_path)

    def generate(self, seed, length=100):
        model = load_model(self.model_path)
        tokenizer_path = os.path.join(curr_directory, "tokenizer.pkl")
        tokenizer = pickle.load(open(tokenizer_path, "rb"))
        sequence = seed
        result = []

        while not result or result[-1] != "endverse":
            encoded = tokenizer.texts_to_sequences([sequence])
            encoded = pad_sequences(
                encoded, maxlen=self.seq_length_pred, truncating="pre"
            )
            pred = model.predict(encoded, verbose=0)[0]
            pred_index = np.argmax(pred)
            predWord = tokenizer.index_word[pred_index]
            sequence += " " + tokenizer.index_word[pred_index]
            result.append(predWord)
        return " ".join(result)

    def embed(self):
        # TODO: Use Word2Vec or GloVe to create embeddings for words
        # Pretrained model very large, and takes a long time to load
        self.tokenizer = Tokenizer()
        self.tokenizer.fit_on_texts(self.verses)
        tokenized = self.tokenizer.texts_to_sequences(self.verses)
        self.vocab_size = len(self.tokenizer.word_index) + 1

        # Convert to sequences of length self.seq_length_pred (how many words before to predict)
        length = self.seq_length_pred + 1
        seq = []
        for i, verse in enumerate(tokenized):
            for j in range(1, len(verse)):
                verse_slice = verse[: j + 1]
                padded = pad_sequences([verse_slice], maxlen=length, truncating="pre")
                seq.append(padded[0])
        # for i, verse in enumerate(tokenized):
        #     for j in range(len(verse) - length + 1):
        #         seq.append(verse[j : j + length])
        seq = np.array(seq)
        print(seq)
        self.X, self.y = seq[:, :-1], seq[:, -1]
        self.y = to_categorical(self.y, num_classes=self.vocab_size)
        self.seq_length = self.X.shape[1]

    def create_model(self):
        EMBEDDING_DIM = 100

        self.model = Sequential()
        embedding_layer = Embedding(
            self.vocab_size,
            EMBEDDING_DIM,
            input_length=self.seq_length,
            trainable=True,
            mask_zero=True,
        )
        self.model.add(embedding_layer)
        self.model.add(LSTM(100, return_sequences=True))
        self.model.add(LSTM(100))
        # self.model.add(Dropout(0.2))
        self.model.add(Dense(self.vocab_size, activation="softmax"))
        self.model.compile(loss="categorical_crossentropy", optimizer="adam")
        print(self.model.summary())

    def fit(self):
        checkpoint = ModelCheckpoint(
            os.getcwd(), monitor="val_acc", verbose=1, save_best_only=True, mode="max"
        )
        callbacks_list = [checkpoint]
        self.model.fit(
            self.X, self.y, batch_size=128, epochs=1, callbacks=callbacks_list
        )


def test_model_generation():
    model = LSTM_Generator()
    # seed = input("Seed word/phrase: ")
    seed = "manifest"
    gen = model.generate(seed)
    print(gen)


def test_embed():
    model = LSTM_Generator()
    model.embed()
    print(model.X)
    print(model.y)


def test_model_basic():
    model = LSTM_Generator()
    tokenizer = pickle.load(open(tokenizer_path, "rb"))
    model.create_model()


if __name__ == "__main__":
    # test_embed()
    test_model_generation()
