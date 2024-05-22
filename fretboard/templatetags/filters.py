from django import template

register = template.Library()

@register.filter
def times(number):
    return range(1, number + 1)

@register.filter
def to_english(num):
    english_numbers = [
        "zero", "one", "two", "three", "four", "five",
        "six", "seven", "eight", "nine", "ten", "eleven",
        "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen"
    ]
    if 0 <= num < len(english_numbers):
        return english_numbers[num]
    return str(num)

@register.filter
def to_roman(num):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

@register.filter
def format_note_name(note):
    # Converts flat notes to the correct format
    flats = {
        "bb": "Bb", "cb": "Cb", "db": "Db", "eb": "Eb", "fb": "Fb", "gb": "Gb", "ab": "Ab", "bb": "Bb"
    }
    # Converts sharp notes to the correct format
    sharps = {
        "cs": "C#", "ds": "D#", "es": "E#", "fs": "F#", "gs": "G#", "as": "A#", "bs": "B#"
    }
    # Check if note is in flats or sharps dictionary
    for key in flats:
        if note.lower().startswith(key):
            return flats[key] + note[-1]
    for key in sharps:
        if note.lower().startswith(key):
            return sharps[key] + note[-1]
    return note.capitalize()

NOTES = {
    "eString": [["f2"], ["gb2", "fs2"], ["g2"], ["ab2", "gs2"], ["a2"], ["bb2", "as2"], ["b2"], ["c3"], ["db3", "cs3"], ["d3"], ["eb3", "ds3"], ["e3"], ["f3"], ["gb3", "fs3"], ["g3"], ["ab3", "gs3"], ["a3"]],
    "bString": [["c2"], ["db2", "cs2"], ["d2"], ["eb2", "ds2"], ["e2"], ["f2"], ["gb2", "fs2"], ["g2"], ["ab2", "gs2"], ["a2"], ["bb2", "as2"], ["b2"], ["c3"], ["db3", "cs3"], ["d3"], ["eb3", "ds3"], ["e3"]],
    "gString": [["ab1", "gs1"], ["a1"], ["bb1", "as1"], ["b1"], ["c2"], ["db2", "cs2"], ["d2"], ["eb2", "ds2"], ["e2"], ["f2"], ["gb2", "fs2"], ["g2"], ["ab2", "gs2"], ["a2"], ["bb2", "as2"], ["b2"], ["c3"]],
    "dString": [["eb1", "ds1"], ["e1"], ["f1"], ["gb1", "fs1"], ["g1"], ["ab1", "gs1"], ["a1"], ["bb1", "as1"], ["b1"], ["c2"], ["db2", "cs2"], ["d2"], ["eb2", "ds2"], ["e2"], ["f2"], ["gb2", "fs2"], ["g2"]],
    "AString": [["bb0", "as0"], ["b0"], ["c1"], ["db1", "cs1"], ["d1"], ["eb1", "ds1"], ["e1"], ["f1"], ["gb1", "fs1"], ["g1"], ["ab1", "gs1"], ["a1"], ["bb1", "as1"], ["b1"], ["c2"], ["db2", "cs2"], ["d2"]],
    "ELowString": [["f0"], ["gb0", "fs0"], ["g0"], ["ab0", "gs0"], ["a0"], ["bb0", "as0"], ["b0"], ["c1"], ["db1", "cs1"], ["d1"], ["eb1", "ds1"], ["e1"], ["f1"], ["gb1", "fs1"], ["g1"], ["ab1", "gs1"], ["a1"]],
}

@register.filter
def get_notes(string_name, fret):
    notes = NOTES.get(string_name, [])
    if fret - 1 < len(notes):
        return notes[fret - 1]
    return []
