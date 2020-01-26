from anki import version as anki_version
old_anki = tuple(int(i) for i in anki_version.split(".")) < (2, 1, 20)

if old_anki:
    from . import old_quick_note_deck_buttons
else:
    from . import new_quick_note_deck_buttons
