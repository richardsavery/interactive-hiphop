import os
import math
import pyttsx3

# import aifc
# from pydub import AudioSegment
import soundfile as sf
# import sounddevice as sd
# import audioread
import numpy as np
from scipy.io.wavfile import write
import random
# from pathlib import Path
import subprocess
# from gtts import gTTS
# import parselmouth
# import matplotlib.pyplot as plt
# import seaborn as sns
import librosa, librosa.display
# from pydub.silence import split_on_silence
# import fleep

note_values = set([1 / 4, 1 / 3, 1 / 2, 2 / 3, 1])

engine = pyttsx3.init()

engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
# engine.setProperty("voice", "english")


def print_voices():
    voices = engine.getProperty("voices")
    for voice in voices:
        print("Voice:")
        print(" - ID: %s" % voice.id)
        print(" - Name: %s" % voice.name)
        print(" - Languages: %s" % voice.languages)
        print(" - Gender: %s" % voice.gender)
        print(" - Age: %s" % voice.age)


def say_phrase(text):
    engine.say(text)
    engine.runAndWait()


def save_and_tokenize(text):
    save_utterance(text, "full.wav")
    for i, word in enumerate(text.split()):
        print(word)
        dir = "./split_audio"
        out_file = dir + "/{0}.wav".format(i)
        print("exporting", out_file)
        save_utterance(word, out_file)
    engine.runAndWait()


# def online_tts(text):
#     print(len(text.split()))
#     tts = gTTS(text, slow=True)
#     tts.save("full.mp3")
#     split_phrase("full.mp3")


# def split_phrase(filename):
#     audio, sr = librosa.load(filename)
#     intervals = librosa.effects.split(audio, top_db=10)
#     print(intervals)
#     print(len(intervals))


def save_utterance(text, filename):

    # using pico2wave (linux)
    # subprocess.call(
    #     ["pico2wave", "--wave", filename, text], cwd=os.path.dirname(os.path.abspath(__file__))
    # )

    # using pyttsx
    engine.save_to_file(text, filename)


def read_aiff(filename):
    print("reading " + filename)
    data, fs = sf.read(filename)
    return (data, fs)


def text_to_rhythm(text, bpm):

    directory = "./split_audio"
    tokenized_audio = []

    # remove old audio
    for file in sorted(os.listdir(directory)):
        if file.endswith(".wav"):
            os.remove(os.path.join(directory, file))

    # create word wav files
    save_and_tokenize(text)
    parseInt = lambda x: int(x[:-4])

    # read files
    path = os.path.dirname(os.path.abspath(__file__)) + "/split_audio"
    print(path)
    print("DIR ", os.listdir(path))
    files = [f for f in os.listdir(path) if f.endswith(".wav")]
    for file in sorted(files, key=parseInt):
        tokenized_audio.append(read_aiff(os.path.join(directory, file)))

    # sample rate
    fs = tokenized_audio[0][1]

    # frames per beat
    fpb = (60 * fs) / bpm

    num_flows = random.randint(1, int((len(tokenized_audio) / 8)))
    flow_groups = np.array_split(np.asarray(tokenized_audio), num_flows)
    print("DIVISIONS: ", [len(x) for x in flow_groups])
    rhythmic_audio = []
    value = None

    for words in flow_groups:
        lengths = [len(x) for x in words]
        average = sum(lengths) / len(lengths)

        # Note: I was planning on replacing this with some logic that chose an
        # appropriate note value instead of just randomly choosing


        # possible_values = set([note_values[2]])
        # for value in note_values:
        #     if abs(value * fpb - average) / average > 0.95:
        #         possible_values.add(value)
        # value = random.choice(list(possible_values))

        # pick a random note vale and remove it from the set
        possible_values = note_values

        if value is not None:
            possible_values -= set([value])
        
        value = random.choice(list(possible_values))
        rhythmic_audio.extend(generic_flow(words, bpm, (value * fpb), adapt=True))
        rhythmic_audio.extend(
            np.zeros(
                int(math.ceil(len(rhythmic_audio) / fpb) * fpb - len(rhythmic_audio))
            )
        )

    rhythmic_audio = punctuate(rhythmic_audio, bpm, fpb)

    sf.write(str(bpm) + ".wav", rhythmic_audio, fs)


