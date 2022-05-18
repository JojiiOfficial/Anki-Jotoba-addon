from typing import Optional, List

import requests
import json

JOTOBA_URL = "https://jotoba.de"
JOTOBA_API = JOTOBA_URL + "/api"
WORDS_API_URL = JOTOBA_API + "/search/words"
SENTENCE_API_URL = JOTOBA_API + "/search/sentences"


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
        self.expression = word["reading"]["kanji"]
        if self.expression is None:
            self.expression = word["reading"]["kana"]
        else:
            self.reading = word["reading"]["kana"]
        self.pitch = get_pitch_html(word)
        self.glosses = get_glosses(word)
        self.part_of_speech = get_pos(word)
        self.audio_url = JOTOBA_URL + word["audio"]


def request_sentence(text):
    return json.loads(request(SENTENCE_API_URL, text).text)["sentences"]


def request_word(text, kana=""):
    return find_word(json.loads(request(WORDS_API_URL, text).text), text, kana)


def request(URL, text):
    data = '{"query":"' + text + '","language":"English","no_english":false}'
    headers = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
    return requests.post(URL, data=data.encode('utf-8'), headers=headers)


def find_word(res, text, kana="") -> Optional[Word]:
    words = res["words"]
    potential_words = []
    kana_words = []
    for word in words:
        reading = word["reading"]

        if "kanji" in reading:
            if reading["kanji"] == text and (reading["kana"] == kana or kana == ""):
                potential_words.append(word)
            elif reading["kana"] == text:
                kana_words.append(word)
        else:
            if reading["kana"] == text:
                potential_words.append(word)

    if len(potential_words) == 0:
        potential_words = kana_words

    if len(potential_words) != 1:  # esp. multiple hits for word written in kana possible, but also for kanji words with different readings
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
                        #if isinstance(keys[key], str):
                        #    pos.append(key)
                        #else:
                        #    pos.append(key.keys()[0])
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
