# Format furigana to anki's furigana style
def format_furigana(furi: str) -> str:
    out = ""

    in_kanji = False

    for c in furi:
        if c == '[':
            in_kanji = True
            out +="<ruby>"
            continue

        if c == '|':
            if in_kanji:
                out += '<rp>(</rp><rt>'
                in_kanji = False
            continue

        if c == ']':
            out += "</rt><rp>)</rp></ruby>"
            continue

        out += c
            
    return out

def log(msg: str):
    print("[Jotoba Addon]", msg)
