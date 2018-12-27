from pyartifact import Deck, decode_deck_string
from pyartifact.deck_encoding.encode import encode_deck
from pyartifact.sets_and_cards import Hero, Item


def test_filtering(cards):
    assert len(cards.filter.type('Spell').mana_cost(gt=4).color('black').rarity('Rare')) == 1


def test_cards_iterable(cards):
    assert list(cards)


def test_find(cards, find_name):
    assert cards.find(find_name.find).name == find_name.found


def test_includes(cards):
    assert len(cards.get('Storm Spirit').includes) == 3


def test_passive_ability(cards):
    assert cards.get('STORM SPIRIT').passive_abilities[0].name == 'Overload'


def test_decode_deck_deck_string(deck_code):
    deck_contents = decode_deck_string(deck_code['string'])
    assert deck_contents['name'] == deck_code['name']
    assert len(deck_contents['heroes']) == 5
    if deck_code['version'] >= 2:
        assert encode_deck(deck_contents, version=deck_code['version']) == deck_code['string']


def test_deck_encoding(cards, deck_code):
    deck = Deck.from_code(deck_code['string'])
    assert deck.name == deck_code['name']
    assert len(deck.heroes) == 5
    if deck_code['version'] >= 2:
        assert deck.deck_code == deck_code['string']


def test_shared_name(cards):
    satyr = cards.get('Satyr Magician', ignore_shared_name=False)
    assert isinstance(satyr, list)
    assert len(satyr) == 2
    storm = cards.get('Storm Spirit')
    assert isinstance(storm, Hero)
    blade = cards.get('Apotheosis Blade')
    assert isinstance(blade, Item)


def test_deck_str(deck_code):
    # Only v2 deck_codes round trip
    if deck_code['version'] == 2:
        deck = Deck.from_code(deck_code['string'])
        assert str(deck) == deck_code['string']
