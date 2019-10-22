from markov import MarkovModel
from lstm import LSTM_Generator


class NoSuchModelException(Exception):
    pass


def generate(modelType, startWord):
    if modelType == "markov":
        model = MarkovModel()
    elif modelType == "lstm":
        model = LSTM()
    else:
        raise NoSuchModelException()
    return model.generate(startWord)


if __name__ == "__main__":
    startWord = input("What do you want to start your rap with?\n > ")
    print("Alright, here's your rap:")
    print(generate("markov", startWord))
