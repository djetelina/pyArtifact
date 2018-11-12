import re
from base64 import b64decode
from typing import List, Tuple, Dict


from .context import ctx
from .sets_and_cards import Hero, CardTypesInstanced
from .exceptions import InvalidDeckString


class Deck:
    current_verison = 2
    rgch_encoded_prefix = 'ADC'

    def __init__(self, name: str, heroes: List[Hero], cards: List[CardTypesInstanced]) -> None:
        # Take this with a big grain of salt for now
        self.name = name
        self.heroes_deployment = heroes
        self.cards = cards

    def __repr__(self) -> str:
        return f'<Artifact deck: {self.__dict__}>'

    @classmethod
    def decode(cls, deck_code: str) -> 'Deck':
        deck_bytes = _decode_string(deck_code)
        if not deck_bytes:
            raise InvalidDeckString
        name, heroes, cards = _parse_deck(deck_bytes)

        # Order in list matters
        turn_1_heroes = [ctx.cards_by_id[hero['id']] for hero in heroes if hero['turn'] == 1]
        turn_2_hero = [ctx.cards_by_id[hero['id']] for hero in heroes if hero['turn'] == 2]
        turn_3_hero = [ctx.cards_by_id[hero['id']] for hero in heroes if hero['turn'] == 3]
        heroes = turn_1_heroes + turn_2_hero + turn_3_hero

        # Expand for counts
        cards_expanded = []
        for card in cards:
            card_instance = ctx.cards_by_id[card['id']]
            print()
            for _ in range(card['count']):
                cards_expanded.append(card_instance)
        return cls(name=name, heroes=heroes, cards=cards_expanded)


def _decode_string(deck_code: str) -> List[int]:
    if not deck_code.startswith(Deck.rgch_encoded_prefix):
        raise InvalidDeckString("The provided deck string doesn't start with known prefix")

    deck_code = deck_code.lstrip(Deck.rgch_encoded_prefix)
    deck_code = deck_code.replace('-', '/').replace('_', '=')
    decoded = b64decode(deck_code)
    return list(decoded)


def _read_bits_chunk(chunk: int, numb_bits: int, curr_shift: int, out_bits: int) -> Tuple[int, bool]:
    continue_bit = 1 << numb_bits
    new_bits = chunk & (continue_bit - 1)
    out_bits |= (new_bits << curr_shift)
    return out_bits, (chunk & continue_bit) != 0


def _read_var_encoded(base_value: int, base_bits: int, data: List[int],
                      index_start: int, index_end: int) -> Tuple[int, int]:
    out_value = 0
    delta_shift = 0
    out_value, unknown_thing = _read_bits_chunk(base_value, base_bits, delta_shift, out_value)
    if (base_bits == 0) or unknown_thing:
        delta_shift += base_bits
        while True:
            if index_start > index_end:
                raise Exception("dunno, more room?")
            next_byte = data[index_start]
            index_start += 1
            out_value, unknown_thing = _read_bits_chunk(next_byte, 7, delta_shift, out_value)
            if not unknown_thing:
                break
            delta_shift += 7
    return out_value, index_start


def _parse_deck(deck_bytes: List[int]) -> Tuple[str, List[Dict[str, int]], List[Dict[str, int]]]:
    total_bytes: int = len(deck_bytes)
    computed_checksum: int = 0
    total_card_bytes: int = 0
    checksum: int = 0
    version_and_heroes: int = 0
    string_length: int = 0
    version: int = 0
    for index, deck_byte in enumerate(deck_bytes):
        if index == 0:
            version_and_heroes = deck_byte
            version = version_and_heroes >> 4
            if Deck.current_verison != version:
                raise InvalidDeckString("Loading unknown deck string version")
        elif index == 1:
            checksum = deck_byte
        elif index == 2:
            string_length = 0
            if version > 1:
                string_length = deck_byte
            total_card_bytes = total_bytes - string_length
        elif index in range(3, total_card_bytes):
            computed_checksum += deck_byte
        else:
            break
    current_index: int = 3
    masked = computed_checksum & 0xFF
    if checksum != masked:
        raise InvalidDeckString("Checksum is wrong")

    number_of_heroes, current_index = _read_var_encoded(version_and_heroes, 3, deck_bytes, current_index,
                                                        total_card_bytes)
    heroes = []
    previous_card_base: int = 0
    for i in range(number_of_heroes):
        current_index, previous_card_base, hero_turn, hero_card_id = _read_serialized_card(deck_bytes,
                                                                                           current_index,
                                                                                           total_card_bytes,
                                                                                           previous_card_base)
        heroes.append(dict(id=hero_card_id, turn=hero_turn))

    cards = []
    previous_card_base = 0
    while current_index <= total_card_bytes:
        current_index, previous_card_base, card_count, card_id = _read_serialized_card(deck_bytes,
                                                                                       current_index,
                                                                                       total_bytes,
                                                                                       previous_card_base)
        cards.append(dict(id=card_id, count=card_count))
    name = ''
    if current_index <= total_bytes:
        some_bytes = deck_bytes[(-1 * string_length):]
        some_bytes = map(chr, some_bytes)
        name = ''.join(some_bytes)
        # WIP simple sanitizer
        name = re.sub('<[^<]+?>', '', name)
    return name, heroes, cards


def _read_serialized_card(data: List[int], index_start: int, index_end: int, prev_card_base: int) -> Tuple[int, int, int, int]:
    if index_start > index_end:
        raise Exception("End of memory or some shit, dunno, php sucks")

    # Header contains the count (2 bits), a continue flag, and 5 bits of offset data.
    # If we have 11 for the count bits we have the count encoded after the offset.
    header = data[index_start]
    index_start += 1
    has_extended_count = (header >> 6) == 0x03

    # Read in the delta, which has 5 bits in the header, then additional bytes while the value is set
    card_delta, index_start = _read_var_encoded(header, 5, data, index_start, index_end)
    out_card_id = prev_card_base + card_delta
    if has_extended_count:
        out_count, index_start = _read_var_encoded(0, 0, data, index_start, index_end)
    else:
        out_count = (header >> 6) + 1
    prev_card_base = out_card_id
    return index_start, prev_card_base, out_count, out_card_id
