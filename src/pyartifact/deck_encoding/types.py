from typing import List

from mypy_extensions import TypedDict


class HeroDecodedType(TypedDict):
    id: int
    turn: int


class CardDecodedType(TypedDict):
    id: int
    count: int


class DeckContentsBase(TypedDict):
    cards: List[CardDecodedType]
    heroes: List[HeroDecodedType]


class DeckContents(DeckContentsBase, total=False):
    name: str
