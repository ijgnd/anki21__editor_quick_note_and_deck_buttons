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


from aqt import mw
from aqt.qt import *
from aqt.modelchooser import ModelChooser
from aqt.deckchooser import DeckChooser
from aqt.utils import tooltip, showInfo

from anki.hooks import wrap
from anki.hooks import runHook, addHook
from anki.lang import _
from anki.utils import isMac

__version__ = "2.1.3"


def update_config(config):
    """try to verify if decks and notes exist"""
    decknames = mw.col.decks.allNames(dyn=False)
    problems_decks = []
    for l in config['deck_button_rows']:
        for d in l:
            if d['name'] not in decknames:
                problems_decks.append(d['name'])
    modelnames = mw.col.models.allNames()
    problems_notes = []
    for l in config['model_button_rows']:
        for m in l:
            if m['name'] not in modelnames:
                problems_notes.append(m['name'])
    errmsg = "Invalid names in add-on 'Quick note and deck buttons' detected! \n\n"
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
mw.addonManager.setConfigUpdatedAction(__name__, update_config)


def gc(arg, fail=False):
    return mw.addonManager.getConfig(__name__).get(arg, fail)


def init_dc(self, mw, widget, label=True, start=None):
    init_chooser(self, mw, widget, label)
    self.setupDecks()
    addHook('currentModelChanged', self.onModelChange)


def init_mc(self, mw, widget, label=True):
    init_chooser(self, mw, widget, label)
    self.setupModels()
    addHook('reset', self.onReset)


def init_chooser(self, mw, widget, label):
    QHBoxLayout.__init__(self)
    self.vbox = QVBoxLayout()
    self.vbox.addLayout(self)
    self.vbox.setContentsMargins(0, 0, 0, 0)  # self.vbox.setMargin(0)   #pyqt5
    self.widget = widget
    self.widget.setLayout(self.vbox)
    self.mw = mw
    self.deck = mw.col
    self.label = label
    self.setContentsMargins(0, 0, 0, 0)  # self.setMargin(0)  #pyqt5   #inner spacing
    self.setSpacing(8)    # outer spacing


def setup_buttons(chooser, rows, text, do_function):
    if rows and isinstance(rows[0], dict):  # backwards compatibility
        rows = [rows]
    for idx, buttons in enumerate(rows):
        target = chooser if idx == 0 else chooser.vbox
        bhbl = QHBoxLayout()
        bhbl.setContentsMargins(0, 0, 0, 0)  # right top left bottom, no effect in MacOS
        for button_item in buttons:
            b = QPushButton(button_item["label"])
            tt = _("Change {what} to {name}").format(
                what=text, name=button_item["name"])
            l = lambda _=None, s=chooser, nn=button_item["name"]: do_function(
                s, nn)
            try:
                sc = _(button_item["shortcut"])
                s = QShortcut(QKeySequence(sc), chooser.widget)
                tt += "<br>({})".format(sc)
            except KeyError:
                pass
            else:
                s.activated.connect(l)
            #this mac specific function from the version 2.0
            #doesn't seem to help in 2.1: At least for me it makes
            #additional buttons for notes in the first line ugly
            #and doesn't help with my other mac problem (which is
            #that the spacing it too big)
            #if isMac:
            #    b.setStyleSheet("padding: 5px; padding-right: 7px;")
            b.setToolTip(tt)
            b.setFocusPolicy(Qt.ClickFocus)  # so that TAB doesn't focus it
            b.setAutoDefault(False)
            bhbl.addWidget(b)
            b.clicked.connect(l)
        target.addLayout(bhbl)


def change_model_to(chooser, model_name):
    global KeepModels
    # Mostly just a copy and paste from the bottom of onModelChange()
    m = chooser.deck.models.byName(model_name)
    try:
        chooser.deck.conf['curModel'] = m['id']
    except TypeError:
        # When you see this error message, the most likely explanation
        # is that the model names are not set up correctly in the
        # model_button_rows list of dictionaries above.
        m = ("No note type “{model}”. Check the config of the add-on "
             "“Quick note and deck buttons (Fork for 2.1)”".format(model=model_name))
        tooltip(m)
        return
    cdeck = chooser.deck.decks.current()
    cdeck['mid'] = m['id']
    chooser.deck.decks.save(cdeck)
    if not KeepModels:
        runHook("currentModelChanged")
        chooser.mw.reset()
    else:  # from Keep Models Add-on
        addcards = chooser.widget.parent()
        addcards.onModelChange()
        chooser.updateModels()


def change_deck_to(self, deck_name):
    self.deck.setText(deck_name)
    self._deckName = deck_name


def onload():
    global KeepModels
    try:
        KeepModels = __import__("424778276").keepModelInAddCards
    except:
        KeepModels = False
addHook("profileLoaded", onload)


ModelChooser.__init__ = init_mc
ModelChooser.setupModels = wrap(
    ModelChooser.setupModels,
    lambda mc: setup_buttons(
        mc, gc('model_button_rows', []), "note type", change_model_to),
    "after")
ModelChooser.change_model_to = change_model_to
DeckChooser.__init__ = init_dc
DeckChooser.setupDecks = wrap(
    DeckChooser.setupDecks,
    lambda dc: setup_buttons(dc, gc('deck_button_rows', []), "deck", change_deck_to),
    "after")
DeckChooser.change_deck_to = change_deck_to
