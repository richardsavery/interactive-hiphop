import os
import sys
import time
import pydub
import librosa
import threading
import speech_recognition as sr
import transcriber as ts

from pydub import AudioSegment
from pydub.silence import split_on_silence


def transcribe_audio(fname):
    r = sr.Recognizer()
    with sr.AudioFile(fname) as source:
        audio_len = source.DURATION
        print(audio_len)
        chunk_len = audio_len // 10
        for chunk in range(10):
            try:
                audio = r.record(source, duration=chunk_len, offset=chunk * chunk_len)
                print(r.recognize_google(audio))
            except:
                print("errored")
                continue

def split_on_onset(fname):
    chunk_dir = '{}_chunks'.format(fname)

    y, sr = librosa.load(fname)
    print(y)
    print("len of y", len(y))
    print(sr)
    frames = librosa.onset.onset_detect(y=y, sr=60000)
    samples = librosa.frames_to_samples(frames)

    if not os.path.exists(chunk_dir):
        os.mkdir(chunk_dir)
    for i in range(len(samples) - 1):
        chunk = y[samples[i] : samples[i + 1]]
        librosa.output.write_wav('{}_chunks/chunk{}.wav'.format(fname, i), chunk, sr)
    last_chunk = y[samples[-1]:]
    librosa.output.write_wav('{}_chunks/chunk{}.wav'.format(fname, len(frames) - 1), last_chunk, sr)
    return chunk_dir

def split(fname):
    sound_file = AudioSegment.from_wav(fname)
    audio_chunks = split_on_silence(sound_file, 
        # must be silent for at least half a second
        min_silence_len=100,

        # consider it silent if quieter than -16 dBFS
        silence_thresh=-35
    )

    # makes folder to hold chunks
    newname = fname[:-4] + "_chunks"
    try:
        os.mkdir(newname)
    except:
        print("file exists already.")

    # writes chunked audio files into folder
    for i, chunk in enumerate(audio_chunks):
        out_file = newname + "/{0}.wav".format(i)
        chunk.export(out_file, format="wav")


if __name__ == '__main__':
    fname = sys.argv[1]
    start = time.time()
    split(fname)
    mypath = fname[:-4] + "_chunks"
    dir_wav = os.listdir(mypath)
    
    # sorts chunked files in order
    dir_wav.sort(key=lambda x: int(x[:-4]))

    words = []

    # TODO: threading for files?
    # right now, just reads them in a for loop
    # also writes a single text file per chunk

    # for wav in dir_wav:
    #     STT = ts.SpeechToText()
    #     name, words_list = STT.transcribe_audio_file(mypath + "/" + wav)
    #     words += words_list
    print('time taken={}'.format(time.time() - start))
    # print(words_list)