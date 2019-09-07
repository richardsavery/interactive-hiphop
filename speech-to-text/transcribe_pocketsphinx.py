import io
import os
import sys
import wave
import pydub
import pyaudio
import speech_recognition as sr

from pocketsphinx import AudioFile


def transcribe_audio(audio_file=None):
    if audio_file == None:
        print("Invalid Param, Terminating...")
        return
    elif audio_file[-4:] == '.mp3':
        sound = AudioSegment.from_mp3(audio_file)
        sound.export(audio_file, format="wav")
        audio_file = audio_file[-4:] + ".wav"
    elif audio_file[-4:] != '.wav':
        print("Invalid Param, Terminating...")
        return

    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    print("Sphinx thinks you said \n\n")
    returnedSpeech = str(r.recognize_sphinx(audio))

    wordsList = returnedSpeech.split()
    print(returnedSpeech)
    print("\n")
    print(wordsList)
    # print("predicted loacation of start ", float(wordsList.index("the")) * 0.3)
    

if __name__ == "__main__":
    transcribe_audio("sample1.wav")
    # transcribe_audio("Post_Malone_Goodbyes.wav")
