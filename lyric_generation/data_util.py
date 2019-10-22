from os import getcwd
from os.path import dirname, join
import json
import re

DATA_PATH = join(join(dirname(getcwd()), "data"), "verses.json")
START_VERSE_TOKEN = " <startVerse> "
START_LINE_TOKEN = " <startLine> "
END_VERSE_TOKEN = " <endVerse> "
END_LINE_TOKEN = " <endLine> "


def get_verses():
    with open(DATA_PATH, "r") as f:
        data = json.loads(f.read())
    verses = []
    for artist in data.keys():
        for album in data[artist].keys():
            for song in data[artist][album].keys():
                for verse in data[artist][album][song]:
                    verse = add_start_end_tokens(verse)
                    verse = filterVerse(verse)
                    # verses.append(verse.split())
                    verses.append(verse)
    return verses


def filterVerse(verse):
    # Getting rid of anything in paranthesis and commas
    return re.sub("[\(\[].*?[\)\]]", "", verse).replace(",", "")


def add_start_end_tokens(verse):
    verse.append(END_VERSE_TOKEN)
    verse = END_LINE_TOKEN.join(verse).lower()
    return verse
