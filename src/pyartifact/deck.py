"""
Deck wrapper with an overview class.
"""
from collections import defaultdict
from typing import List, Union, Dict

from ._context import ctx
from .deck_encoding.decode import decode_deck_string
from .deck_encoding.encode import encode_deck
from .exceptions import PyArtifactException
from .filtering import CardFilter
from .sets_and_cards import Hero, CardTypesInstanced, Item, Spell, Improvement, Creep
from .types.deck_types import HeroDeckType, CardDeckType, DeckContents


class Deck:
    """
    Class for holding information about a deck. To use this, all sets must be loaded.

    As this library isn't supposed to be a fully fledged deck constructor,
    accessing deck_contents directly is recommended.

    Compared to the out-of-the-box data encoded in the deck string, this object enriches
    them with an additional key `instance` that holds an instance of the deck from :py:class:`pyartifact.Cards`

    As of now, the deck object does no validations, the rules to follow are:

        * Some cards have `includes`, that are automatically added to the deck and they shouldn't
          be in the cards portion of deck contents.
        * Abilities and Passive abilities aren't able to be included in a deck, as they come with another cards
          and are more of a traits than cards.
        * Heroes have their own part of deck contents, don't put them into the cards section

    Deck code versions
    ~~~~~~~~~~~~~~~~~~

    Deck codes currently have two versions. We are able to load both, but only dump to version 2.

    +---------+--------+-------+---------------+
    | Version | Heroes | Cards |   Deck name   |
    +=========+========+=======+===============+
    |    1    |   yes  |  yes  |      no       |
    +---------+--------+-------+---------------+
    |    2    |   yes  |  yes  | 63 characters |
    +---------+--------+-------+---------------+

    When loading version 1, this library will still provide a name, which will be an empty string.
    """
    def __init__(self, deck_contents: DeckContents) -> None:
        """
        :param deck_contents:   dict of deck contents
        """
        if sorted(ctx.loaded_sets) != sorted(ctx.all_sets):
            raise PyArtifactException("To instantiate a Deck, all sets musts be loaded.")
        self.deck_contents = deck_contents
        self._enrich()

    def __repr__(self) -> str:
        return f'<Artifact deck: {self.deck_contents}>'

    @classmethod
    def from_code(cls, deck_code: str) -> 'Deck':
        """
        Constructs the deck object from a deck code string.

        `Deck.from_code(deck_code)` does the exact same thing as `Deck.loads(deck_code)`

        :param deck_code:   Version 1 or 2 deck code
        """
        return cls(deck_contents=decode_deck_string(deck_code))

    loads = from_code

    @classmethod
    def new(cls, name: str, heroes: List[HeroDeckType], cards: List[CardDeckType]):
        """
        Constructs the deck object from the insides of deck contents, for when you can't be bothered to make a dict.

        :param name:        Name of the deck
        :param heroes:      List of dictionaries holding information about the heroes
        :param cards:       List of dictionaries holding information about the cards
        """
        deck_contents = DeckContents(name=name, heroes=heroes, cards=cards)
        return cls(deck_contents)

    @property
    def deck_code(self) -> str:
        """Returns the latest version of the deck code."""
        return encode_deck(self.deck_contents)

    __str__ = deck_code

    def dumps(self) -> str:
        """
        Returns the latest version of the deck code, same as deck_code property.
        For people who are used to json/yaml api :).
        """
        return self.deck_code

    @property
    def name(self) -> str:
        """Name of the deck or an empty string of there is no name."""
        return self.deck_contents.get('name', '')

    @name.setter
    def name(self, new_name: str) -> None:
        """Sets a new name of the deck"""
        self.deck_contents['name'] = new_name

    @property
    def cards(self) -> List[CardDeckType]:
        """List of dictionaries with all the cards and their information"""
        return self.deck_contents['cards']

    @property
    def heroes(self) -> List[HeroDeckType]:
        """List of dictionaries with all the heroes and their information"""
        return self.deck_contents['heroes']

    @property
    def overview(self) -> 'Overview':
        """
        Returns an overview of the deck, used for quick glances at it's contents.
        The overview holds an instance of the deck and will change with any changes made to the deck.
        """
        return Overview(self)

    def expand_cards(self, hero_includes: bool = True) -> List[CardTypesInstanced]:
        """
        Expands all the cards in the deck into a list of their instances, once for each count.

        :param hero_includes:   Whether also expand auto-includes coming with the heroes
        """
        expanded: List[CardTypesInstanced] = []
        for card in self.cards:
            for _ in range(card['count']):
                expanded.append(card['instance'])
        if hero_includes:
            for hero in self.heroes:
                expanded += hero['instance'].includes
        return expanded

    def _enrich(self) -> None:
        """Adds instance key to all heroes and cards."""
        enriched_heroes: List[HeroDeckType] = []
        for hero in self.heroes:
            hero_instance = ctx.cards_by_id[hero['id']]
            enriched_heroes.append(HeroDeckType(instance=hero_instance, turn=hero['turn'], id=hero['id']))

        enriched_cards: List[CardDeckType] = []
        for card in self.cards:
            card_instance = ctx.cards_by_id[card['id']]
            enriched_cards.append(CardDeckType(instance=card_instance, count=card['count'], id=card['id']))

        enriched_deck = DeckContents(name=self.name, heroes=enriched_heroes, cards=enriched_cards)
        self.deck_contents = enriched_deck

    @staticmethod
    def new_hero_dict(hero: Hero, turn: int) -> HeroDeckType:
        """
        Construction of a hero dict compatible with the encoding process and Deck object internals

        :param hero:        Instance of a hero card
        :param turn:        Which turn the hero will be deployed
        """
        return HeroDeckType(instance=hero, turn=turn, id=hero.id)

    @staticmethod
    def new_card_dict(card: CardTypesInstanced, count: int) -> CardDeckType:
        """
        Construction of a card dict compatible with the encoding process and Deck object internals

        :param card:        Instance of a card
        :param count:       How many copies are in the deck
        """
        return CardDeckType(instance=card, count=count, id=card.id)


