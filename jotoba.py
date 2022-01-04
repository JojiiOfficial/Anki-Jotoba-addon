import requests
import json

JOTOBA_URL = "https://jotoba.de"
JOTOBA_API = JOTOBA_URL + "/api"
WORDS_API_URL = JOTOBA_API + "/search/words"
SENTENCE_API_URL = JOTOBA_API + "/search/sentences"

def request_sentence(text):
    return json.loads(request(SENTENCE_API_URL, text).text)["sentences"]

def request_word(text, kana = ""):
    return find_word(json.loads(request(WORDS_API_URL, text).text), text, kana)

def request(URL, text):
    data = '{"query":"' + text + '","language":"English","no_english":false}'
    headers = {"Content-Type": "application/json; charset=utf-8", "Accept":"application/json"}
    return requests.post(URL, data = data.encode('utf-8'), headers = headers)

def find_word(res, text, kana = ""):
    words=res["words"]
    potential_words = []
    kana_words = []
    for word in words:
        reading = word["reading"]

        if "kanji" in reading:
            print(text)
            print(kana)
            print(reading)
            if reading["kanji"] == text and (reading["kana"] == kana or kana == ""):
                potential_words.append(word)
            elif reading["kana"] == text:
                kana_words.append(word)
        else:
            if reading["kana"] == text:
                potential_words.append(word)

    if len(potential_words) == 0:
        potential_words = kana_words

    if len(potential_words) != 1:
        return None

    return potential_words[0]

def get_pos(word):
    pos = []
    if word != None and "senses" in word:
        for sense in word["senses"]:
            for keys in sense["pos"]:
                if isinstance(keys, str):
                    pos.append(keys)
                else:
                    for key in keys.keys():
                        pos.append(key)
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

def get_pitch(word) -> None | str:
    if not "pitch" in word:
        return None

    pitch_str = ""
    pitch = word["pitch"]

    for i in pitch:
        part = i["part"];
        high = i["high"];
        if high:
            pitch_str += "↑"
        else:
            pitch_str += "↓"
        pitch_str += part

    if pitch_str == "":
        return None

    return pitch_str

def get_pitch_html(word) -> None | str:
    if word == None or "pitch" not in word:
        return None

    pitch_str = ""
    pitch = word["pitch"]

    p_count = len(pitch)

    for i,p in enumerate(pitch):
        part = p["part"];
        high = p["high"];

        classes = ""

        if high:
            classes += "t"
        else:
            classes += "b"

        if i != p_count -1:
            classes += " r"

        pitch_str += '<span class="pitch {classes}">{part}</span>'.format(classes=classes, part=part)

    if pitch_str == "":
        return None

    return pitch_str

