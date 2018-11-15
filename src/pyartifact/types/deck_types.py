from typing import List

from mypy_extensions import TypedDict

from ..sets_and_cards import Hero, CardTypesInstanced


class HeroDecodedType(TypedDict):
    id: int
    turn: int


class HeroDeckType(HeroDecodedType, total=False):
    instance: Hero


class CardDecodedType(TypedDict):
    id: int
    count: int


class CardDeckType(CardDecodedType, total=False):
    instance: CardTypesInstanced


class DeckContentsBase(TypedDict):
    cards: List[CardDeckType]
    heroes: List[HeroDeckType]


class DeckContents(DeckContentsBase, total=False):
    name: str
