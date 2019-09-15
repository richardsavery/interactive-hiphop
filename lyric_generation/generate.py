from hmm import HiddenMarkovModel

hmm = HiddenMarkovModel()

startWord = input("What do you want to start your rap with?\n > ")
print("Alright, here's your rap:")
print(hmm.generate(startWord))
