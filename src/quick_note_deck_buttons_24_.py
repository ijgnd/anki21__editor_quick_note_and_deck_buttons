# Add-on for Anki 2.1: Adds "Quick Access" buttons for notetype and deck in "Add" cards dialog

# Copyright © Steve AW <steveawa@gmail.com>
#           © 2012–2017 Roland Sieker <ospalh@gmail.com>
#           © 2017 Glutanimate <github.com/glutanimate>
#           © 2018- ijgnd

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from anki.hooks import wrap
from anki.utils import isMac

from aqt import mw
from aqt.qt import (
    Qt,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QShortcut,
    QKeySequence,
    QWidget,
)

from aqt import gui_hooks
from aqt.addcards import AddCards
from aqt.deckchooser import DeckChooser
from aqt.utils import askUser, showInfo, tooltip


__version__ = "3.1"
addonname = mw.addonManager.addonName(__name__.split(".")[0])


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    return fail





def on_startup_maybe_update_config_to_202004():
    conf = mw.addonManager.getConfig(__name__)
    if not conf:
        print("error in add-on 'quick note and deck buttons'.")
        return
    containsname = False
    tocheck = {
        "deck_button_rows": "deck",
        "model_button_rows": "note type",
    }
    for val in tocheck.keys():
        for rowlist in conf[val]:
            for dictionary in rowlist:
                if "name" in dictionary:
                    containsname = True
                    break
    if not containsname:
        return
    msg = (f'The add-on "{addonname}" contains a dated config. More recent versions no '
            'longer contain the value "name". Instead "deck" or "note type" is used. '
            '<br><br>You can automatically update your config now.<br><br>'
            'During the auto update no error should occur. But if an error did occur '
            'your config would be destroyed. So only answer yes if you have a backup '
            "of your add-on folder with proper backup software or if you don't mind to "
            "manually recreate it.<br><br>"
            "If you don't do an auto-update you have to manually change all occurrences "
            'of "name" in "deck_button_rows" to "deck" and all occurrences of "name" '
            """to "note type" in the add-on config. Otherwise you'll run into problems."""
            "<br><br>Auto update config?"
    )
    if not askUser(msg):
        return
    for val, new in tocheck.items():
        if val in conf:
            for rowlist in conf[val]:
                for dictionary in rowlist:
                    if dictionary.get("name", False):
                        if not dictionary.get(new, False):
                            dictionary[new] = dictionary["name"]
                        del dictionary["name"]
    mw.addonManager.writeConfig(__name__, conf)
gui_hooks.profile_did_open.append(on_startup_maybe_update_config_to_202004)


general_warning = ("<br>Check the readme or reset your config. If you don't adjust the config "
                   "you will run into strange errors.")


def check_entry(config, relevantval, neededval, existing):
    has_problems = []
    for row in config[relevantval]:
        if not isinstance(row, list):
            showInfo((f'Illegal setting in config for the addon "{addonname}".<br>'
                      f'"{relevantval}" must contain json-arrays (=lists) of values for each row.'
                      f'{general_warning}'))
            return
        for dct in row:
            if not isinstance(dct, dict):
                showInfo((f'Illegal setting in config for the addon "{addonname}".<br>'
                        f'"{relevantval}" must contain json-arrays (=lists) of values for '
                         'each row where each array value that defines a button is a json-object '
                         '(=dict, associative array). '
                        f'Your setting "{dct}" is not a json-object.'  
                        f'{general_warning}'))
                return
            if not neededval in dct:
                showInfo((f'Illegal setting in config for the addon "{addonname}".<br>Each '
                          f'entry in "{relevantval}" must contain a "{neededval}" value.'
                          f'{general_warning}'))
                return
            if dct[neededval] not in existing:
                has_problems.append(dct[neededval])
    return has_problems


def on_user_changed_config(config):
    for val in config.keys():
        if val not in ["deck_button_rows", "model_button_rows"]:
            showInfo(('Illegal setting in config for the addon "{addonname}"<br>. If you '
                      "don't change it you'll run into errors."))
            return
    problems_decks = check_entry(config, "deck_button_rows", "deck", mw.col.decks.allNames(dyn=False))
    if problems_decks is None:
        return
    problems_notes = check_entry(config, 'model_button_rows', "note type", mw.col.models.allNames())
    if problems_notes is None:
        return

    errmsg = f"Invalid names in add-on '{addonname}' detected! \n\n"
    if problems_decks:
        errmsg += 'Check the deck "name"s:\n      ' + "\n      ".join(problems_decks) + "\n\n"
    if problems_notes:
        errmsg += 'Check the note type "name"s:\n      ' + "\n      ".join(problems_notes) + "\n\n"
    errmsg += ("If you don't change this and later click on the button for a "
               "\nnon-existing deck or note you will get strange errors."
               "\n\nHint: Pay attention to this common source of error:"
               "\nleading and/or trailing spaces and to not"
               "\naccidentally use a double space.")
    if problems_decks or problems_notes:
        showInfo(errmsg)
