from .editor import SRC_FIELD_POS, SRC_FIELD_NAME, AUDIO_FIELD_POS, JOTOBA_URL, READING_FIELD_POS, MEANING_FIELD_POS, POS_FIELD_POS, PITCH_FIELD_POS, PITCH_FIELD_NAME, has_fields, READING_FIELD_NAME, POS_FIELD_NAME, EXAMPLE_FIELD_PREFIX
from .jotoba import *
from .utils import format_furigana
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
    """ Add pitch menu """
    a = QAction("Bulk-add Pitch", browser)
    a.triggered.connect(lambda: onRegenerate(browser, pitch = True))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

    """ Add POS menu """
    a = QAction("Bulk-add POS", browser)
    a.triggered.connect(lambda: onRegenerate(browser, pos = True))
    browser.form.menuEdit.addAction(a)

    """ Add Sentence menu """
    a = QAction("Bulk-add Sentences", browser)
    a.triggered.connect(lambda: onRegenerate(browser, sentences = True))
    browser.form.menuEdit.addAction(a)

    """ Add All menu """
    a = QAction("Bulk-add All", browser)
    a.triggered.connect(lambda: onRegenerate(browser,pitch = True, pos = True, sentences = True))
    browser.form.menuEdit.addAction(a)

def onRegenerate(browser, pitch = False, pos = False, sentences = False):
    bulk_add(browser.selectedNotes(), pitch, pos, sentences)

def bulk_add(nids, pitch = False, pos = False, sentences = False):
    mw.checkpoint("Bulk-add data")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)

        if not has_fields(note):
            print("skipping: not all fields")
            continue

        need_change = False
        need_sentence = False

        if note[PITCH_FIELD_NAME] == "" and pitch:
            need_change = True

        if note[POS_FIELD_NAME] == "" and pos:
            need_change = True

        if sentences:
            for i in range(3):
                if note[EXAMPLE_FIELD_PREFIX+str(i+1)] == "":
                    need_change = True
                    need_sentence = True
                    break

        if not need_change:
            continue

        try:
            kana = note[READING_FIELD_NAME]
            word = request_word(note[SRC_FIELD_NAME], kana)
        except:
            print("not found for:"+note[SRC_FIELD_NAME])
            continue

        pitch_d = get_pitch_html(word)
        if note[PITCH_FIELD_NAME] == "" and pitch and pitch_d != None:
            note[PITCH_FIELD_NAME] = pitch_d

        pos_d = get_pos(word)
        if note[POS_FIELD_NAME] == "" and pos and pos_d != None:
            note[POS_FIELD_NAME] = "; ".join(pos_d)

        if sentences and need_sentence:
            try:
                sentences = request_sentence(note[SRC_FIELD_NAME])
                for i, sentence in enumerate(sentences):
                    if i > 2:
                        break;

                    field_name = EXAMPLE_FIELD_PREFIX+str(i+1)
                    if note[field_name] != "":
                        continue

                    note[field_name] = format_furigana(sentence["furigana"]) 
            except:
                print("didn't find sentences")
                pass

        note.flush()
    mw.progress.finish()
    mw.reset()
