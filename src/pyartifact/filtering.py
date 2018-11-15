from typing import Optional, Iterable, Union, List, Tuple

from .exceptions import UnknownFilterArgument
from .sets_and_cards import CardSet, CardTypes, CardTypesInstanced, AVAILABLE_TYPES, STR_TO_CARD_TYPE


def convert_card_type(type_: Union[str, CardTypes]) -> CardTypes:
    if isinstance(type_, AVAILABLE_TYPES):
        return type_
    else:
        try:
            return STR_TO_CARD_TYPE[type_]
        except KeyError:
            raise UnknownFilterArgument(f'Unrecognized card type: {type_}')


def convert_card_types(card_types: Iterable[Union[str, CardTypes]]) -> Tuple[CardTypes, ...]:
    return tuple([convert_card_type(ct) for ct in card_types])


class CardFilter:
    def __init__(
            self,
            sets:
            Optional[Iterable[CardSet]] = None,
            cards: Optional[Iterable[CardTypesInstanced]] = None
    ) -> None:
        self.cards: List[CardTypesInstanced] = list(cards) if cards else list()
        if sets:
            for card_set in sets:
                for card in card_set.data.card_list:  # type: ignore
                    self.cards.append(card)
        self._filtered: List[CardTypesInstanced] = []

    def __len__(self) -> int:
        return len(self.cards)

    def __str__(self) -> str:
        return f'<CardFilter: {self.cards}>'

    def __getitem__(self, item: int) -> 'CardTypesInstanced':
        return list(self.cards)[item]

    def type(self, type_: Union[str, CardTypes], filter_out=False) -> 'CardFilter':
        type_ = convert_card_type(type_)
        for card in self.cards:
            if filter_out:
                if not isinstance(card, type_):
                    self._filtered.append(card)
            else:
                if isinstance(card, type_):
                    self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def types_in(self, card_types: Iterable[Union[str, CardTypes]]) -> 'CardFilter':
        """
        Filters out cards that were not passed to this filter

        :param card_types:  Either strings of card types, or this library's classes of card types
        """
        card_types = convert_card_types(card_types)
        for card in self.cards:
            if isinstance(card, card_types):
                self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def types_not_in(self, card_types: Iterable[Union[str, CardTypes]]) -> 'CardFilter':
        """
        Filters out cards that were passed into this filter

        :param card_types:  Either strings of card types, or this library's classes of card types
        """
        card_types = convert_card_types(card_types)
        for card in self.cards:
            if not isinstance(card, card_types):
                self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def rarity(self, rarity: str) -> 'CardFilter':
        for card in self.cards:
            if hasattr(card, 'rarity'):
                if card.rarity == rarity:
                    self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def rarity_in(self, rarities: List[str]) -> 'CardFilter':
        for card in self.cards:
            if hasattr(card, 'rarity'):
                if card.rarity in rarities:
                    self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def rarity_not_in(self, rarities: List[str]) -> 'CardFilter':
        for card in self.cards:
            if hasattr(card, 'rarity'):
                if card.rarity not in rarities:
                    self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def color(self, color: str) -> 'CardFilter':
        for card in self.cards:
            if hasattr(card, 'color'):
                if card.color == color.lower():
                    self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def color_in(self, colors: Iterable[str]) -> 'CardFilter':
        colors = [color.lower() for color in colors]
        for card in self.cards:
            if hasattr(card, 'color'):
                if card.color in colors:
                    self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def color_not_in(self, colors: Iterable[str]) -> 'CardFilter':
        colors = [color.lower() for color in colors]
        for card in self.cards:
            if hasattr(card, 'color'):
                if card.color not in colors:
                    self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def mana_cost(
            self,
            gt: Optional[int] = None,
            gte: Optional[int] = None,
            lt: Optional[int] = None,
            lte: Optional[int] = None,
            eq: Optional[int] = None
    ) -> 'CardFilter':
        """
        Filters out cards by their mana cost, if they have one. This will always filter out cards without mana cost.
        If multiple arguments are passed, every card that fits at least one will pass the filter.

        :param gt:      Filters out cards that have higher mana cost than the number provided
        :param gte:     Filters out cards that have higher or equal mana cost than the number provided
        :param lt:      Filters out cards that have lower mana cost than the number provided
        :param lte:     Filters out cards that have lower or equal mana cost than the number provided
        :param eq:      Filters out cards that have mana cost equal to the number provided
        """
        for card in self.cards:
            if hasattr(card, 'mana_cost'):
                if gt is not None and card.mana_cost > gt:
                    self._filtered.append(card)
                elif gte is not None and card.mana_cost >= gte:
                    self._filtered.append(card)
                elif lt is not None and card.mana_cost < lt:
                    self._filtered.append(card)
                elif lte is not None and card.mana_cost <= lte:
                    self._filtered.append(card)
                elif eq is not None and card.mana_cost == eq:
                    self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def gold_cost(
            self,
            gt: Optional[int] = None,
            gte: Optional[int] = None,
            lt: Optional[int] = None,
            lte: Optional[int] = None,
            eq: Optional[int] = None
    ) -> 'CardFilter':
        """
        Filters out cards by their gold cost, if they have one. This will always filter out cards without gold cost.
        If multiple arguments are passed, every card that fits at least one will pass the filter.

        :param gt:      Filters out cards that have higher gold cost than the number provided
        :param gte:     Filters out cards that have higher or equal gold cost than the number provided
        :param lt:      Filters out cards that have lower gold cost than the number provided
        :param lte:     Filters out cards that have lower or equal gold cost than the number provided
        :param eq:      Filters out cards that have gold cost equal to the number provided
        """
        for card in self.cards:
            if hasattr(card, 'gold_cost'):
                if gt is not None and card.gold_cost > gt:
                    self._filtered.append(card)
                elif gte is not None and card.gold_cost >= gte:
                    self._filtered.append(card)
                elif lt is not None and card.gold_cost < lt:
                    self._filtered.append(card)
                elif lte is not None and card.gold_cost <= lte:
                    self._filtered.append(card)
                elif eq is not None and card.gold_cost == eq:
                    self._filtered.append(card)
        return CardFilter(cards=self._filtered)

    def sub_type(self, sub_type: str) -> 'CardFilter':
        """
        Filters out everything but items and leaves just items with a subtype equal to the provided string

        :param sub_type:    Sub type of an item
        """
        for card in self.cards:
            if getattr(card, 'sub_type') == sub_type:
                self._filtered.append(card)
        return CardFilter(cards=self._filtered)
