from typing import List, Dict

from mypy_extensions import TypedDict

# Key is language (atm only english), value is text, which includes html
LocalizedText = Dict[str, str]
# Key is so far only default, value is the url
ImageUrl = Dict[str, str]


class ReferenceTypeBase(TypedDict):
    card_id: int
    ref_type: str  # includes, passive_ability, active_ability, references


class ReferenceType(ReferenceTypeBase, total=False):
    count: int


class SetInfoType(TypedDict):
    set_id: int
    pack_item_def: int
    name: LocalizedText


class CardListDataType(TypedDict, total=False):
    card_id: int
    base_card_id: int
    card_type: str  # Hero, Passive Ability, Spell, Creep, Ability, Item, Improvement
    sub_type: str
    gold_cost: int
    mana_cost: int
    card_name: LocalizedText
    card_text: LocalizedText
    mini_image: ImageUrl
    large_image: ImageUrl
    ingame_image: ImageUrl
    illustrator: str
    rarity: str  # Common, Uncommon, Rare
    is_blue: bool
    is_red: bool
    is_black: bool
    is_green: bool
    item_def: int
    attack: int
    armor: int
    hit_points: int
    references: List[ReferenceType]


class CardSetType(TypedDict):
    version: int
    set_info: SetInfoType
    card_list: List[CardListDataType]


class SetDataType(TypedDict):
    card_set: CardSetType
