from .editor import SRC_FIELD_POS, SRC_FIELD_NAME, AUDIO_FIELD_POS, JOTOBA_URL, READING_FIELD_POS, MEANING_FIELD_POS, POS_FIELD_POS, PITCH_FIELD_POS, PITCH_FIELD_NAME, has_fields, READING_FIELD_NAME
from .jotoba import request_word, get_pitch_html
from anki.hooks import addHook
from aqt.utils import showInfo
from aqt.qt import *
from aqt import mw

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
    for i in [MEANING_FIELD_POS, READING_FIELD_POS, POS_FIELD_POS, PITCH_FIELD_POS]:
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
    addHook("browser.setupMenus", setupBrowserMenu) # Bulk add

def setupBrowserMenu(browser):
    """ Add menu entry to browser window """
    a = QAction("Bulk-add Pitch", browser)
    a.triggered.connect(lambda: onRegenerate(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

def onRegenerate(browser):
    bulk_add_pitch(browser.selectedNotes())

def bulk_add_pitch(nids):
    mw.checkpoint("Bulk-add Pitch")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)

        if not has_fields(note):
            print("skipping: not all fields")
            continue

        if note[PITCH_FIELD_NAME] != "":
            print("skipping: Pitch existing")
            continue

        try:
            kana = note[READING_FIELD_NAME]
            word = request_word(note[SRC_FIELD_NAME], kana)
        except:
            print("not found for:"+note[SRC_FIELD_NAME])
            continue

        pitch = get_pitch_html(word)
        if pitch == None:
            print("skipping: Pitch not available")
            continue

        note[PITCH_FIELD_NAME] = pitch
        print("setting pitch")

        note.flush()
    mw.progress.finish()
    mw.reset()
