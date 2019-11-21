import os
import sys
import wave
import pydub
import pyaudio

import speech_recognition as sr

# only plays an audio file
# doesn't terminate unless manual cancel
def play_wav_file(filename=None):
    CHUNK = 1048576
    if filename == None or filename[-4:] != ".wav":
        print("Invalid File Input")
        print("Terminating...")
        return
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)
    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()

