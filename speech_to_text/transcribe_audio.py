import os
import sys
import time
import pydub
import librosa
import threading
import speech_recognition as sr

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

# if __name__ == '__main__':
#     fname = sys.argv[1]
#     start = time.time()
#     split_on_onset(fname)
#     print('time taken={}'.format(time.time() - start))

def split(fname):
    sound_file = AudioSegment.from_wav(fname)
    audio_chunks = split_on_silence(sound_file, 
        # must be silent for at least half a second
        min_silence_len=100,

        # consider it silent if quieter than -16 dBFS
        silence_thresh=-35
    )
    print(audio_chunks)
    newname = fname[:-4] + "_chunks"
    os.mkdir(newname)

    for i, chunk in enumerate(audio_chunks):

        out_file = newname + "/chunk{0}.wav".format(i)
        print("exporting", out_file)
        chunk.export(out_file, format="wav")