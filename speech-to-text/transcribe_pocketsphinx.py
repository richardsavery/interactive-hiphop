import io
import os
import sys
import wave
import pydub
import pyaudio
import eng_to_ipa as ipa
import speech_recognition as sr

from pocketsphinx import AudioFile


class SpeechToText:

    def __init__(self, audiofile=None):
        self.audiofile = audiofile
    
    def transcribe_audio(self, audio_file=None):
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

        file_name = audio_file[:-4] + ".txt"
        audio_text_file = open(file_name, "w")
        audio_text_file.write(returnedSpeech)
        audio_text_file.close()

        wordsList = returnedSpeech.split()
        print(returnedSpeech)
        print("\n")
        print(wordsList)
        # print("predicted loacation of start ", float(wordsList.index("the")) * 0.3)
        return file_name
        
    def write_as_IPA(self, file_name):
        if file_name[-4:] == ".wav":
            file_name = file_name[:-4] + ".txt"

        try:
            reader = open(file_name, "r")
            lines = reader.read()
            converted = ipa.convert(lines)
            reader.close()
        except:
            return "Error in Reading File"

        ipa_file_name = file_name[:-4] + "_IPA.txt"
        ipa_text_file = open(ipa_file_name, "w")
        ipa_text_file.write(converted)
        ipa_text_file.close()
        
        return ipa_file_name

    # if __name__ == "__main__":
    #     transcribe_audio("sample1.wav")
