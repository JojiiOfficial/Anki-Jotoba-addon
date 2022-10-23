from anki.notes import Note
from aqt import mw, gui_hooks
from aqt.utils import showInfo

from .jotoba import *
from .utils import format_furigana, log

# Field constants
EXPRESSION_FIELD_NAME = "Expression"
EXPRESSION_FIELD_POS = 0

READING_FIELD_NAME = "Reading"
READING_FIELD_POS = 1

PITCH_FIELD_NAME = "Pitch"
PITCH_FIELD_POS = 2

MEANING_FIELD_NAME = "Meaning"
MEANING_FIELD_POS = 3

POS_FIELD_NAME = "POS"
POS_FIELD_POS = 4

IMAGE_FIELD_NAME = "Image"
Image_FIELD_POS = 5

AUDIO_FIELD_NAME = "Audio"
AUDIO_FIELD_POS = 6

NOTES_FIELD_NAME = "Notes"
NOTES_FIELD_POS = 7

EXAMPLE_FIELD_PREFIX = "Example "

ALL_FIELD_NAMES = [EXPRESSION_FIELD_NAME, MEANING_FIELD_NAME, READING_FIELD_NAME, POS_FIELD_NAME, PITCH_FIELD_NAME,
                   EXAMPLE_FIELD_PREFIX + "1", EXAMPLE_FIELD_PREFIX + "2", EXAMPLE_FIELD_PREFIX + "3"]

ALL_FIELD_POS = {EXPRESSION_FIELD_NAME: EXPRESSION_FIELD_POS,
                 AUDIO_FIELD_NAME: AUDIO_FIELD_POS,
                 MEANING_FIELD_NAME: MEANING_FIELD_POS,
                 READING_FIELD_NAME: READING_FIELD_POS,
                 POS_FIELD_NAME: POS_FIELD_POS,
                 PITCH_FIELD_NAME: PITCH_FIELD_POS}


def fill_data(note: Note, expr: str, flag: bool, reading: str = ""):
    need_update = False
    for field_i in ALL_FIELD_NAMES:
        if note[field_i] == "":
            need_update = True
            break

    if not need_update:
        return flag

    try:
        word = request_word(expr, reading)
    except Exception as e:  # error while fetching word
        log(e)
        return flag

    if word is None:  # word not found or ambiguity (no kana reading) -> user will call again after providing reading
        return flag

    note[EXPRESSION_FIELD_NAME] = word.expression

    note[POS_FIELD_NAME] = "; ".join(word.part_of_speech)

    note[READING_FIELD_NAME] = word.reading

    note[MEANING_FIELD_NAME] = "; ".join(word.glosses[:3])

    note[PITCH_FIELD_NAME] = word.pitch

    try:
        sentences = request_sentence(expr)
        for i, sentence in enumerate(sentences):
            if i > 2:
                break

            field_name = EXAMPLE_FIELD_PREFIX + str(i + 1)
            if note[field_name] != "":
                continue

            note[field_name] = format_furigana(sentence["furigana"])
    except Exception as e:
        log(e)
        pass

    return True


# Check whether all fields are available in currently displayed note
def has_fields(note) -> bool:
    for f in ALL_FIELD_POS:
        exists = False
        for pos, name in enumerate(mw.col.models.field_names(note.note_type())):
            if name == f and pos == ALL_FIELD_POS[f]:
                exists = True
        if not exists:
            return False
    return True


def add_examples_focus_lost(flag: bool, note: Note, fidx: int):
    if fidx not in [EXPRESSION_FIELD_POS, READING_FIELD_POS]:
        return flag

    if not has_fields(note):
        log("Note does not have the required fields")
        return flag

    expr_text = note[EXPRESSION_FIELD_NAME]

    if expr_text == "":
        log("Expression field is empty")
        return flag

    if fidx == EXPRESSION_FIELD_POS:
        return fill_data(note, expr_text, flag)

    reading_text = note[READING_FIELD_NAME]

    if reading_text == "":
        return flag

    return fill_data(note, expr_text, flag, reading_text)


gui_hooks.editor_did_unfocus_field.append(add_examples_focus_lost)

from .buttons import init as btn_init

btn_init()
