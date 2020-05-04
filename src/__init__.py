from anki import version as anki_version
_, _, point = anki_version.split(".")
point = int(point)

if point < 20:
    from . import quick_note_deck_buttons_00_
elif point < 23:
    from . import quick_note_deck_buttons_20_
else:
    # designed for Keep model of add cards from 2020-05-04 or later, https://ankiweb.net/shared/info/424778276
    from . import quick_note_deck_buttons_24_
