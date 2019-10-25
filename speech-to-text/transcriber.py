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
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums

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

    def use_gcp(self, file):
        GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""{
            "type": "service_account",
                "project_id": "srt-editing-1536019242339",
                "private_key_id": "36d75900a4b92525d507bf52a3203def2878f1db",
                "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCk6TVCcNTj39MQ\nfxM/v7Rbt1rY6Qv3FfKH5YeH1v2RXw355oId/6ZwWzUyInla+KIb4hThTmq0H44a\nZAfGqbmLKeJSZxEZB3wsRAFv7hDnw1dRuEdR7U+YXuTC/kqZOYepaxVdNj9ibigz\njcjioyq/McXXcNp9ENYZrMzq4GooC24i6WBEOPTvhIxSAKgazqQfVhSzOHhO1w+d\nhxrsGNLuRXkPOOe5M2RGM9RipAZID8JwfccY/iXSs6KXn1HKR3rR7txsDpUkfKsc\n9RTEl+8ffFWjA8FzRgiJ4DxdUz7UW9wyzQeVGG2+S1IwNhefPAuFdU9FiM0g7vpP\nVlzcA2SRAgMBAAECggEAIKD/57h5dujnUwFBpsBgiDEcKYTa2DWgeiEBEvCH1UaQ\ndlyUbCkUHnD9coD9r/E36fpulTG1zRPdQv19yGH2k0FjRVidOm2PtRZzjlj1QVYW\nJdYnTl98+zHzY117FxwZ6nyEip/cJLaU/7ZTA/yyzYeklH8Ay/QT2JqnJOXoOynO\nZgiSMRiJ4a0yp28AxKPKZiYcHT0SzesVnunxry9tU1C+0igku7b4XEh9MKjinEc7\nYypnPsE0Hy2miTMg2k93LeTYGzdN/XcwIvkcpQ8NE6W39lCkv0tYvyxRTuGIwFjk\nsFqargGlFezO3BLPqkjo3cbem23bfhLyFugDCxE07QKBgQDXxeLuH1Y/5UJMb8Zs\nXVOdBji76aeUFQkCTljFg+7Umz+x00IZOAsqgprAwz2cmhbHDrCyQ2ufoLRUvKdQ\nUidyZnjHKfkRiUhZ0OGxLOVqXFxFZX04p3o3XXX+6xjIQPbuQGECkfJKNF219wDI\nNxp1GGDn5kBXqP6U4CUmrpTY0wKBgQDDp9l86QgotOklPRvOaeZd0+hLMpyZEQn6\ntkPIJbV2reA0qx1Ylfi0QsMKKcDjEpA3LIpI30bamzqYpIGM15LOQGIBRxIdRB31\nDrEPP+OYeJoFJPlGrg/teU96wyLMnZae1Y2Ah1FuoLF6pNm140XpIh94wmaMQKvd\n9vqGr31uiwKBgBbrFOR3/aBByJ33zVqbOxNVotcKxVrsNQ3CppksH0UDzGsl5kJp\nen4kay2IT1X/4+V2wPveP2MwHZdWhmr4nun+yltVMPhU3ZN0pVQ9UYzPjJluYzOO\nTmPtEGhoLjSu+ctqmSM9vz90enOmbbXWbH/9e+WFxlXJRGkpuah3KKYzAoGAUPGb\nB5M83eJiZhaO72ledcjaXGnW4XhsIX3QMvhux2eNzxxPqrt4xdKs8AJwG0EtyrWx\njA5bOMtphYbhVcxFnvCB2zd05gitQBnQ5Jcw6H5UcfZm7nfKfRtn50jdl7tGefWt\ncdQJu3PdmPikXRxmatnEHWiHllSXBeBMqvXlNZsCgYB07H/mZRCvVJK1+mtaSA+w\njp1VIbsuouthyrXaA/y4dg+3qdkeAG7p+uGCZjyCnRT7RiDJkh/ioPlnytISk6Ht\nIf5b4jmB04WwVu5EWGJQzRi2toLw2JAD+iUsdrKbON5uaq95ZClNvAeSCjA82Y5T\n/nRpOcwiQ8E68/bJXq3IAQ==\n-----END PRIVATE KEY-----\n",
                "client_email": "interactive-hiphop@srt-editing-1536019242339.iam.gserviceaccount.com",
                "client_id": "109455511731968078576",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/interactive-hiphop%40srt-editing-1536019242339.iam.gserviceaccount.com"
                }
            """
        r = sr.Recognizer()
        with sr.AudioFile(file) as source:
            audio_fr = r.record(source)  # read the entire audio file
        try:
            print("Google Cloud Speech recognition for \"numero\" with different sets of preferred phrases:")
            print(r.recognize_google_cloud(audio_fr, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, preferred_phrases=["noomarow"]))
            print(r.recognize_google_cloud(audio_fr, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, preferred_phrases=["newmarrow"]))
        except sr.UnknownValueError:
            print("Google Cloud Speech could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Cloud Speech service; {0}".format(e))



    # def text_to_ipa(self, path):
    #     # Use this function if you have a txt file that's in words but need IPA
    #     f = open(path, 'r')
    #     words = f.read()


    # if __name__ == "__main__":
    #     transcribe_audio("sample1.wav")
    # def sample_recognize(self, local_file_path):
    #     """
    #     Transcribe a short audio file using synchronous speech recognition

    #     Args:
    #     local_file_path Path to local audio file, e.g. /path/audio.wav
    #     """

    #     client = speech_v1.SpeechClient()

    #     # local_file_path = 'resources/brooklyn_bridge.raw'

    #     # The language of the supplied audio
    #     language_code = "en-US"

    #     # Sample rate in Hertz of the audio data sent
    #     sample_rate_hertz = 16000

    #     # Encoding of audio data sent. This sample sets this explicitly.
    #     # This field is optional for FLAC and WAV audio formats.
    #     encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    #     config = {
    #         "language_code": language_code,
    #         "sample_rate_hertz": sample_rate_hertz,
    #         "encoding": encoding,
    #     }
    #     with io.open(local_file_path, "rb") as f:
    #         content = f.read()
    #     audio = {"content": content}

    #     response = client.recognize(config, audio)
    #     for result in response.results:
    #         # First alternative is the most probable result
    #         alternative = result.alternatives[0]
    #         print(u"Transcript: {}".format(alternative.transcript))