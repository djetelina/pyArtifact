Library overview
----------------

There are 2 main functions of pyArtifact

* Wrap Valve's card API with easier to work with pythonic objects
* Wrap deck code API to enable encoding a decoding

Card API usage
~~~~~~~~~~~~~~

First step will be loading all the cards:

.. code-block:: python

    from pyartifact import Cards
    cards = Cards()
    cards.load_all_sets()


This enables you to use 3 methods to search and filter cards.

First of all there's filter, for example if you want to find blue spells that cost less than 3 mana:

.. code-block:: python

    filtered = cards.filter.type('Spell').color('Blue').mana_cost(lt=3)
    # To see how many cards we found
    len(filtered)
    # To see the names of the found cards
    for card in filtered.cards:
        print(card.name)

If you know what you're looking for, you can simply get it:

.. code-block:: python

    # Get the card instance by the cards name
    storm_spirit = cards.get('Storm Spirit')
    # Play around with it!
    print(f'Storm spirit has {storm_spirit.attack} attack and {storm_spirit.hit_points} health.')
    print(f"When you put him into your deck, he brings the spell '{storm_spirit.includes[0].name}' with him.")

Deck code API
~~~~~~~~~~~~~

pyArtifact offers two approaches to deck encoding and decoding. If you want to use the card objects showcased above,
you can use the :py:class:`pyartifact.Deck` object:

.. code-block:: python

    from pyartifact import Deck
    deck = Deck.from_code("ADCJQUQI30zuwEYg2ABeF1Bu94BmWIBTEkLtAKlAZakAYmHh0JsdWUvUmVkIEV4YW1wbGU_")
    # or alternatively
    deck = Deck.loads("ADCJQUQI30zuwEYg2ABeF1Bu94BmWIBTEkLtAKlAZakAYmHh0JsdWUvUmVkIEV4YW1wbGU_")
    # And done!
    print(len(deck.overview.items))  # It's 9. The deck has 9 items in it
    # You can now edit it
    deck.name = 'Renamed deck'
    # And turn back into a deck code
    print(deck.deck_code)  # Or str(deck), or deck.dumps(), so you have your options open.

To use all this, you need to have all the existing sets loaded with the Card API, as it's enriching
the data with the instances of the cards, for easier manipulation. If that is something you don't want
and you'd just like to use the encode and decode functions, pyArtifact has your back:

.. code-block:: python

    from pyartifact import decode_deck_string, encode_deck
    deck_data = decode_deck_string("ADCJQUQI30zuwEYg2ABeF1Bu94BmWIBTEkLtAKlAZakAYmHh0JsdWUvUmVkIEV4YW1wbGU_")
    deck_string = encode_deck(deck_data)
