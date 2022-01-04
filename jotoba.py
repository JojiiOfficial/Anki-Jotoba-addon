import requests
import json

JOTOBA_URL = "https://jotoba.de"
JOTOBA_API = JOTOBA_URL + "/api"
WORDS_API_URL = JOTOBA_API + "/search/words"
SENTENCE_API_URL = JOTOBA_API + "/search/sentences"

def request_sentence(text):
    return json.loads(request(SENTENCE_API_URL, text).text)["sentences"]

def request_word(text):
    return find_word(json.loads(request(WORDS_API_URL, text).text), text)

def request(URL, text):
    data = '{"query":"' + text + '","language":"English","no_english":false}'
    headers = {"Content-Type": "application/json; charset=utf-8", "Accept":"application/json"}
    return requests.post(URL, data = data.encode('utf-8'), headers = headers)

def find_word(res, text):
    words=res["words"]
    potential_words = []
    kana_words = []
    for word in words:
        reading = word["reading"]

        if "kanji" in reading:
            if reading["kanji"] == text:
                potential_words.append(word)
            elif reading["kana"] == text:
                kana_words.append(word)
        else:
            if reading["kana"] == text:
                potential_words.append(word)

    if len(potential_words) == 0:
        potential_words = kana_words

    if len(potential_words) != 1:
        print(len(potential_words))
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

def get_pitch(word) -> str:
    if not "pitch" in word:
        return ""

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

    return pitch_str

