#### general

The buttons you see to quickly change 

- ... the note type are defined by "model_button_rows"
- ... the deck are defined by "deck_button_rows"

"deck__model__proportion" allows you influence the relative width of the deck area and note type 
area. A higher number means that the affected element should get relatively bigger. E.g. 
`"deck__model__proportion": [9,1],` means that the deck area will be much wider *if the number of* 
*visible buttons allows this*. It does *not* mean that the deck area will be exactly nine times as 
wide as the model area.

If you work with multiple profiles you can enable or disable this add-on for selected profiles
with `"Disable for these profiles"` and `"Enable only for these profiles"`.
If `"Enable only for these profiles"` is an empty list this add-on will be enabled for all profiles
except for those set under `"Disable for these profiles"`. If you set a name in 
`"Enable only for these profiles"` this add-on will only be active in this profile. This setting
will override an entry in `"Disable for these profiles"`.

#### Details

- `model_button_rows` and `deck_button_rows` each contain a list of lists. Each nested list represents one row.
- The buttons in each row are defined by a list of dictionaries.
- Each dictionary must contain:
    - `label`: the text of the button
    - `deck` or `note type`: the name of the note type or deck to change to. The deck is created if it doesn’t
      exist already.
- You can also add the following values to each dictionary: `shortcut`, `deck` or `note type`,
`tags clear existing`, `tags to add`, `tags to remove`, `shortcut only/no button`, 
`focus to field number`
- `tags clear existing` must be "true" or "false". The default is "false".
- `tags to add` and `tags to remove` must be lists and look like this ["add_this_one", "and_this_one"].
- You can also set `shortcut only/no button` to "true" so that a button is not shown for this option. In this case the value for `label` will be ignored.
- `focus to field number` must be an integer (1, 2, 3, etc.)
- Closely follow the examples. Use the correct symbols like brackets, curly braces, etc.
- Before Anki 2.1.24 you can't select text to copy it from the readme sidebar of this add-on
config dialog. If you use an  older Anki version you can view the following examples 
also [on this website](https://github.com/ijgnd/anki21__editor_quick_note_and_deck_buttons/blob/master/src/config.md) 
from where you can copy them.

#### example with one row 


    {
        "deck_button_rows": [
            [
                {
                    "label": "Deck1",
                    "shortcut": "Ctrl+7",
                    "deck": "Deck1"
                },
                {
                    "label": "my subdeck",
                    "deck": "Deck1::my subdeck"
                }
            ]
        ],
        "model_button_rows": [
            [
                {
                    "label": "B",
                    "shortcut": "Ctrl+1",
                    "note type": "Basic"
                },
                {
                    "label": "C",
                    "shortcut": "Ctrl+2",
                    "note type": "Cloze"
                }
            ]
        ]
    }


#### example with two rows 


    {
        "deck_button_rows": [
            [
                {
                    "label": "Deck1",
                    "shortcut": "Ctrl+7",
                    "deck": "Deck1"
                },
                {
                    "label": "my subdeck",
                    "deck": "Deck1::my subdeck"
                }
            ],
            [
                {
                    "label": "Deck 2",
                    "deck": "Deck 2"
                }
            ]
        ],
        "model_button_rows": [
            [
                {
                    "label": "B",
                    "shortcut": "Ctrl+1",
                    "note type": "Basic"
                },
                {
                    "label": "C",
                    "shortcut": "Ctrl+2",
                    "note type": "Cloze"
                }
            ],
            [
                {
                    "label": "with reverse",
                    "shortcut": "Ctrl+3",
                    "note type": "Basic (and reversed card)"
                }
            ]
        ]
    }


#### example with one row where a button changes the note type and deck at the same time and modifies tags


    {
        "deck_button_rows": [
            [
                {
                    "label": "Deck1",
                    "shortcut": "Ctrl+7",
                    "deck": "Deck1",
                    "note type": "Basic",
                    "tags clear existing": true,
                    "tags to add": ["quick_note_buttons_addon_sample_tag_for_deck"],
                    "tags to remove": []
                },
                {
                    "label": "my subdeck",
                    "deck": "Deck1::my subdeck"
                }
            ]
        ],
        "model_button_rows": [
            [
                {
                    "label": "B",
                    "shortcut": "Ctrl+1",
                    "note type": "Basic",
                    "deck": "Deck1",
                    "tags clear existing": false,
                    "tags to add": ["quick_note_buttons_addon_sample_tag_models", "quick_note_buttons_addon_models_this_too"],
                    "tags to remove": ["if_present_this_tag_will_be_removed", "also_this_one"]
                },
                {
                    "label": "C",
                    "shortcut": "Ctrl+2",
                    "note type": "Cloze"
                }
            ]
        ]
    }

