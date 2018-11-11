from typing import List, Optional

from .sets_and_cards import CardSet, CardTypesInstanced
from .filtering import CardFilter
from .context import ctx


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
        :param raw_data:        Whether you want to use the raw json data from the api, or the object mapping
                                provided by this library
        """
        self._set_numbers = limit_sets or ['00', '01']
        self.sets: List[CardSet] = [CardSet(set_number) for set_number in self._set_numbers]
        if localize is not None:
            ctx.language = localize

    def load_all_sets(self):
        ctx.cards_by_id = {}
        ctx.cards_by_name = {}
        for set in self.sets:
            set.load()

    @property
    def filter(self) -> 'CardFilter':
        return CardFilter(sets=self.sets)

    def get(self, name: str) -> 'CardTypesInstanced':
        return ctx.cards_by_name[name.lower()]

    def find(self, name_approx: str) -> 'CardTypesInstanced':
        raise NotImplementedError('Card lookup with approx. names is not yet implemented.')
