import os
import math
import pyttsx3
import aifc
from pydub import AudioSegment
import soundfile as sf
import sounddevice as sd
import audioread
import numpy as np
from scipy.io.wavfile import write
import random

import parselmouth
import matplotlib.pyplot as plt
import seaborn as sns
import librosa, librosa.display
# from pydub.silence import split_on_silence
# import fleep

note_values = [1/4, 1/3, 1/2, 2/3, 1]

engine = pyttsx3.init()
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')

def say_phrase(text):
    engine.say(text)
    engine.runAndWait()

def save_and_tokenize(text):
    save_utterance(text, "full.aiff")
    for i, word in enumerate(text.split()):
        print(word)
        out_file = "./split_audio/{0}.aiff".format(i)
        print("exporting", out_file)
        save_utterance(word, out_file)
    engine.runAndWait()

def save_utterance(text, filename):
    engine.save_to_file(text, filename)

def read_aiff(filename):
    print("reading " + filename)
    data, fs = sf.read(filename)
    return (data, fs)

def text_to_rhythm(text, bpm):
    directory = "./split_audio"
    tokenized_audio = []

    #remove old audio
    for file in sorted(os.listdir(directory)):
        if file.endswith(".aiff"):
            os.remove(os.path.join(directory, file))

    #create word aiff files
    save_and_tokenize(text)
    # numeric = lambda x, y: int(x[:-4]) > int(y[:-4])
    parseInt = lambda x: int(x[:-5])
    #read files
    files = [f for f in os.listdir(directory) if f.endswith(".aiff")]
    for file in sorted(files, key=parseInt):
        tokenized_audio.append(read_aiff(os.path.join(directory, file)))
    
    fs = tokenized_audio[0][1]
    fpb = (60 * fs) / bpm

    num_flows = random.randint(1, int((len(tokenized_audio) / 6)))
    flow_groups = np.array_split(np.asarray(tokenized_audio), num_flows)
    rhythmic_audio = []
    for words in flow_groups:
        lengths = [len(x) for x in words]
        average = sum(lengths) / len(lengths)
        possible_values = set([note_values[2]])
        for value in note_values:
            if abs(value * fpb - average) / average > .9:
                possible_values.add(value)
        value = random.choice(list(possible_values))
        rhythmic_audio.extend(generic_flow(words, bpm, (value * fpb), adapt=True))
        rhythmic_audio.extend(np.zeros(int(math.ceil(len(rhythmic_audio)/fpb)*fpb - len(rhythmic_audio))))
    sf.write(str(bpm) + ".wav" , rhythmic_audio, fs)

"""
Helper method to stretch/compress words to a given length
"""
def change_duration(word, length):
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
        if duration == 0 or not adapt: duration = 1
        rhythmic_audio.extend(change_duration(data, duration*length))
    return rhythmic_audio

def adapt_quarter_flow(tokenized_audio, bpm):
    fs = tokenized_audio[0][1]
    rhythmic_audio = []

    #frames per beat
    fpb = (60 * fs) / bpm
    print("Frames per beat", fpb)

    for data, fs in tokenized_audio:
        print("frames for word: ", len(data))
        beats = math.ceil(len(data) / fpb)
        data = np.append(data, np.zeros(int((beats*fpb) - len(data)), dtype=int))
        rhythmic_audio.extend(data)
    return rhythmic_audio


"""
A flow which rounds word length to the nearest sixteenth then adds them up
"""
def adapt_sixteenth_flow(tokenized_audio, bpm):
    fs = tokenized_audio[0][1]
    rhythmic_audio = []

    #frames per beat
    fpb = (60 * fs) / bpm
    sixteenths = fpb / 4
    print("Frames per beat", fpb)

    # word lengths
    lengths = [len(x[0]) for x in tokenized_audio]
    # word_durations = [x // sixteenths for x in lengths]
    word_durations = []
    # print(word_durations)

    padded_words = []
    for data, fs in tokenized_audio:
        length = math.ceil(len(data) / sixteenths)
        print(data)
        data = np.append(data, np.zeros(int((length * sixteenths) - len(data)), dtype=int))
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
Testing Librosa's Onset Detection
"""
def quantize_syllables(tokenized_audio, bpm):
    test_frames, fs = tokenized_audio[1]
    print("length", len(test_frames))
    onset_frames = librosa.onset.onset_detect(test_frames, sr=fs, hop_length=5)
    print(onset_frames) # frame numbers of estimated onsets

def concatenate_segments(x, onset_samples, pad_duration=0.500):
    """Concatenate segments into one signal."""
    silence = numpy.zeros(int(pad_duration*sr)) # silence
    frame_sz = min(numpy.diff(onset_samples))   # every segment has uniform frame size
    return numpy.concatenate([
        numpy.concatenate([x[i:i+frame_sz], silence]) # pad segment with silence
        for i in onset_samples
    ])


text_to_rhythm("Let's trace the hint and check the file. Let's see who bent and detect the style. I flip the script so it cant get foul. At least not now it'll take a while.", 120)

def draw_spectrogram(spectrogram, dynamic_range=70):
    X, Y = spectrogram.x_grid(), spectrogram.y_grid()
    sg_db = 10 * np.log10(spectrogram.values)
    plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
    plt.ylim([spectrogram.ymin, spectrogram.ymax])
    plt.xlabel("time [s]")
    plt.ylabel("frequency [Hz]")

def draw_intensity(intensity):
    plt.plot(intensity.xs(), intensity.values.T, linewidth=3, color='w')
    plt.plot(intensity.xs(), intensity.values.T, linewidth=1)
    plt.grid(False)
    plt.ylim(0)
    plt.ylabel("intensity [dB]")