mw.addonManager.setConfigUpdatedAction(__name__, on_user_changed_config)















def init_dc(self, mw, widget, label=True, start=None):
    init_chooser(self, mw, widget, label)
    self.setupDecks()
    p = widget.parent()
    if isinstance(p, AddCards):
        self.addcards = p
    else:
        self.addcards = None
    gui_hooks.current_note_type_did_change.append(self.onModelChangeNew)


def init_mc_keepmodels(self, parent, mw, widget, label=True):
    init_chooser(self, mw, widget, label)
    self.parent = parent
    if isinstance(self.parent, AddCards):
        self.addcards = self.parent
    else:
        self.addcards = None
    init_mc_helper(self, mw, widget, label)


def init_mc(self, mw, widget, label=True):
    init_chooser(self, mw, widget, label)
    try:
        topparent = self.parent().parent().parent()
    except:
        self.addcards = False
    else:
        if isinstance(topparent, AddCards):
            self.addcards = topparent
        else:
            self.addcards = False
    init_mc_helper(self, mw, widget, label)


def init_mc_helper(self, mw, widget, label):
    self.setupModels()
    gui_hooks.state_did_reset.append(self.onReset)


def init_chooser(self, mw, widget, label):
    QHBoxLayout.__init__(self)
    self.vbox = QVBoxLayout()
    self.vbox.addLayout(self)
    self.vbox.setContentsMargins(0, 0, 0, 0)
    self.widget = widget
    self.widget.setLayout(self.vbox)
    self.mw = mw
    self.deck = mw.col  # yes that's right
    self.label = label
    self.setContentsMargins(0, 0, 0, 0)   #inner spacing
    self.setSpacing(8)    # outer spacing


def tooltip_string(e, isdc):
    this_val = e.get("deck", "") if isdc else e.get("note type", "")
    this_string = "deck"
    other_val = e.get("note type", "") if isdc else e.get("deck", "")
    other_string = "note type"
    if not isdc:
        this_val, this_string, other_val, other_string = other_val, other_string, this_val, this_string
    other = ""
    if other_val:
        other = f'{other_string} to "{other_val}"'
    tagstring = ""
    if any([val in e for val in ["tags clear existing", "tags to add", "tags to remove"]]):
        clear = e.get("tags clear existing", "")
        add = e.get("tags to add", "")
        remove = e.get("tags to remove", "")
        tagstring = f"""<br>tags: clear:{clear}/add:{add}/remove:{remove}"""
    msg = f'Change {this_string} to "{this_val}"'
    if any([other, tagstring]):
        msg += "<br>(" + other + tagstring + ")"
    return msg


def setup_buttons(chooser, rows, do_function):
    isdc = True if isinstance(chooser, DeckChooser) else False
    if not isdc:
        # then it's a model choser
        # model choser is also used in browser to change note type
        if not chooser.addcards:
            return
    if rows and isinstance(rows[0], dict):  # backwards compatibility
        rows = [rows]
    for idx, buttons in enumerate(rows):
        target = chooser if idx == 0 else chooser.vbox
        bhbl = QHBoxLayout()
        bhbl.setContentsMargins(0, 0, 0, 0)  # right top left bottom, no effect in MacOS
        for e in buttons:
            but = QPushButton(e["label"])
            totip = tooltip_string(e, isdc)
            func = lambda _=None, s=chooser, d=e: do_function(s, d)
            try:
                sc = e["shortcut"]
                s = QShortcut(QKeySequence(sc), chooser.widget)
                totip += f"<br><br>({sc})"
            except KeyError:
                pass
            else:
                s.activated.connect(func)
            # this mac specific function from the version 2.0
            # doesn't seem to help in 2.1: At least for me it makes
            # additional buttons for notes in the first line ugly
            # and doesn't help with my other mac problem (which is
            # that the spacing it too big)
            # if isMac:
            #     but.setStyleSheet("padding: 5px; padding-right: 7px;")
            but.setToolTip(totip)
            but.setFocusPolicy(Qt.ClickFocus)  # so that TAB doesn't focus it
            but.setAutoDefault(False)
            but.clicked.connect(func)
            if not e.get("shortcut only/no button", False):
                bhbl.addWidget(but)
        target.addLayout(bhbl)


