from typing import Optional, List

import requests
import json
from aqt import mw

config = mw.addonManager.getConfig(__name__)
print(config)

LANGUAGE = config["Language"]
JOTOBA_URL = config["Jotoba_URL"]
WORDS_API_URL = JOTOBA_URL + config["API_Words_Suffix"]
SENTENCE_API_URL = JOTOBA_URL + config["API_Sentence_Suffix"]


class Word:
    expression: str
    reading: str
    glosses: List[str]
    pitch: str
    part_of_speech: List[str]
    audio_url: str

    def __init__(self, word):
        if not word:
            return
        if "kanji" in word["reading"]:
            self.expression = word["reading"]["kanji"]
            self.reading = word["reading"]["kana"]
        else:
            self.expression = word["reading"]["kana"]
            self.reading = ""
        self.pitch = get_pitch_html(word)
        self.glosses = get_glosses(word)
        self.part_of_speech = get_pos(word)
        if "audio" in word:
            self.audio_url = JOTOBA_URL + word["audio"]


def request_sentence(text):
    return json.loads(request(SENTENCE_API_URL, text).text)["sentences"]


def request_word(text, kana=""):
    return find_word(json.loads(request(WORDS_API_URL, text).text), text, kana)


def request(URL, text):
    data = '{"query":"' + text + '","language":"'+LANGUAGE+'","no_english":true}'
    headers = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
    return requests.post(URL, data=data.encode('utf-8'), headers=headers)


def find_word(res, expr, kana="") -> Optional[Word]:
    words = res["words"]
    potential_words = []
    kana_words = []
    for word in words:
        reading = word["reading"]

        if "kanji" in reading:
            if reading["kanji"] == expr and (reading["kana"] == kana or kana == ""):
                potential_words.append(word)
            elif reading["kana"] == expr or reading["kana"] == kana:    # kana word has kanji writing or kanji writing is different from expr
                kana_words.append(word)
        else:
            if reading["kana"] == expr:
                potential_words.append(word)

    if len(potential_words) == 0:
        potential_words = kana_words

    if len(potential_words) != 1 and kana == "":  # esp. multiple hits for word written in kana possible, but also for kanji words with different readings
        return None

    word = Word(potential_words[0])

    return word


def get_pos(word) -> List[str]:
    pos = []
    if word is not None and "senses" in word:
        for sense in word["senses"]:
            for keys in sense["pos"]:
                if isinstance(keys, str):
                    pos.append(keys)
                else:
                    for key in keys.keys():
                        pos.append(key)
                        # if key == "Verb":
                        #    if isinstance(keys[key], str):
                        #        pos.append(keys[key])
                        #    else:
                        #        pos.append(keys[key].keys()[0]) # ?????
        pos = list(dict.fromkeys(pos))
    return pos


def get_katakana(word):
    return word["reading"]["kana"]


def gloss_count(word):
    senses = word["senses"]
    count = 0
    for sense in senses:
        count += len(sense["glosses"])

    return count


def get_glosses(word):
    senses = word["senses"]
    glosses = []
    for sense in senses:
        for gloss in sense["glosses"]:
            glosses.append(gloss)
    return glosses


def get_pitch(word) -> str:
    if not "pitch" in word:
        return ""

    pitch_str = ""
    pitch = word["pitch"]

    for i in pitch:
        part = i["part"]
        high = i["high"]
        if high:
            pitch_str += "↑"
        else:
            pitch_str += "↓"
        pitch_str += part

    if pitch_str == "":
        return ""

    return pitch_str


def get_pitch_html(word) -> str:
    if word is None or "pitch" not in word:
        return ""

    pitch_str = ""
    pitch = word["pitch"]

    p_count = len(pitch)

    for i, p in enumerate(pitch):
        part = p["part"]
        high = p["high"]

        classes = ""

        if high:
            classes += "t"
        else:
            classes += "b"

        if i != p_count - 1:
            classes += " r"

        pitch_str += f'<span class="pitch {classes}">{part}</span>'

    if pitch_str == "":
        return ""

    return pitch_str
