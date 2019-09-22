import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Embedding, Dropout, LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils

from data_util import get_verses


class LSTM:
    def __init__(self):
        self.verses = get_verses()
        self.max_len = max(map(len, self.verses))
        self.create_model()

    def generate(self, startWord):
        pass

    def embed(self):
        pass

    def create_model(self):
        self.model = Sequential()
        embedding_layer = Embedding(
            input_dim=len(word_index) + 1,
            output_dim=EMBEDDING_DIM,
            weights=[embedding_matrix],
            input_length=MAX_SEQUENCE_LENGTH,
            trainable=True,
        )
        self.model.add(embedding_layer)
        self.model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2])))
        # self.model.add(Dropout(0.2))
        self.model.add(Dense(y.shape[1], activation="softmax"))
        self.model.compile(loss="categorical_crossentropy", optimizer="adam")

    def fit(self):
        pass
