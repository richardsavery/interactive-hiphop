import time

import librosa
import os
import pydub
from pydub.silence import split_on_silence
from pydub import AudioSegment
import speech_recognition as sr
import sys
import threading
import transcriber as ts

class TextTranscription:
    def __init__(self, count):
        self.text_segments = [''] * count

class SpeechFileProcessor:
    def __init__(self):
        self._text_segment_lock = threading.Lock()

    def process_audio_file(self, fname, persist=False):
        # Split the audio file into more managable chunks
        split_dir, num_split_files = self._split_silence(fname)
        if num_split_files == 0:
            raise Exception('Could not split audio file {}'.format(fname))
        # initialize text segment array
        self._transcribe_threads = [None] * num_split_files
        transcription = TextTranscription(num_split_files)
        for i, chunk in enumerate(os.listdir(split_dir)):
            chunk_path = os.path.join(split_dir, chunk)
            kwargs = {'chunk_path' : chunk_path, 'i' : i, 'transcription' : transcription}
            self._transcribe_threads[i] = threading.Thread(target=self._transcribe, kwargs=kwargs)
        for thread in self._transcribe_threads:
            thread.start()
        for thread in self._transcribe_threads:
            if thread.is_alive():
                thread.join()
        
        transcribed_text = ' '.join(transcription.text_segments)

        if persist:
            outfname = '{}_transcription.txt'.format(fname)
            with open(outfname, 'w') as f:
                f.write(transcribed_text)
        return transcribed_text
        
    def _split_silence(self, fname):
        sound_file = AudioSegment.from_wav(fname)
        audio_chunks = split_on_silence(sound_file, 
            # must be silent for at least half a second
            min_silence_len=100,

            silence_thresh=-35
        )
        split_dir = "{}_split".format(fname)
        if not os.path.exists(split_dir):
            os.mkdir(split_dir)

        for i, chunk in enumerate(audio_chunks):
            out_file = "{}/chunk{}.wav".format(split_dir, i)
            chunk.export(out_file, format="wav")

        return split_dir, len(audio_chunks)
    
    
    def _transcribe(*args, **kwargs):
        chunk_path = kwargs['chunk_path']
        i = kwargs['i']
        r = sr.Recognizer()
        transcription = kwargs['transcription']
        text = ''
        with sr.AudioFile(chunk_path) as source:
            try:
                audio = r.record(source)
                text = r.recognize_google(audio)
            except:
                return
        transcription.text_segments[i] = text



if __name__ == '__main__':
    fname = sys.argv[1]
    processor = SpeechFileProcessor()
    start_time = time.time()
    transcription = processor.process_audio_file(fname, persist=True)
    print('time taken: {}'.format(time.time() - start_time))
    print(transcription)