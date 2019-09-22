# Code taken from
# https://github.com/llSourcell/Rap_Lyric_Generator/blob/master/MarkovRap.py
# and modified to fit our data representations

import random, re
from data_util import get_verses


class MarkovModel:
    def __init__(self):
        self.verses = get_verses()
        self.freqDict = {}
        self.probDict = {}
        self.createDict()

    def createDict(self):
        # count frequencies curr -> succ
        for verse in self.verses:
            for curr, succ in zip(verse[1:], verse[:-1]):
                # check if curr is already in the dict of dicts
                if curr not in self.freqDict:
                    self.freqDict[curr] = {succ: 1}
                else:
                    # check if the dict associated with curr already has succ
                    if succ not in self.freqDict[curr]:
                        self.freqDict[curr][succ] = 1
                    else:
                        self.freqDict[curr][succ] += 1

        # compute percentages
        for curr, currDict in self.freqDict.items():
            self.probDict[curr] = {}
            currTotal = sum(currDict.values())
            for succ in currDict:
                self.probDict[curr][succ] = currDict[succ] / currTotal

    def markov_next(self, curr):
        if curr not in self.probDict:
            return random.choice(list(self.probDict.keys()))
        else:
            succProbs = self.probDict[curr]
            randProb = random.random()
            currProb = 0.0
            for succ in succProbs:
                currProb += succProbs[succ]
                if randProb <= currProb:
                    return succ
            return random.choice(list(self.probDict.keys()))

    def makeRap(self, curr, T=50):
        rap = [curr]
        for t in range(T):
            rap.append(self.markov_next(rap[-1]))
        return " ".join(rap)

    def generate(self, startWord):
        return self.makeRap(startWord)

    if __name__ == "__main__":
        rapFreqDict = {}
        rapProbDict = addToDict("lyrics1.txt", rapFreqDict)
        rapProbDict = addToDict("lyrics2.txt", rapFreqDict)

        startWord = input("What do you want to start your rap with?\n > ")
        print("Alright, here's your rap:")
        print(makeRap(startWord, rapProbDict))
