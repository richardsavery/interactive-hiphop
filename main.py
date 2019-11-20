import os
import sys
sys.path.append('./speech_to_text')
import json
from time import time


import_start_time = time()
from speech_to_text.record_audio import AudioRecorder
from speech_to_text.transcribe_audio import SpeechFileProcessor
from rhymes_keywords_sentiment.keywordextraction import KeywordExtractor
from rhymes_keywords_sentiment.sentiment_analysis import SentimentAnalyzer
from lyric_generation.lstm import LSTM_Generator
from markov_model_rhymes.markov_rhyme import MarkovRhymeGenerator
from text_to_rhythm.text_to_speech import text_to_rhythm
import_total_time = time() - import_start_time
print("Time for all imports:", import_total_time)

def print_spacer(text):
    print(f"""\n\n\n
***************************************************************************
{text}
***************************************************************************
    """
    )


def main():
    project_directory = os.path.dirname(os.path.realpath(__file__))
    get_data_file_path = lambda filename : os.path.join(project_directory, 'data', filename) 

    # get input lyrics text from audio
    print_spacer("Speech To Text")
    speech_to_text = AudioRecorder()
    input_sound_file = get_data_file_path('speech_test.wav')
    speech_to_text.record_to_file(input_sound_file)

    speech_to_text_start = time()
    speech_file_processor = SpeechFileProcessor()
    processed_input_text_file = speech_file_processor.process_audio_file(input_sound_file, persist=True)

    with open(processed_input_text_file) as f:
        input_lyrics = f.read().lower()

    speech_to_text_total_time = time() - speech_to_text_start
    print('Speech to text time:', speech_to_text_total_time)


    # get keywords from text
    keyword_start_time = time()
    print_spacer("Keyword Extraction")
    keyword_extractor = KeywordExtractor(model="textrank")
    extra_stop_words = ["n't", "'s", "'m", "``", "'", '"', '.', ","]
    keyword_extractor.set_stopwords(extra_stop_words)

    keyword_extractor.analyze(input_lyrics)
    keywords = keyword_extractor.get_keywords(5)
    print('keywords:', keywords)
    keyword_total_time = time() - keyword_start_time
    print("Keyword time: ", keyword_total_time)

    # generate lyrics
    generation_start_time = time()
    print_spacer("Lyric Generation")
    generator = LSTM_Generator()
    output_lyrics = generator.generate(keywords[0])

    generation_total_time = time() - generation_start_time
    print("generation time: ", generation_total_time)


    print_spacer("Generated Lyrics")
    print(output_lyrics.replace('endline', '\n'))

    # generate rhymes
    rhymes_start_time = time()
    print_spacer("Rhyme Generation")
    output_lyrics = output_lyrics.replace('endverse', '')
    output_lines = output_lyrics.split('endline')[:5]
    output_lines_with_rhymes = []

    corpus = json_to_corpus(get_data_file_path('verses.json'))
    rhyme_generator = MarkovRhymeGenerator(corpus)
    for line in output_lines:
        # print(line)
        output_lines_with_rhymes.append(line)
        rhyming_line = rhyme_generator.generate_rhyming_line(line)
        if rhyming_line:
            print('\n****found rhyme****')
            print("Initial line:", line)
            output_lines_with_rhymes.append(rhyming_line)

    rhymes_total_time = time() - rhymes_start_time
    print("rhymes time: ", rhymes_total_time)


    output_lyrics_with_rhymes = "\n".join(output_lines_with_rhymes)

    print("\n\nlyrics with rhymes:")
    print(output_lyrics_with_rhymes)

    # get sentiment from text
    sentiment_start_time = time()
    print_spacer("Sentiment Analysis")
    sentiment_analyzer = SentimentAnalyzer()
    neg_score = sentiment_analyzer.get_negativity(output_lyrics_with_rhymes)
    print('aggresion score =', neg_score)

    sentiment_total_time = time() - sentiment_start_time
    print("sentiment time: ", sentiment_total_time)
    

    # say the words
    text_to_rhythm_start_time = time()
    text_to_rhythm(output_lyrics_with_rhymes, 101)
    text_to_rhythm_total_time = time() - text_to_rhythm_start_time
    print("text_to_rhythm time: ", text_to_rhythm_total_time)

def json_to_corpus(fname):
    with open(fname, 'r') as f:
        lyrics = json.load(f)
    lines = []
    for artist in lyrics:
        for album in lyrics[artist]:
            for song in lyrics[artist][album]:
                for verse in lyrics[artist][album][song]:
                    for line in verse:
                        lines.append(line)

    return'\n'.join(lines)


if __name__ == '__main__':
    main()