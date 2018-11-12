from pyartifact.deck import Deck


def test_filtering(cards):
    assert len(cards.filter.type('Spell').mana_cost(gt=4).color('black').rarity('Rare')) == 1


def test_includes(cards):
    assert len(cards.get('Storm Spirit').includes) == 3


def test_passive_ability(cards):
    assert cards.get('STORM SPIRIT').passive_abilities[0].name == 'Overload'


def test_deck(cards):
    deck = Deck.decode('ADCJWkTZX05uwGDCRV4XQGy3QGLmqUBg4GQJgGLGgO7AaABR3JlZW4vQmxhY2sgRXhhbXBsZQ__')
    assert deck.name == 'Green/Black Example'
