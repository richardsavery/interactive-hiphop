import io
import os
import sys
import wave
import pydub
import pyaudio
import eng_to_ipa as ipa
import speech_recognition as sr
from pocketsphinx import AudioFile
from sys import byteorder
from array import array
from struct import pack

import pyaudio
import wave

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

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
            ipa_file_name = file_name[:-4] + "_IPA.txt"
            ipa_text_file = open(ipa_file_name, "w")

            lines = reader.readlines()
            for line in lines:
                converted = ipa.convert(line)
                ipa_text_file.write(converted + "\n")

            reader.close()
            ipa_text_file.close()
        except:
            return "Error in Reading File"
        
        return ipa_file_name

    def is_silent(self, snd_data):
        "Returns 'True' if below the 'silent' threshold"
        return max(snd_data) < THRESHOLD

    def normalize(self, snd_data):
        "Average the volume out"
        MAXIMUM = 16384
        times = float(MAXIMUM)/max(abs(i) for i in snd_data)

        r = array('h')
        for i in snd_data:
            r.append(int(i*times))
        return r

    def trim(self, snd_data):
        "Trim the blank spots at the start and end"
        def _trim(snd_data):
            snd_started = False
            r = array('h')

            for i in snd_data:
                if not snd_started and abs(i)>THRESHOLD:
                    snd_started = True
                    r.append(i)

                elif snd_started:
                    r.append(i)
            return r

        # Trim to the left
        snd_data = _trim(snd_data)

        # Trim to the right
        snd_data.reverse()
        snd_data = _trim(snd_data)
        snd_data.reverse()
        return snd_data

    def add_silence(self, snd_data, seconds):
        "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
        r = array('h', [0 for i in range(int(seconds*RATE))])
        r.extend(snd_data)
        r.extend([0 for i in range(int(seconds*RATE))])
        return r

    def record(self):
        """
        Record a word or words from the microphone and 
        return the data as an array of signed shorts.

        Normalizes the audio, trims silence from the 
        start and end, and pads with 0.5 seconds of 
        blank sound to make sure VLC et al can play 
        it without getting chopped off.
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=1, rate=RATE,
            input=True, output=True,
            frames_per_buffer=CHUNK_SIZE)

        num_silent = 0
        snd_started = False

        r = array('h')

        while 1:
            # little endian, signed short
            snd_data = array('h', stream.read(CHUNK_SIZE))
            if byteorder == 'big':
                snd_data.byteswap()
            r.extend(snd_data)

            silent = self.is_silent(snd_data)

            if silent and snd_started:
                num_silent += 1
            elif not silent and not snd_started:
                snd_started = True

            if snd_started and num_silent > 60:
                break

        sample_width = p.get_sample_size(FORMAT)
        stream.stop_stream()
        stream.close()
        p.terminate()

        r = self.normalize(r)
        r = self.trim(r)
        r = self.add_silence(r, 0.5)
        return sample_width, r

    def record_to_file(self, path):
        # Records from the microphone and outputs the resulting data to 'path'
        # USE THIS FUNCTION!!!!!
        sample_width, data = self.record()
        data = pack('<' + ('h'*len(data)), *data)

        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()

        self.transcribe_audio(path)
        self.write_as_IPA(path)

    # def text_to_ipa(self, path):
    #     # Use this function if you have a txt file that's in words but need IPA
    #     f = open(path, 'r')
    #     words = f.read()


    # if __name__ == "__main__":
    #     transcribe_audio("sample1.wav")