def punctuate(audio, bpm, fpb):
    print("LENGTH", len(audio))

    for i in range(int(len(audio) / fpb)):
        print(i * fpb)
        if i % 16 == 15:
            print("empty beat")
            audio = np.insert(audio, int(i * fpb), np.zeros(int(fpb), dtype=int))
    return audio


"""
Helper method to stretch/compress words to a given length
"""


def change_duration(word, length):
    if length > len(word):
        word = np.append(word, np.zeros(int((length - len(word)) / 2), dtype=int))
    return librosa.effects.time_stretch(word, len(word) / length)


"""
Generic flow which stretches all words to given length
"""

def generic_flow(tokenized_audio, bpm, length, adapt=True):
    fs = tokenized_audio[0][1]
    rhythmic_audio = []

    for data, fs in tokenized_audio:
        print("frames for word: ", len(data))
        duration = math.floor(len(data) / length)
        if duration == 0 or not adapt:
            duration = 1
        rhythmic_audio.extend(change_duration(data, duration * length))
    return rhythmic_audio


"""
old flows which can be simulated by passing in the correct value to 
generic_flow

"""

def adapt_quarter_flow(tokenized_audio, bpm):
    fs = tokenized_audio[0][1]
    rhythmic_audio = []

    # frames per beat
    fpb = (60 * fs) / bpm
    print("Frames per beat", fpb)

    for data, fs in tokenized_audio:
        print("frames for word: ", len(data))
        beats = math.ceil(len(data) / fpb)
        data = np.append(data, np.zeros(int((beats * fpb) - len(data)), dtype=int))
        rhythmic_audio.extend(data)
    return rhythmic_audio


"""
A flow which rounds word length to the nearest sixteenth then adds them up
"""

def adapt_sixteenth_flow(tokenized_audio, bpm):
    fs = tokenized_audio[0][1]
    rhythmic_audio = []

    # frames per beat
    fpb = (60 * fs) / bpm
    sixteenths = fpb / 4
    print("Frames per beat", fpb)

    # word lengths
    lengths = [len(x[0]) for x in tokenized_audio]
    # word_durations = [x // sixteenths for x in lengths]
    word_durations = []
    padded_words = []

    for data, fs in tokenized_audio:
        length = math.ceil(len(data) / sixteenths)
        print(data)
        data = np.append(
            data, np.zeros(int((length * sixteenths) - len(data)), dtype=int)
        )
        word_durations.append(length)
        padded_words.append(data)

    total_sixteenths = sum(word_durations)
    measures = math.ceil(total_sixteenths / 16)
    remaining_pads = (measures * 16) - total_sixteenths
    pads_per_word = remaining_pads // len(padded_words)
    for data in padded_words:
        rhythmic_audio.extend(data)
    return rhythmic_audio


"""
Uncomment a line for quick testing
"""
if __name__ == "__main__":
    # text_to_rhythm("I was a fiend, before I had been a teen, I melted microphones instead of cones of ice cream, music orientaded so when hip hop was originated, fitted like pieces of puzzles, complicated", 90)

    text_to_rhythm(
        "Let's trace the hint and check the file. Let's see who bent and detect the style. I flip the script so it cant get foul. At least not now it'll take a while.",
        90,
    )
    
    # say_phrase("Testing the text to speech")

    # print_voices()
    # online_tts(
    #     "Let's trace the hint and check the file. Let's see who bent and detect the style. I flip the script so it cant get foul. At least not now it'll take a while."
    # )

