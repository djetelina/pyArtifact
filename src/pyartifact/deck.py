import logging
from typing import List

from .context import ctx
from .deck_encoding.decode import decode_deck_string
from .exceptions import PyArtifactException
from .sets_and_cards import Hero, CardTypesInstanced


class Deck:
    def __init__(self, name: str, heroes: List[Hero], cards: List[CardTypesInstanced]) -> None:
        # Take this with a big grain of salt for now
        self.name = name
        self.heroes_deployment = heroes
        self.cards = cards

    def __repr__(self) -> str:
        return f'<Artifact deck: {self.__dict__}>'

    @classmethod
    def from_code(cls, deck_code: str) -> 'Deck':
        if not ctx.cards_by_id:
            raise PyArtifactException("Deck constructor `from_code` can't be used without Card sets being loaded."
                                      "To get raw data use the function `pyartifact.decode_deck_string(deck_string)`")
        name, heroes, cards = decode_deck_string(deck_code)

        # Order in list matters
        turn_1_heroes = [ctx.cards_by_id[hero['id']] for hero in heroes if hero['turn'] == 1]
        turn_2_hero = [ctx.cards_by_id[hero['id']] for hero in heroes if hero['turn'] == 2]
        turn_3_hero = [ctx.cards_by_id[hero['id']] for hero in heroes if hero['turn'] == 3]
        heroes = turn_1_heroes + turn_2_hero + turn_3_hero

        # Expand for counts
        cards_expanded = []
        for card in cards:
            try:
                card_instance = ctx.cards_by_id[card['id']]
            except KeyError:
                logging.warning("Unknown card id found in the deck string, omitting from the final deck")
                continue
            for _ in range(card['count']):
                cards_expanded.append(card_instance)
        return cls(name=name, heroes=heroes, cards=cards_expanded)
