import io
import os
import sys
import wave
import pydub
import pyaudio
import eng_to_ipa as ipa
import speech_recognition as sr
# from pocketsphinx import AudioFile
from sys import byteorder
from array import array
from struct import pack
# from google.cloud import speech_v1
# from google.cloud.speech_v1 import enums
import transcribe_audio as ta

import pyaudio
import wave

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

class AudioRecorder:

    def __init__(self, microphone=None):
        self.found_invalid = False
        mics = sr.Microphone.list_microphone_names()
        print("Available recording devices:")
        for i, mic in enumerate(mics):
            print(f'{i}: {mic}')
        self.microphone = int(input("Enter the index of the recording device: "))
        

    def set_mic(self):
        print(sr.Microphone.list_microphone_names())
        self.microphone = int(input("Enter the index of the new recording device: "))
    
    def transcribe_audio_file(self, audio_file=None):
        # this transcribes an existing audio file
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
        print("Google thinks you said:  ")

        try:
            returnedSpeech = str(r.recognize_google(audio))
            self.found_invalid = False
        except:
            print("Unidentified token in ", audio_file)
            returnedSpeech = ""
            self.found_invalid = True
        file_name = audio_file[:-4] + ".txt"
        if not self.found_invalid:
            audio_text_file = open(file_name, "a")
            audio_text_file.write(returnedSpeech)
            audio_text_file.close()

        wordsList = returnedSpeech.split()
        print(returnedSpeech + "\n")
        # print("predicted loacation of start ", float(wordsList.index("the")) * 0.3)
        return file_name, wordsList
        
    def write_as_IPA(self, file_name):
        # this writes a text file as another IPA text file
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

    def find_IPA_chars(self, file):
        "Takes IPA file and finds all unique sounds"
        if file[-7:] == "IPA.txt":
            f = open(file, "r")
            words = f.read()
            IPA = []
            for char in words:
                if char not in IPA and char.isalpha():
                    IPA.append(char)
            return IPA

    def most_common_phoneme_in_line(self, file, only_vowels=False):
        "Finds the most commonly occurring phoneme in a rap line and assumes it is the rhyme of it"
        ""
        import collections
        if file[-7:] == "IPA.txt":
            f = open(file, "r")
            lines = f.readlines()
            for line in lines:
                d = collections.defaultdict(int)
                for c in line:
                    if not only_vowels:
                        if c.isalpha():
                            d[c] += 1
                    else:
                        if c.isalpha() and c in ["ə", "e", "ɑ", "æ", "ɔ", "ɛ", "ɪ", "ʊ", "u", "i"]:
                            d[c] += 1
                print(line[:-2] + ":  " + str(sorted(d.items(), key=lambda x: x[1], reverse=True)[0]))
        pass

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
        try:
            stream = p.open(
                format=FORMAT, 
                channels=1, 
                rate=RATE,
                input=True, 
                input_device_index=self.microphone,
                output=True,
                frames_per_buffer=CHUNK_SIZE)
        except OSError:
            print("Invalid Audio Input Source. Switch input and call function again.\n")
            self.set_mic()
            return
        print("\nRECORDING IN PROGRESS...")

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

            if snd_started and num_silent > 80:
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
        val = self.record()
        if val == None:
            return
        sample_width, data = val
        data = pack('<' + ('h'*len(data)), *data)

        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()

        self.transcribe_audio_file(path)
        self.write_as_IPA(path)
        return(path)

    def recognize_google(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Speak Anything...")
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                print("You said \n{}".format(text))
            except:
                print("Could not recognize voice")

    # def text_to_ipa(self, path):
    #     # Use this function if you have a txt file that's in words but need IPA
    #     f = open(path, 'r')
    #     words = f.read()


if __name__ == "__main__":
    a = SpeechToText()
    b = ta.SpeechFileProcessor()
    fname = str(sys.argv[1]) # records to this file
    a.record_to_file(fname)
    print(b.process_audio_file(fname))