def modify_tags(vals, oldtaglist):
    clear = vals.get("tags clear existing", False)
    if isinstance(clear, bool) and clear:
        tags = set()
    else:
        tags = set(oldtaglist)

    toadd = vals.get("tags to add", False)
    if isinstance(toadd, list):
        tags.update(set(toadd))
    if isinstance(toadd, str):
        tags.update(set([toadd]))

    remove = vals.get("tags to remove", False)
    if isinstance(remove, list):
        tags -= set(remove)
    if isinstance(remove, str):
        tags -= set([remove])
    
    return list(tags)


def settags(addinstance, vals):
    e = addinstance.editor
    e.saveTags()
    e.note.tags = modify_tags(vals, e.note.tags.copy())
    e.note.flush()
    e.tags.setText(e.note.stringTags().strip())


def model_changer(mc, vals):
    global KeepModels
    model_name = vals.get("note type")
    # Mostly just a copy and paste from the bottom of onModelChange()
    m = mc.deck.models.byName(model_name)
    try:
        mc.deck.conf['curModel'] = m['id']
    except TypeError:
        # When you see this error message, the most likely explanation
        # is that the model names are not set up correctly in the
        # model_button_rows list of dictionaries above.
        m = (f"No note type “{model_name}”. Check the config of the add-on "
              "“Quick note and deck buttons (Fork for 2.1)”")
        tooltip(m)
        return
    cdeck = mc.deck.decks.current()
    cdeck['mid'] = m['id']
    mc.deck.decks.save(cdeck)
    if not KeepModels:
        gui_hooks.current_note_type_did_change(m)
        mc.mw.reset()
    else:   # from Keep Models: 424778276.onModelChange
        mc.updateModels()
        gui_hooks.current_note_type_did_change(m)
        mc.parent.onModelChange()
        mc.updateModels()
        mc.parent.setAndFocusNote(mc.parent.note)


def deck_changer(dcinstance, deck_name):
    dcinstance.deck.setText(deck_name)
    dcinstance._deckName = deck_name


def set_focus(addcards, vals):
    addcards.editor.web.setFocus()
    focusto = vals.get("focus to field number", 1)
    try:
        focusto = int(focusto)   # int(True) => 1
    except:
        m = (f'error in config of add-on "{addonname}": "focus to field number" '
              "can't be transformed into an int. For details see the readme. Aborting ...")
        tooltip(m)
    else:
        focusto = max(focusto, 1)
        addcards.editor.web.eval(f"""focusField({focusto-1});""")


def _change_model_to(mc, vals):
    if not vals.get("note type", ""):
        tooltip("Error in add-on config. Aborting ...")
        return
    model_changer(mc, vals)
    if any([v in vals for v in ["tags clear existing", "tags to add", "tags to remove"]]):
        settags(mc.addcards, vals)
    if "deck" in vals:
        deck_changer(mc.addcards.deckChooser, vals["deck"])
    set_focus(mc.addcards, vals)


def change_model_to(mc, vals):
    mc.addcards.editor.saveNow(lambda m=mc, v=vals: _change_model_to(m, v))


def _change_deck_to(dc, vals):
    deck_name = vals.get("deck")
    if not deck_name:
        tooltip("Error in add-on config. Aborting ...")
        return
    deck_changer(dc, deck_name)
    if "note type" in vals:
        model_changer(dc.addcards.modelChooser, vals)
    if any([v in vals for v in ["tags clear existing", "tags to add", "tags to remove"]]):
        settags(dc.addcards, vals)
    set_focus(dc.addcards, vals)


def change_deck_to(self, vals):
    self.addcards.editor.saveNow(lambda d=self, v=vals: _change_deck_to(d, v))


def onload():
    global KeepModels
    try:
        ModelChooser = __import__("424778276").modelChooser.ModelChooser
        ModelChooser.__init__ = init_mc_keepmodels
        KeepModels = True
    except:
        from aqt.modelchooser import ModelChooser
        ModelChooser.__init__ = init_mc
        KeepModels = False
    
    ModelChooser.setupModels = wrap(
        ModelChooser.setupModels,
        lambda mc: setup_buttons(mc, gc('model_button_rows', []), change_model_to), 
        "after")
    ModelChooser.change_model_to = change_model_to
    DeckChooser.__init__ = init_dc
    DeckChooser.setupDecks = wrap(
        DeckChooser.setupDecks,
        lambda dc: setup_buttons(dc, gc('deck_button_rows', []), change_deck_to),
        "after")
    DeckChooser.change_deck_to = change_deck_to
gui_hooks.profile_did_open.append(onload)
