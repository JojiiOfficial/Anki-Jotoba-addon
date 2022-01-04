from .editor import SRC_FIELD_POS, AUDIO_FIELD_POS, JOTOBA_URL, READING_FIELD_POS, MEANING_FIELD_POS, POS_FIELD_POS
from .jotoba import request_word
from anki.hooks import addHook
from aqt.utils import showInfo

# Audio button
def get_audio(editor):
    allFields = editor.note.fields
    src_text = allFields[SRC_FIELD_POS];
    if src_text == "":
        return
    try:
        word = request_word(src_text)
    except:
        showInfo("Word not found")
        return

    if word != None and "audio" in word:
        audio = JOTOBA_URL+word["audio"]
        set_values_on_editor(audio, editor)
    else:
        showInfo("Word has no audio")


def set_values_on_editor(audio, editor):
    audio = editor.urlToFile(audio)
    allFields = editor.note.fields
    allFields[AUDIO_FIELD_POS] = f'[sound:{audio}]'
    editor.loadNote()
    editor.web.setFocus()
    editor.web.eval(f'focusField({AUDIO_FIELD_POS});')
    editor.web.eval('caretToEnd();')

def addAudioBtn(buttons, editor):
    editor._links['add_audio'] = get_audio
    return buttons + [editor._addButton("", "add_audio", "tooltip", label = "Add Audio")]

# Clear contents
def clear_contents(editor):
    allFields = editor.note.fields
    for i in range(len(allFields)):
        allFields[i] = f''
    editor.loadNote()
    editor.web.eval(f'focusField(0);')

def addClearContent(buttons, editor):
    editor._links['clear_contents'] = clear_contents
    return buttons + [editor._addButton("", "clear_contents", "tooltip", label = "Clear all")]

# Update fileds
def update_fields(editor):
    allFields = editor.note.fields
    if allFields[SRC_FIELD_POS] == "":
        return
    for i in [MEANING_FIELD_POS, READING_FIELD_POS, POS_FIELD_POS]:
        allFields[i] = f''
    editor.loadNote()
    editor.web.eval(f'focusField(0);')
    editor.web.eval(f'focusField(1);')
    return

def addUpdateFieldBtn(buttons, editor):
    editor._links['update_fields'] = update_fields
    return buttons + [editor._addButton("", "update_fields", "tooltip", label = "Update data")]

def init():
    addHook("setupEditorButtons", addClearContent)
    addHook("setupEditorButtons", addUpdateFieldBtn)
    addHook("setupEditorButtons", addAudioBtn)
