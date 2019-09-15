from os import getcwd
from os.path import dirname, join
import json

DATA_PATH = join(join(dirname(getcwd()), "data"), "verses.json")


def get_verses():
    with open(DATA_PATH, "r") as f:
        data = json.loads(f.read())
    verses = []
    for artist in data.keys():
        for album in data[artist].keys():
            for song in data[artist][album].keys():
                for verse in data[artist][album][song]:
                    verses.append(verse)
    return verses
