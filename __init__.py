# provisional update for 2.1 by ijgnd from 2018
#
# original comments:
    # Copyright © 2012–2017 Roland Sieker <ospalh@gmail.com>
    # Copyright © 2017 Glutanimate <github.com/glutanimate>
    #
    # Provenance:
    # The idea, original version and parts of this code
    # written by Steve AW <steveawa@gmail.com>
    #
    # License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
    #
    # Support: Report an issue at https://github.com/ospalh/anki-addons/
    # The more precise the report, the greater the chance i will do something.

"""
Adds "Quick Access" buttons to quickly change between frequently used
note types and decks in the editor component of the "Add" cards dialog
and browser.
"""

from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QShortcut, QVBoxLayout
from PyQt5.QtGui import QKeySequence

from aqt import mw
from aqt.qt import *
from aqt.modelchooser import ModelChooser
from aqt.deckchooser import DeckChooser
from aqt.utils import tooltip, showInfo

from anki.hooks import wrap
from anki.hooks import runHook, addHook
from anki.lang import _
from anki.utils import isMac

__version__ = "2.1.2"


def update_config(conf):
    """try to verify if decks and notes exist"""
    global config

    try:    # check if database can be queried
        decks = mw.col.decks.all()
    except KeyError:
        config=conf   
    else:
        decknames = []
        for d in decks:
            decknames.append(d['name'])
        problems_decks = []
        for l in conf['deck_button_rows']:
            for d in l:
                if not d['name'] in decknames:
                    problems_decks.append(d['name'])

        modelnames = []  
        for m in mw.col.models.all():
            modelnames.append(m['name'])

        problems_notes = []
        for l in conf['model_button_rows']:
            for m in l: 
                if not m['name'] in modelnames:
                    problems_notes.append(m['name'])

        errormessage="Invalid names in add-on 'Quick note and deck buttons' detected! \n\n"  
        if problems_decks:
            errormessage += 'Check the deck "name"s:\n      ' + "\n      ".join(problems_decks) + "\n\n"
        if problems_notes:
            errormessage += 'Check the note type "name"s:\n      ' + "\n      ".join(problems_notes) + "\n\n"      
        errormessage += "If you don't change this and later click on the button for a " + \
                      "\nnon-existing deck or note you will get strange errors." + \
                      "\n\nHint: Pay attention to this common source of error:" + \
                      "\nleading and/or trailing spaces and to not" + \
                      "\naccidentally use a double space."              
        if problems_decks or problems_notes:
            showInfo(errormessage)
        config=conf          


#on startup decks = mw.col.decks returns "None" so I can't check during startup if
#the settings are valid.
config = mw.addonManager.getConfig(__name__)
mw.addonManager.setConfigUpdatedAction(__name__,update_config) 



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
    self.vbox.setContentsMargins(0,0,0,0)  #self.vbox.setMargin(0)   #pyqt5
    self.widget = widget
    self.widget.setLayout(self.vbox)
    self.mw = mw
    self.deck = mw.col
    self.label = label
    self.setContentsMargins(0,0,0,0)  #self.setMargin(0)  #pyqt5   #inner spacing
    self.setSpacing(8)    #outer spacing


def setup_buttons(chooser, rows, text, do_function):
    if rows and isinstance(rows[0], dict):  # backwards compatibility
        rows = [rows]
    for idx, buttons in enumerate(rows):
        target = chooser if idx == 0 else chooser.vbox
        bhbl = QHBoxLayout()
        bhbl.setContentsMargins(0,0,0,0)  #right top left bottom   #this seems to have no effect in MacOS
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
            #    b.setToolTip(tt)
            #    b.setFocusPolicy(Qt.ClickFocus)
            #    b.setAutoDefault(False)
            bhbl.addWidget(b)
            b.clicked.connect(l)
        target.addLayout(bhbl)


def change_model_to(chooser, model_name):
    """Change to model with name model_name"""
    # Mostly just a copy and paste from the bottom of onModelChange()
    m = chooser.deck.models.byName(model_name)
    try:
        chooser.deck.conf['curModel'] = m['id']
    except TypeError:
        # When you see this error message, the most likely explanation
        # is that the model names are not set up correctly in the
        # model_button_rows list of dictionaries above.
        tooltip(u"No note type “{model}”".format(model=model_name))
        return
    cdeck = chooser.deck.decks.current()
    cdeck['mid'] = m['id']
    chooser.deck.decks.save(cdeck)
    runHook("currentModelChanged")
    chooser.mw.reset()


def change_deck_to(self, deck_name):
    """Change to deck with name deck_name"""
    # Well, that is easy.
    self.deck.setText(deck_name)
    self._deckName = deck_name


ModelChooser.__init__ = init_mc
ModelChooser.setupModels = wrap(
    ModelChooser.setupModels,
    lambda mc: setup_buttons(
        mc, config['model_button_rows'], "note type", change_model_to),
    "after")
ModelChooser.change_model_to = change_model_to
DeckChooser.__init__ = init_dc
DeckChooser.setupDecks = wrap(
    DeckChooser.setupDecks,
    lambda dc: setup_buttons(dc, config['deck_button_rows'], "deck", change_deck_to),
    "after")
DeckChooser.change_deck_to = change_deck_to
