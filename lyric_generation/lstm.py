import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Embedding, Dropout, LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
from keras.preprocessing.text import Tokenizer
from keras.callbacks import ModelCheckpoint
import pickle
import os

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical

from data_util import get_verses, create_data


class LSTM_Generator:
    def __init__(self):
        self.verses = get_verses()
        # self.data = create_data(self.verses)
        self.max_len = max(map(lambda x: len(x), self.verses))
        self.embed()
        print("data done")
        self.create_model()
        print("model created")
        pickle.dump(self.tokenizer, open("tokenizer.pkl", "wb"))
        self.fit()
        self.model.save("model.h5")

    def generate(self, startWord):
        pass

    def embed(self):
        # TODO: Use Word2Vec or GloVe to create embeddings for words
        # Pretrained model very large, and takes a long time to load
        self.tokenizer = Tokenizer()
        self.tokenizer.fit_on_texts(self.verses)
        tokenized = self.tokenizer.texts_to_sequences(self.verses)
        self.vocab_size = len(self.tokenizer.word_index) + 1

        # Convert to sequences of length 10 (how many words before to predict)
        length = 10 + 1
        seq = []
        for i, verse in enumerate(tokenized):
            for j in range(len(verse) - length + 1):
                seq.append(verse[j : j + length])
        seq = np.array(seq)
        self.X, self.y = seq[:, :-1], seq[:, -1]
        self.y = to_categorical(self.y, num_classes=self.vocab_size)
        self.seq_length = self.X.shape[1]

    def create_model(self):
        EMBEDDING_DIM = 100

        self.model = Sequential()
        embedding_layer = Embedding(
            self.vocab_size, EMBEDDING_DIM, input_length=self.seq_length, trainable=True
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
            self.X, self.y, batch_size=128, epochs=100, callbacks=callbacks_list
        )


LSTM_Generator()
