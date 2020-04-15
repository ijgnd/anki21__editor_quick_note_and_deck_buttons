#### general

The buttons you see to quickly change 

- ... the note type are defined by "model_button_rows"
- ... the deck are defined by "deck_button_rows"

#### Details

- `model_button_rows` and `deck_button_rows` each contain a list of lists. Each nested list represents one row.
- The buttons in each row are defined by a list of dictionaries.
- Each dictionary must contain:
    - `label`: the text of the button
    - `deck` or `note type`: the name of the note type or deck to change to. The deck is created if it doesn’t
      exist already.
    - shortcut (optional): the shortcut key
- You can also add the following values to each dictionary: `deck` or `note type`,
`tags clear existing`, `tags to add`, `tags to remove`.
- Closely follow the examples. Use the correct symbols like brackets, curly braces, etc.
- The examples from this readme might not be shown properly in the config window of Anki. To see the examples with proper 
  line breaks have a look at the site on AnkiWeb or on Github.

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
                    "deck": "Basic"
                },
                {
                    "label": "C",
                    "shortcut": "Ctrl+2",
                    "decknote type": "Cloze"
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
                    "note type": "Deck1"
                },
                {
                    "label": "my subdeck",
                    "note type": "Deck1::my subdeck"
                }
            ],
            [
                {
                    "label": "Deck 2",
                    "note type": "Deck 2"
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
                    "tags to add": ["this_tag_was_added", "also_this"],
                    "tags to remove": ["this_tag_will_be_removed_if_present", "this_too"]
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
                    "tags to add": ["this_is_added", "this_too"],
                    "tags to remove": ["if_present_this_tag_will_be_removed", "also_this_one"]
                },
                {
                    "label": "C",
                    "shortcut": "Ctrl+2",
                    "decknote type": "Cloze"
                }
            ]
        ]
    }

