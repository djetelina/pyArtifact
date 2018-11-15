from typing import List, Optional

from ._context import ctx
from .filtering import CardFilter
from .sets_and_cards import CardSet, CardTypesInstanced


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
        :param localize:        Which language to fetch strings for, at this time only english is available
        """
        self._set_numbers = limit_sets or ctx.all_sets
        self.sets: List[CardSet] = [CardSet(set_number) for set_number in self._set_numbers]
        if localize is not None:
            ctx.language = localize

    def load_all_sets(self) -> None:
        """
        Loads all the sets it should load from the api.
        """
        ctx.cards_by_id = {}
        ctx.cards_by_name = {}
        for set_ in self.sets:
            set_.load()
        ctx.loaded_sets = self._set_numbers

    @property
    def filter(self) -> 'CardFilter':
        """
        Creates a new filter instance with all the cards.
        :return:
        """
        return CardFilter(sets=self.sets)

    # noinspection PyMethodMayBeStatic
    def get(self, name: str) -> 'CardTypesInstanced':
        """
        Gets a card instance by name

        :param name:    Name of the card (case insensitive)
        """
        return ctx.cards_by_name[name.lower()]

    def find(self, name_approx: str) -> 'CardTypesInstanced':
        raise NotImplementedError('Card lookup with approx. names is not yet implemented.')
