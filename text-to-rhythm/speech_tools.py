import pyttsx3
from pydub import AudioSegment
from pydub.silence import split_on_silence
import fleep


engine = pyttsx3.init()
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')

def save_and_tokenize(text):
    save_utterance(text, "full.aiff")
    for i, word in enumerate(text.split()):
        print(word)
        out_file = "./split_audio/word{0}.aiff".format(i)
        print("exporting", out_file)
        save_utterance(word, out_file)
    engine.runAndWait()

def save_utterance(text, filename):
    engine.save_to_file(text, filename)

def tokenize_audio(filename):
    sound_file = AudioSegment.from_wav(filename)
    words = split_on_silence(sound_file, 
        # must be silent for at least 50ms
        min_silence_len=50,
        # consider it silent if quieter than -20 dBFS
        silence_thresh=-20)

    for i, word in enumerate(words):

        out_file = "./split_audio/word{0}.aiff".format(i)
        print("exporting", out_file)
        word.export(out_file, format="aiff")
# save_and_tokenize("test I am a robot and I can rap") 