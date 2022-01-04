from .jotoba import *
from .utils import format_furigana

from anki.hooks import addHook
from aqt import mw

# Field constants
SRC_FIELD_NAME = "Expression"
SRC_FIELD_POS = 0

AUDIO_FIELD_NAME = "Audio"
AUDIO_FIELD_POS = 5

MEANING_FIELD_NAME = "Meaning"
MEANING_FIELD_POS = 2

READING_FIELD_NAME = "Reading"
READING_FIELD_POS = 1

POS_FIELD_NAME = "POS"
POS_FIELD_POS = 3

PITCH_FIELD_NAME = "Pitch"
PITCH_FIELD_POS = 13

EXAMPLE_FIELD_PREFIX = "Example "

def fill_data(fields, text, flag):
    if not has_fields(fields):
        return flag
    try:
        reading = fields[READING_FIELD_NAME]
        word = request_word(text, kana = reading)
    except:
        print("Didn't found word")
        return flag

    if word == None:
        print("didn't found #2")
        return flag

    did_change = False

    pos = get_pos(word)
    if fields[POS_FIELD_NAME] == "" and len(pos) > 0:
        fields[POS_FIELD_NAME] = "; ".join(pos)
        did_change = True

    reading = get_katakana(word)
    if fields[READING_FIELD_NAME] == "" and text != reading:
        fields[READING_FIELD_NAME] = reading
        did_change = True

    if fields[MEANING_FIELD_NAME] == "" and gloss_count(word) <= 3:
        glosses = get_glosses(word)
        fields[MEANING_FIELD_NAME] = ", ".join(glosses)
        did_change = True

    pitch = get_pitch_html(word)
    if fields[PITCH_FIELD_NAME] == "" and pitch != None:
        fields[PITCH_FIELD_NAME] = pitch
        did_change = True

    try:
        sentences = request_sentence(text)
        for i, sentence in enumerate(sentences):
            if i > 2:
                break;
            fields[EXAMPLE_FIELD_PREFIX+str(i+1)] = format_furigana(sentence["furigana"]) 
    except:
        print("didn't find sentences")
        pass

    return did_change

# Check whether all fields are available in given note
def has_fields(fields) -> bool:
    for field in [SRC_FIELD_NAME, AUDIO_FIELD_NAME, MEANING_FIELD_NAME, READING_FIELD_NAME, POS_FIELD_NAME, PITCH_FIELD_NAME]:
        if not field in fields:
            return False
    return True

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

    return fill_data(n, src_text, flag)

addHook('editFocusLost', add_examples_focusLost)

from .buttons import init as btn_init
btn_init()
