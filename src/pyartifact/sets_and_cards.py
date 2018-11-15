from typing import Optional, List, Union, Type, Dict

import requests

from ._context import ctx
from .types.json_types import CardSetType, SetInfoType, SetDataType, ReferenceType


class CardBase:
    """Each card has this."""
    def __init__(self, **kwargs) -> None:
        self.id: int = kwargs['card_id']
        self.base_id: int = kwargs['base_card_id']
        self.name: str = kwargs['card_name'][ctx.language]
        self.type: str = kwargs['card_type']
        self.text: str = kwargs['card_text'].get(ctx.language, '')
        self.mini_image: str = kwargs['mini_image'].get('default')
        self.large_image: str = kwargs['large_image'].get('default')
        self.ingame_image: str = kwargs['ingame_image'].get('default')
        self.__references: List[ReferenceType] = kwargs['references']

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Artifact card: {self.__dict__}>'

    @property
    def includes(self) -> List['CardTypesInstanced']:
        """List of all the cards this card includes automatically in a deck."""
        includes = []
        for ref in self.__references:
            if ref['ref_type'] == 'includes':
                included = ctx.cards_by_id[ref['card_id']]
                for _ in range(ref['count']):
                    includes.append(included)
        return includes

    @property
    def passive_abilities(self) -> List['PassiveAbility']:
        """List of the cards passive abilities"""
        passive_abilities = []
        for ref in self.__references:
            if ref['ref_type'] == 'passive_ability':
                ability = ctx.cards_by_id[ref['card_id']]
                passive_abilities.append(ability)
        return passive_abilities

    @property
    def active_abilities(self) -> List['Ability']:
        """List of the cards active abilities"""
        abilities = []
        for ref in self.__references:
            if ref['ref_type'] == 'active_ability':
                ability = ctx.cards_by_id[ref['card_id']]
                abilities.append(ability)
        return abilities

    @property
    def references(self) -> List['CardTypesInstanced']:
        """List of cards that this card references"""
        references = []
        for ref in self.__references:
            if ref['ref_type'] == 'references':
                reference = ctx.cards_by_id[ref['card_id']]
                references.append(reference)
        return references


class ColoredCard:
    def __init__(self, **kwargs) -> None:
        if kwargs.get('is_blue', False):
            self.color: str = 'blue'
        elif kwargs.get('is_black', False):
            self.color = 'black'
        elif kwargs.get('is_red', False):
            self.color = 'red'
        elif kwargs.get('is_green', False):
            self.color = 'green'
        else:  # in case future sets introduce new colors, this way it won't break this library
            self.color = 'unknown'


class Unit:
    def __init__(self, **kwargs) -> None:
        self.attack: int = kwargs.get('attack', 0)
        self.armor: int = kwargs.get('armor', 0)
        self.hit_points: int = kwargs.get('hit_points', 0)


class Collectible:
    """Doesn't mean that EVERY card of that type is Collectible, all subtypes have a few  exceptions in the base set."""
    def __init__(self, **kwargs) -> None:
        self.rarity: Optional[str] = kwargs.get('rarity')
        self.item_def: Optional[int] = kwargs.get('item_def')


class Castable:
    def __init__(self, **kwargs) -> None:
        self.mana_cost: int = kwargs['mana_cost']


class Hero(CardBase, ColoredCard, Unit, Collectible):
    def __init__(self, **kwargs) -> None:
        CardBase.__init__(self, **kwargs)
        ColoredCard.__init__(self, **kwargs)
        Unit.__init__(self, **kwargs)
        Collectible.__init__(self, **kwargs)
        self.illustrator: str = kwargs['illustrator']


class PassiveAbility(CardBase):
    def __init__(self, **kwargs) -> None:
        CardBase.__init__(self, **kwargs)


class Spell(CardBase, ColoredCard, Collectible, Castable):
    def __init__(self, **kwargs) -> None:
        CardBase.__init__(self, **kwargs)
        ColoredCard.__init__(self, **kwargs)
        Collectible.__init__(self, **kwargs)
        Castable.__init__(self, **kwargs)
        self.illustrator: str = kwargs['illustrator']


class Creep(CardBase, ColoredCard, Unit, Collectible, Castable):
    def __init__(self, **kwargs):
        CardBase.__init__(self, **kwargs)
        ColoredCard.__init__(self, **kwargs)
        Unit.__init__(self, **kwargs)
        Collectible.__init__(self, **kwargs)
        Castable.__init__(self, **kwargs)
        self.illustrator: Optional[str] = kwargs.get('illustrator')


class Ability(CardBase):
    def __init__(self, **kwargs) -> None:
        CardBase.__init__(self, **kwargs)


class Item(CardBase, Collectible):
    def __init__(self, **kwargs) -> None:
        CardBase.__init__(self, **kwargs)
        Collectible.__init__(self, **kwargs)
        self.illustrator: str = kwargs['illustrator']
        self.gold_cost: int = kwargs['gold_cost']
        self.sub_type: str = kwargs['sub_type']


class Improvement(CardBase, ColoredCard, Collectible, Castable):
    def __init__(self, **kwargs) -> None:
        CardBase.__init__(self, **kwargs)
        ColoredCard.__init__(self, **kwargs)
        Collectible.__init__(self, **kwargs)
        Castable.__init__(self, **kwargs)
        self.illustrator: str = kwargs['illustrator']


class SetInfo:
    def __init__(self, set_info: SetInfoType) -> None:
        self.set_id: int = set_info['set_id']
        self.pack_item_def: int = set_info['pack_item_def']
        self.name: str = set_info['name'][ctx.language]


CardTypesInstanced = Union[Item, Hero, Ability, PassiveAbility, Improvement, Creep, Spell]
CardTypes = Union[
    Type[Item], Type[Hero], Type[Ability], Type[PassiveAbility],
    Type[Improvement], Type[Creep], Type[Spell]
]
STR_TO_CARD_TYPE: Dict[str, CardTypes] = {
    'Hero': Hero,
    'Passive Ability': PassiveAbility,
    'Spell': Spell,
    'Creep': Creep,
    'Ability': Ability,
    'Item': Item,
    'Improvement': Improvement
}
AVAILABLE_TYPES = (Item, Hero, Ability, PassiveAbility, Improvement, Creep, Spell)


class CardSetData:
    # Stronghold and Pathing are core game mechanics, there's no need to be indexing them
    not_indexed = ['Stronghold', 'Pathing']

    def __init__(self, data: CardSetType) -> None:
        self.version: int = data['version']
        self.set_info = SetInfo(data['set_info'])
        self.card_list: List[CardTypesInstanced] = []
        for card in data['card_list']:
            if card['card_type'] not in self.not_indexed:
                type_of_card = STR_TO_CARD_TYPE[card['card_type']]  # type: CardTypes
                card_instance = type_of_card(**card)
                self.card_list.append(card_instance)
                # For fast lookups
                ctx.cards_by_id[card['base_card_id']] = card_instance
                ctx.cards_by_name[card['card_name'][ctx.language].lower()] = card_instance


class CardSet:
    base_url = 'https://playartifact.com/cardset/'

    def __init__(self, set_number: str) -> None:
        self.url = f'{self.base_url}{set_number}'
        self.expire_time = None
        self.data: Optional[CardSetData] = None

    def load(self) -> None:
        cdn_info = requests.get(self.url).json()
        self.expire_time = cdn_info['expire_time']
        data: SetDataType = requests.get(f"{cdn_info['cdn_root']}{cdn_info['url']}").json()
        self.data = CardSetData(data['card_set'])
