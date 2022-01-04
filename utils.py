# Format furigana to anki's furigana style
def format_furigana(furi) -> str:
    out = ""

    in_kanji = False

    for c in furi:
        if c == '[':
            in_kanji = True
            continue

        if c == ']':
            out += "]"
            continue

        if c == '|':
            if in_kanji:
                out += '['
                in_kanji = False
            continue

        out += c
            
    return out

