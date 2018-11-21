from collections import defaultdict
from typing import List, Optional, Union

from fuzzywuzzy import fuzz

from ._context import ctx
from .filtering import CardFilter
from .sets_and_cards import CardSet, CardTypesInstanced, NotAbility


class Cards:
    """
    Synchronous API around Artifact API sets of cards
    """
    def __init__(
            self,
            limit_sets: Optional[List[str]] = None,
            localize: Optional[str] = None,
    ) -> None:
        """
        :param limit_sets:      Whether to only fetch some sets, by default all ar used ('00', and '01')
        :param localize:        Which language to fetch strings for. Will be turned into lowercase automatically.
        """
        self._set_numbers = limit_sets or ctx.all_sets
        self.sets: List[CardSet] = [CardSet(set_number) for set_number in self._set_numbers]
        if localize is not None:
            ctx.language = localize.lower()
        self.__cards_expanded = []

    def __getitem__(self, item):
        return self.__cards_expanded[item]

    def load_all_sets(self) -> None:
        """
        Loads all the sets it should load from the api.
        """
        ctx.cards_by_id = {}
        ctx.cards_by_name = defaultdict(list)
        self.__cards_expanded = []
        for set_ in self.sets:
            set_.load()
        ctx.loaded_sets = self._set_numbers
        for set in self.sets:
            for card in set.data.card_list:
                self.__cards_expanded.append(card)

    @property
    def filter(self) -> 'CardFilter':
        """
        Creates a new filter instance with all the cards.
        :return:
        """
        return CardFilter(cards=self.__cards_expanded)

    # noinspection PyMethodMayBeStatic
    def get(self, name: str, ignore_shared_name: bool = True) -> Union['CardTypesInstanced', List['CardTypesInstanced']]:
        """
        Gets a card instance by name.

        This is is a bit problematic, because some cards can have the same names as their ability.
        By default, this library will ignore that fact and return the not ability card.
        If it fails to find a card that's not an ability, it'll return the first one it registered.

        You can override this behavior in which case this method will return a list of cards,
        instead of the card directly.

        :param name:                Name of the card (case insensitive)
        :param ignore_shared_name:  If there are more cards with the same name, get just the first hit.
        """
        cards_found = ctx.cards_by_name[name.lower()]
        if ignore_shared_name:
            for card in cards_found:
                # Find the first card that's not an ability
                if issubclass(card.__class__, NotAbility):
                    return card
            # If it's all abilities for some reason, just return the first one
            return cards_found[0]
        return cards_found

    def find(self, name_approx: str, threshold: int = 75) -> Optional['CardTypesInstanced']:
        """
        Finds a card by name, doesn't have to be exact name, thanks to highly sophisticated AI - a.k.a.
        simple algorithm, that will try and guess what was meant.

        This algorithm can change over time so don't expect the same results across different versions.

        :param name_approx:             Name to look up
        :param threshold:               How strict to be, higher number -> less likely to
                                        find a result if the name is off, higher chance the result will be correct
        """
        result = None

        if name_approx in ctx.cards_by_name.keys():
            return self.get(name_approx)
        name_scores = {}
        for name in ctx.cards_by_name.keys():
            score = fuzz.WRatio(name_approx, name)
            if score >= threshold:
                name_scores[name] = score

        max_score = max(name_scores.values())
        for name, score in name_scores.items():
            if score == max_score:
                instantiated = ctx.cards_by_name[name]
                try:
                    result = [inst for inst in instantiated if issubclass(inst.__class__, NotAbility)][0]
                except IndexError:
                    continue
                return result
