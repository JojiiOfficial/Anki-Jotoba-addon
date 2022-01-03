from anki.hooks import addHook
from aqt import mw

import json
import requests

# Field constants
SRC_FIELD_NAME = "Expression"
SRC_FIELD_POS = 0

AUDIO_FIELD_NAME = "Audio"
AUDIO_FIELD_POS = 5

POS_FIELD_NAME = "POS"

# API constants
JOTOBA_URL = "http://127.0.0.1:8080"
JOTOBA_API = JOTOBA_URL + "/api"
WORDS_API_URL = JOTOBA_API + "/search/words"
SENTENCE_API_URL = JOTOBA_API + "/search/sentences"

def fill_data(fields, text):
    try:
        word = request_word(text)
    except:
        return
    #print(word)

    if word != None and "audio" in word and fields[AUDIO_FIELD_NAME] == "":
        audio = JOTOBA_URL+word["audio"]
        fields[AUDIO_FIELD_NAME] = f'[sound:{audio}]'

    pos = get_pos(word)
    if fields[POS_FIELD_NAME] == "" and len(pos) > 0:
        fields[POS_FIELD_NAME] = ";".join(pos)

    return True

def request_sentence(text):
    data = '{"query":"' + text + '","language":"English","no_english":false}'
    headers = {"Content-Type": "application/json; charset=utf-8", "Accept":"application/json"}
    res = requests.post(SENTENCE_API_URL, data = data.encode('utf-8'), headers = headers)
    return json.loads(res.text)["sentences"]

def request_word(text):
    data = '{"query":"' + text + '","language":"English","no_english":false}'
    headers = {"Content-Type": "application/json; charset=utf-8", "Accept":"application/json"}
    res = requests.post(WORDS_API_URL, data = data.encode('utf-8'), headers = headers)
    return find_word(json.loads(res.text), text)

def find_word(res, text):
    words=res["words"]
    potential_words = []
    for word in words:
        if word["reading"]["kanji"] == text:
            potential_words.append(word)

    if len(potential_words) != 1:
        return None

    return potential_words[0]


def get_pos(word):
    pos = []
    if word != None and "senses" in word:
        for sense in word["senses"]:
            for keys in sense["pos"]:
                for key in keys.keys():
                    pos.append(key)
        pos = list(dict.fromkeys(pos))
    return pos

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


### Hooks

def add_examples_focusLost(flag, n, fidx):
    src_text = n[SRC_FIELD_NAME]

    if src_text == "":
        return flag

    lookupIdx = []
    for f in [SRC_FIELD_NAME]:
        for c, name in enumerate(mw.col.models.field_names(n.note_type())):
            if name == f:
                lookupIdx.append(c)

    # Not src field
    if fidx not in lookupIdx:
        return flag

    return fill_data(n, src_text)

addHook('editFocusLost', add_examples_focusLost)

def get_audio(editor):
    allFields = editor.note.fields
    src_text = allFields[SRC_FIELD_POS];
    if src_text == "":
        return
    try:
        word = request_word(src_text)
    except:
        return

    if word != None and "audio" in word:
        audio = JOTOBA_URL+word["audio"]
        set_values_on_editor(audio, editor)


def set_values_on_editor(audio, editor):
    audio = editor.urlToFile(audio)
    field_number_of_audio = 5
    allFields = editor.note.fields
    allFields[field_number_of_audio] = f'[sound:{audio}]'
    editor.loadNote()
    editor.web.setFocus()
    editor.web.eval(f'focusField({field_number_of_audio});')
    editor.web.eval('caretToEnd();')

def addMyButton(buttons, editor):
    editor._links['add_audio'] = get_audio
    return buttons + [editor._addButton("", "add_audio", "tooltip", label = "Add Audio")]

addHook("setupEditorButtons", addMyButton)
