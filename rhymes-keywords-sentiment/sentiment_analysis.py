from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords 
from pandas import read_excel
import pickle
import sys
import os

class SentimentAnalyzer():
    def __init__(self):
        self.reader = SentimentFileReader()

    def get_valence(self, sample_path):
        sentiment_lexicon_map = self.reader.get_hu_lexicon()
        song_words = self.reader.get_song_words(sample_path)
        scores = self.bag_of_words(sentiment_lexicon_map, song_words)
        return scores['Positive']

    def bag_of_words(self, sentiment_lexicon_map, words):
        sentiments = sentiment_lexicon_map.keys()
        scores = {s: 0 for s in sentiments}

        for word in words:
            for sentiment in sentiments:
                lexicon = sentiment_lexicon_map[sentiment]
                if word in lexicon:
                    scores[sentiment] += 1

        total_scored_words = sum(scores.values())
        scaled_scores = {key: val / total_scored_words for key, val in scores.items()}
        
        return scaled_scores

        
class SentimentFileReader():
    # 6,800 positive and negative words
    # Shouts to Minqing Hu and Bing Liu
    def save_hu_lexicon(self):
        sentiments = ['Positive', 'Negative']
        sentiment_path_map = {
            sentiments[0]: self.get_data_path('hu_positive_lexicon.txt'),
            sentiments[1]: self.get_data_path('hu_negative_lexicon.txt'),
        }
        sentiment_lexicon_map = {s: set() for s in sentiments}

        for sentiment in sentiments:
            path = sentiment_path_map[sentiment]
            lexicon = sentiment_lexicon_map[sentiment]
            with open(path) as file:
                for line in file:
                    word = line.rstrip()
                    lexicon.add(word)
        
        self.save_pickle(sentiment_lexicon_map, 'hu_lexicon.pkl')

        return sentiment_lexicon_map

    def get_hu_lexicon(self):
        return self.load_pickle('hu_lexicon.pkl')


    def save_harvard_lexicon(self):
        sentiments = ['Positiv', 'Negativ', 'Strong', 'Power', 'Weak', 'Submit', \
        'Active', 'Passive', 'Pleasur', 'Pain', 'Feel', 'Arousal', 'EMOT', 'Virtue', \
        'Vice', 'Ovrst', 'Undrst']
        sentiment_lexicon_map = {s: set() for s in sentiments}

        spreadsheet_path = self.get_data_path('harvard_lexicon.xls')
        lexicon_df = read_excel(spreadsheet_path)

        for _, row in lexicon_df.iterrows():
            word = str(row['Entry']).lower()
            if not word.isalpha():
                continue
            for sentiment in sentiments:
                if row[sentiment] == sentiment:
                    lexicon = sentiment_lexicon_map[sentiment]
                    lexicon.add(word)

        self.save_pickle(sentiment_lexicon_map, 'harvard_lexicon.pkl')
        
    # ~12,000 words with a variety of sentiments
    # Credits to Phillip Stone, Harvard 2000
    # 
    # feel free to look through  ./sentiment_analysis_data/harvard_lexicon.xls
    # and add column names to the `sentiments` array
    def get_harvard_lexicon(self):
        return self.load_pickle('harvard_lexicon.pkl')

    def get_song_words(self, song_file_name):
        song = ""
        path =  self.get_data_path(song_file_name)
        with open(path) as f:
            for line in f:
                line = line.rstrip().lower()
                song += line + ' '

        # Remove stop words and non-alphabetical tokens
        stop_words = set(stopwords.words('english'))
        extra_stop_words = ["n't", "'s", "'m", "``", "'", '"', ".", ","]
        for word in extra_stop_words:
            stop_words.add(word)
        song_words = word_tokenize(song)
        song_words = [w for w in song_words if w not in stop_words and w.isalpha()]

        return song_words

    def get_data_path(self, file_name):
        curr_file = os.path.abspath(sys.modules[__name__].__file__)
        curr_dir = os.path.dirname(curr_file)
        data_path = os.path.join(curr_dir, 'sentiment_analysis_data', file_name)
        return data_path

    def save_pickle(self, item, file_name):
        path = self.get_data_path(file_name)
        with open(path, 'wb') as file:
            pickle.dump(item, file)

    def load_pickle(self, file_name):
        path = self.get_data_path(file_name)
        with open(path, 'rb') as file:
            item = pickle.load(file)
        return item


# example use case
def main():
    analyzer = SentimentAnalyzer()
    valence = analyzer.get_valence('who_shot_ya.txt')
    print(valence)

if __name__ == "__main__":
    main()
