# pyArtifact

Pythonic wrapper around Valve's Artifact API, with object mapping, filtering and hopefully more

Current phase: **prototype** -> very unstable API

[![MIT License](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://opensource.org/licenses/MIT)
[![pypi version](https://badge.fury.io/py/pyartifact.svg)](https://badge.fury.io/py/pyartifact)

## Here's what we can do so far
```python
>>> from pyartifact import Cards
>>> cards = Cards()
>>> cards.load_all_sets()
>>> repr(cards.get('Storm Spirit').includes[0])
<Artifact card: {'id': 10538, 'base_id': 10538, 'name': 'Ball Lightning', 'type': 'Spell', 'text': "Move an <span style='font-weight:bold;color:#736e80;'>allied black hero</span> to an empty combat position in any lane.", 'mini_image': 'https://steamcdn-a.akamaihd.net/apps/583950/icons/set01/10538.aeb7a6a47e1d8b1a26307ae25e329df3e3bb0843.png', 'large_image': 'https://steamcdn-a.akamaihd.net/apps/583950/icons/set01/10538_large_english.9b39d2d2bb4769b68fa3ac42abee35b1685a57de.png', 'ingame_image': None, '_CardBase__references': [], 'color': 'black', 'rarity': None, 'item_def': None, 'mana_cost': 3, 'illustrator': 'JiHun Lee'}>

>>> filtered = cards.filter.type('Spell').mana_cost(gt=4).color('black').rarity('Rare')
>>> len(filtered)
1
>>> for card in filtered:
...     print(card)
...
The Cover of Night

# Deck encoding (wrapper not done)
>>> from pyartifact import decode_deck_string
>>> deck_contents = decode_deck_string('ADCJQUQI30zuwEYg2ABeF1Bu94BmWIBTEkLtAKlAZakAYmHh0JsdWUvUmVkIEV4YW1wbGU_')
>>> print(deck_contents['name'])
Blue/Red Example
>>> print(deck_contents['heroes'])
[{'id': 4003, 'turn': 1}, {'id': 10006, 'turn': 1}, {'id': 10030, 'turn': 1}, {'id': 10033, 'turn': 3}, {'id': 10065, 'turn': 2}]
>>> from pyartifact import encode_deck
>>> print(encode_deck(deck_contents))
ADCJQUQI30zuwEYg2ABeF1Bu94BmWIBTEkLtAKlAZakAYmHh0JsdWUvUmVkIEV4YW1wbGU_
```

## Plans

* Provide text sanitizers (text atm. has html) - to markdown, strip, etc., use for deck encoding/decoding
* Add more filtering options
* Cleanup code structure (possible performance improvements)
