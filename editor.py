from anki.notes import Note
from aqt import mw, gui_hooks
from aqt.utils import showInfo

from .jotoba import *
from .utils import format_furigana

# Field constants
SRC_FIELD_NAME = "Expression"
SRC_FIELD_POS = 0

READING_FIELD_NAME = "Reading"
READING_FIELD_POS = 1

MEANING_FIELD_NAME = "Meaning"
MEANING_FIELD_POS = 2

POS_FIELD_NAME = "POS"
POS_FIELD_POS = 3

AUDIO_FIELD_NAME = "Audio"
AUDIO_FIELD_POS = 5

PITCH_FIELD_NAME = "Pitch"
PITCH_FIELD_POS = 13

EXAMPLE_FIELD_PREFIX = "Example "

ALL_FIELDS = [SRC_FIELD_NAME, MEANING_FIELD_NAME, READING_FIELD_NAME, POS_FIELD_NAME, PITCH_FIELD_NAME,
              EXAMPLE_FIELD_PREFIX + "1", EXAMPLE_FIELD_PREFIX + "2", EXAMPLE_FIELD_PREFIX + "3"]


def fill_data(note: Note, text: str, flag: bool):
    if not has_fields(note):
        return flag

    need_update = False
    for field_i in ALL_FIELDS:
        if note[field_i] == "":
            need_update = True
            break

    if not need_update:
        return flag

    try:
        reading = note[READING_FIELD_NAME]
        word = request_word(text, kana=reading)
    except:  # error while fetching word
        return flag

    if word is None:
        return flag

    did_change = False

    note[SRC_FIELD_NAME] = word.expression

    note[POS_FIELD_NAME] = "; ".join(word.part_of_speech)

    note[READING_FIELD_NAME] = word.reading

    note[MEANING_FIELD_NAME] = "; ".join(word.glosses[:3])

    note[PITCH_FIELD_NAME] = word.pitch

    try:
        sentences = request_sentence(text)
        for i, sentence in enumerate(sentences):
            if i > 2:
                break

            field_name = EXAMPLE_FIELD_PREFIX + str(i + 1)
            if note[field_name] != "":
                continue

            note[field_name] = format_furigana(sentence["furigana"])
    except:
        print("didn't find sentences")
        pass

    return did_change


# Check whether all fields are available in given note
def has_fields(note) -> bool:
    for field in [SRC_FIELD_NAME, AUDIO_FIELD_NAME, MEANING_FIELD_NAME, READING_FIELD_NAME, POS_FIELD_NAME,
                  PITCH_FIELD_NAME]:
        if field not in note:
            return False
    return True


def add_examples_focus_lost(flag: bool, n: Note, fidx: int):
    src_text = n[SRC_FIELD_NAME]

    if src_text == "":
        return flag

    lookup_idx = []
    for f in [SRC_FIELD_NAME]:
        for c, name in enumerate(mw.col.models.field_names(n.note_type())):
            if name == f:
                lookup_idx.append(c)

    # Not src field
    if fidx not in lookup_idx:
        return flag

    return fill_data(n, src_text, flag)


gui_hooks.editor_did_unfocus_field.append(add_examples_focus_lost)

from .buttons import init as btn_init

btn_init()
