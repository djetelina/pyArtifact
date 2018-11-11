# pyArtifact

Pythonic wrapper around Valve's Artifact API, with object mapping, filtering and hopefully more

Current phase: **prototype** -> very unstable API

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
```

## Plans

* Implement deck code API
* Provide text sanitizers (text atm. has html) - to markdown, strip, etc.
* Add more filtering options
* Cleanup code structure (possible performance improvements)
* Write documentation
* See what people actually want from this library/if it's wanted at all
