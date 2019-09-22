import pyttsx3
# from pydub import AudioSegment
# from pydub.silence import split_on_silence
# import fleep


engine = pyttsx3.init()
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')

def say_phrase(text):
    engine.say(text)
    engine.runAndWait()

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

save_and_tokenize("test I am a robot and I can rap") 