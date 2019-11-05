import os
import json

from speech_to_text.transcriber import SpeechToText
from rhymes_keywords_sentiment.keywordextraction import KeywordExtractor
from rhymes_keywords_sentiment.sentiment_analysis import SentimentAnalyzer
from lyric_generation.lstm import LSTM_Generator
from markov_model_rhymes.markov_rhyme import MarkovRhymeGenerator
# from text_to_rhythm.text_to_speech import text_to_rhythm

def print_spacer(text):
    print(f"""\n\n\n
***************************************************************************
{text}
***************************************************************************
    """
    )


def main():
    # get input lyrics text from audio
    print_spacer("Speech To Text")
    audio_path = os.path.join("data", "sample1.wav")
    speech_to_text = SpeechToText()
    input_lyrics_file_path = speech_to_text.transcribe_audio(audio_path)

    input_lyrics_file_path = os.path.join(os.getcwd(), 'speech_to_text', 'sample1.txt')

    with open(input_lyrics_file_path) as f:
        input_lyrics = f.read().lower()

    # get keywords from text
    print_spacer("Keyword Extraction")
    keyword_extractor = KeywordExtractor(model="textrank")
    extra_stop_words = ["n't", "'s", "'m", "``", "'", '"', '.', ","]
    keyword_extractor.set_stopwords(extra_stop_words)

    keyword_extractor.analyze(input_lyrics)
    keywords = keyword_extractor.get_keywords(5)
    print('keywords:', keywords)
    keywords[0] = 'robot'

    # generate lyrics
    print_spacer("Lyric Generation")
    generator = LSTM_Generator()
    output_lyrics = generator.generate(keywords[0])
    output_lyrics = output_lyrics.replace('nigga', 'dude')


    # output_lyrics = "dro endline got jones scars and shots strap out and beat endline taking the microphone man's light for endline so often takin' around or this clothes what they sprinting nigga feeling endline and i wasn't learning she vote we still talking endline i'm on my person i got my own shit endline i'm on ya' own to me 'cause the baby of white mess endline cause i'm living to fuck with me my dollar though endline anybody blow with no tag nigga endline and other boy don't let you grow endline look into a jeep and a wild skin endline all you niggas got pushed and they fuckin' smoke endline and before we come for tomorrow who i know endline i should be smokin' up then andre hit 'em girl i touched them bogus display broken off endline better and all of drug one man 44 and they threw around and endline he said he don't know about it endline 'cause when i actually come on all endline i remember the strap off then then in us endline before i was the shame i got a new life on the sky endline and all i could quit mad g's on me endline it's the new dealer endline who you made me some shit i was a paid endline your momma natural sweet to all endline for my room that they know not it endline i got my own direction endline and i don't know that nigga endline let you pull the lab and go out of chat that endline pull up in my house like a family on the track endline and i don't know that i know endline endverse"

    print_spacer("Generated Lyrics")
    print(output_lyrics.replace('endline', '\n'))

    # generate rhymes
    print_spacer("Rhyme Generation")
    output_lyrics = output_lyrics.replace('endverse', '')
    output_lines = output_lyrics.split('endline')[:5]
    output_lines_with_rhymes = []

    corpus = json_to_corpus('./data/verses.json')
    rhyme_generator = MarkovRhymeGenerator(corpus)
    for line in output_lines:
        # print(line)
        output_lines_with_rhymes.append(line)
        rhyming_line = rhyme_generator.generate_rhyming_line(line)
        if rhyming_line:
            print('\n****found rhyme****')
            print("Initial line:", line)
            print("Rhyming line:", rhyming_line.replace('nigga', 'dude'))
            output_lines_with_rhymes.append(rhyming_line)


    output_lyrics_with_rhymes = "\n".join(output_lines_with_rhymes)
    output_lines_with_rhymes = output_lyrics_with_rhymes.replace('nigga', 'dude')

    # output_lyrics_with_rhymes = """
    # got jones scars and shots strap out and beat

    # thanks!" this fly flow take practice like tae bo with billy blanks to get the paper on the caper heard me in the benz in the backseat
    
    # taking the microphone man's light for
    # so often takin' around or this clothes what they sprinting nigga feeling

    # y'all!) (can i kick it?) as you inhale like a breath of fresh air the game's a pound of that bay area kush it's nothin' we can do this shit right here in front of our building yeah, further, ice and glamorized drug dealing was appealing
    # and i wasn't learning she vote we still talking

    # thanks!" this fly flow take practice like tae bo with billy blanks to get the loot so i can tell him how much i fucking hate you making my eyes ache, stalking
    # """

    print("\n\nlyrics with rhymes:")
    print(output_lyrics_with_rhymes)

    # # get sentiment from text
    print_spacer("Sentiment Analysis")
    sentiment_analyzer = SentimentAnalyzer()
    neg_score = sentiment_analyzer.get_negativity(output_lyrics_with_rhymes)
    print('aggresion score =', neg_score)
    

    # say the words
    # text_to_rhythm(output_lyrics_with_rhymes, 101)

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