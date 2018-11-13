"""
TODO this while thing needs to be re-thought and rewritten
"""
from typing import List, Optional

from .context import ctx
from .deck_encoding.decode import decode_deck_string
from .deck_encoding.encode import encode_deck
from .deck_encoding.types import CardDecodedType, DeckContents
from .exceptions import PyArtifactException, InvalidHeroTurn, HeroTurnFull
from .sets_and_cards import Hero, CardTypesInstanced


class CardEnrichedType(CardDecodedType):
    card: CardTypesInstanced


class HeroDeployment:
    def __init__(
            self,
            turn_one: Optional[List[Optional[Hero]]] = None,
            turn_two: Optional[Hero] = None,
            turn_three: Optional[Hero] = None
    ) -> None:
        self.turn_one = turn_one if turn_one is not None else [None, None, None]
        self.turn_two = turn_two
        self.turn_three = turn_three

    @classmethod
    def from_list(cls, list_of_heroes: List[Optional[Hero]]) -> 'HeroDeployment':
        new = cls()
        for hero in list_of_heroes:
            new.add(hero)
        return new

    @property
    def valid(self) -> bool:
        """
        Whether the hero deployment is valid - all positions are filled
        """
        turn_one_heroes = len([h for h in self.turn_one if isinstance(h, Hero)]) == 3
        turn_two_hero = isinstance(self.turn_two, Hero)
        turn_three_hero = isinstance(self.turn_three, Hero)
        return turn_one_heroes and turn_two_hero and turn_three_hero

    @property
    def as_list(self) -> List[Optional[Hero]]:
        """
        Reruns the hero deployments as a list, where indexes 0-2 are turn one, 1 is turn two, 2 is turn three.
        If no hero is in a position, None is in it's place instead.
        The returned list is a standalone instance, if you want to apply it, construct new HeroDeployment `from_list`
        """
        as_list = self.turn_one.copy()
        as_list.append(self.turn_two)
        as_list.append(self.turn_three)
        return as_list

    @property
    def free_turns(self) -> List[int]:
        free_turns = []
        if len([h for h in self.turn_one if h is not None]) < 3:
            free_turns.append(1)
        if self.turn_two is None:
            free_turns.append(2)
        if self.turn_three is None:
            free_turns.append(3)
        return free_turns

    def add(self, hero: Optional[Hero], turn: Optional[int] = None) -> None:
        """
        Adds a hero.

        :param hero:    Instance of the hero, or None if you so desire.
        :param turn:    Which turn the hero will be deployed, otherwise first free will be automatically selected
        """
        turns = {
            1: self.turn_one,
            2: self.turn_two,
            3: self.turn_three,
            None: None
        }
        if turn is None:
            if self.free_turns:
                turn = self.free_turns[0]
            else:
                raise HeroTurnFull
        if turn not in turns.keys():
            raise InvalidHeroTurn

        if turns[turn] is self.turn_one:
            if len([h for h in self.turn_one if h is not None]) >= 3:
                raise HeroTurnFull
            else:
                self.turn_one[self.turn_one.index(None)] = hero
        else:
            if turns[turn] is not None:
                raise HeroTurnFull
            else:
                turns[turn] = hero


class Deck:
    def __init__(self, name: str, heroes: List[Optional[Hero]], cards: List[CardEnrichedType], deck_contents: DeckContents) -> None:
        # Take this with a big grain of salt for now
        self.name = name
        self._heroes = HeroDeployment.from_list(heroes)
        self._cards = cards
        self._deck_contents = deck_contents

    def __repr__(self) -> str:
        return f'<Artifact deck: {self.__dict__}>'

    @classmethod
    def from_code(cls, deck_code: str) -> 'Deck':
        if not ctx.cards_by_id:
            raise PyArtifactException("Deck constructor `from_code` can't be used without Card sets being loaded."
                                      "To get raw data use the function `pyartifact.decode_deck_string(deck_string)`")
        deck_contents = decode_deck_string(deck_code)

        hero_deployment = HeroDeployment()
        for hero in deck_contents['heroes']:
            hero_deployment.add(ctx.cards_by_id[hero['id']], turn=hero['turn'])

        enriched_cards: List[CardEnrichedType] = []
        for card in deck_contents['cards']:
            enriched_card: CardEnrichedType = dict(id=card['id'], count=card['count'], card=ctx.cards_by_id[card['id']])
            enriched_cards.append(enriched_card)

        return cls(name=deck_contents['name'], heroes=hero_deployment.as_list, cards=enriched_cards, deck_contents=deck_contents)

    @property
    def deck_code(self) -> str:
        return encode_deck(self._deck_contents)

    @property
    def cards(self) -> List[CardEnrichedType]:
        return self._cards

    @property
    def cards_expanded(self) -> List[CardTypesInstanced]:
        expanded = []
        for card in self._cards:
            for _ in range(card['count']):
                expanded.append(card['card'])
        for hero in self._heroes.as_list:
            if hero is not None:
                expanded += hero.includes
        return expanded

    def add_hero(self, hero: Hero, turn: Optional[int] = None) -> None:
        self._heroes.add(hero, turn)
