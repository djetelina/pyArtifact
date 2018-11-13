from pyartifact import Deck, decode_deck_string


def test_filtering(cards):
    assert len(cards.filter.type('Spell').mana_cost(gt=4).color('black').rarity('Rare')) == 1


def test_includes(cards):
    assert len(cards.get('Storm Spirit').includes) == 3


def test_passive_ability(cards):
    assert cards.get('STORM SPIRIT').passive_abilities[0].name == 'Overload'


def test_decode_deck_deck_string(deck_code):
    name, heroes, cards = decode_deck_string(deck_code['string'])
    print(cards)


def test_deck_from_code(cards, deck_code):
    deck = Deck.from_code(deck_code['string'])
    assert deck.name == deck_code['name']