class Overview:
    """A helper object for quick glances over the deck contents."""
    def __init__(self, deck: Deck) -> None:
        """
        :param deck:    An instantiated deck object
        """
        self.deck = deck

    def items(self, sub_type: str = None, return_filter: bool = False) -> Union[List[Item], CardFilter]:
        """
        All the items in the deck.

        :param sub_type:            Whether to list only certain sub type of the items
        :param return_filter:       Whether to return a :py:class:`pyartifact.CardFilter` object or just a List of cards
        """
        items = CardFilter(cards=self.deck.expand_cards(hero_includes=False)).type(Item)
        if sub_type is not None:
            items = items.sub_type(sub_type)
        if not return_filter:
            return items.cards
        return items

    def spells(self, return_filter: bool = False) -> Union[List[Spell], CardFilter]:
        """
        All the spells in the deck.

        :param return_filter:       Whether to return a :py:class:`pyartifact.CardFilter` object or just a List of cards
        """
        spells = CardFilter(cards=self.deck.expand_cards()).type(Spell)
        if not return_filter:
            return spells.cards
        return spells

    def heroes(self, return_filter: bool = False) -> Union[List[Hero], CardFilter]:
        """
        All the heroes in the deck, sorted by their turns of deployment.

        :param return_filter:       Whether to return a :py:class:`pyartifact.CardFilter` object or just a List of cards
        """
        heroes = [h['instance'] for h in sorted(self.deck.heroes, key=lambda x: x['turn'])]
        if return_filter:
            return CardFilter(cards=heroes)
        return heroes

    def improvements(self, return_filter: bool = False) -> Union[List[Improvement], CardFilter]:
        """
        All the improvements in the deck.

        :param return_filter:       Whether to return a :py:class:`pyartifact.CardFilter` object or just a List of cards
        """
        improvements = CardFilter(cards=self.deck.expand_cards()).type(Improvement)
        if not return_filter:
            return improvements.cards
        return improvements

    def creeps(self, return_filter: bool = False) -> Union[List[Creep], CardFilter]:
        """
        All the creeps in the deck.

        :param return_filter:       Whether to return a :py:class:`pyartifact.CardFilter` object or just a List of cards
        """
        creeps = CardFilter(cards=self.deck.expand_cards()).type(Creep)
        if not return_filter:
            return creeps.cards
        return creeps

    def items_per_subtype(self) -> Dict[str, List[Item]]:
        """
        A more detailed overview of items on the deck in a form of defaultdict(list) where each key is a sub type
        and it's value is a list of those items.
        """
        result: Dict[str, List[Item]] = defaultdict(list)
        for item in self.items():
            result[item.sub_type].append(item)
        return result
