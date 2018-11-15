import re
from base64 import b64decode
from typing import List, Tuple

from .types import HeroDecodedType, CardDecodedType, DeckContents
from ..exceptions import InvalidDeckString, DeckDecodeException

# Version 1: Heroes and Cards
# Version 2: Name, Heroes and Cards
SUPPORTED_VERSIONS = [1, 2]


def decode_deck_string(deck_code: str) -> DeckContents:
    """
    Takes in deck code, e.g. 'ADCJWkTZX05uwGDCRV4XQGy3QGLmqUBg4GQJgGLGgO7AaABR3JlZW4vQmxhY2sgRXhhbXBsZQ__'
    and decodes it into a dict of name, heroes and cards.

    :param deck_code:               Deck code
    :return:                        Deck contents
    :raises InvalidDeckString:      When an invalid deck string is provided, e.g. unknown version, bad checksum etc.
    :raises DeckDecodeException:    When something odd happens while decoding
    """
    return Decoder(deck_code).deck_contents


class Decoder:
    prefix = 'ADC'

    def __init__(self, deck_code: str) -> None:
        """
        :param deck_code:       Deck code
        """
        self.deck_code = deck_code
        self._binary = bytearray()

    @property
    def deck_contents(self) -> DeckContents:
        self._decode_string()
        self._get_version_and_heroes()
        self._get_lengths_and_calc_checksum()
        self._parse_deck()
        return self._deck_contents

    def _decode_string(self) -> None:
        if not self.deck_code.startswith(self.prefix):
            raise InvalidDeckString("The provided deck string doesn't start with a known prefix")
        # Strip the prefix and turn it into a valid base64 from url-safe string
        deck_code_b64 = self.deck_code.lstrip(self.prefix).replace('-', '/').replace('_', '=')
        decoded = b64decode(deck_code_b64)
        self._binary = bytearray(decoded)
        # If something funky happened, let the user know that it's terrible
        if not self._binary:
            raise InvalidDeckString("No binary data could be decoded from the string")

    def _parse_deck(self) -> None:
        # Read the rest of heroes count and get the moved 'cursor'
        self._heroes_count, self._current_index = self._read_var_encoded(self._version_and_heroes, 3,
                                                                         self._card_bytes_start_index,
                                                                         self._total_card_bytes)
        # Read the list of heroes
        heroes: List[HeroDecodedType] = []
        self._previous_card_base: int = 0
        for _ in range(self._heroes_count):
            hero_turn, hero_card_id = self._read_serialized_card(read_until_index=self._total_card_bytes)
            heroes.append(HeroDecodedType(id=hero_card_id, turn=hero_turn))

        # Read the list of cards
        cards: List[CardDecodedType] = []
        self._previous_card_base = 0
        while self._current_index < self._total_card_bytes:
            card_count, card_id = self._read_serialized_card(read_until_index=len(self._binary))
            cards.append(CardDecodedType(id=card_id, count=card_count))

        # Read the name if it's present
        if self._name_length:
            name = self._binary[-self._name_length:].decode()
            # WIP simple html sanitizer
            name = re.sub('<[^<]+?>', '', name)
        else:
            name = ''

        self._deck_contents = DeckContents(name=name, heroes=heroes, cards=cards)

    def _get_version_and_heroes(self) -> None:
        """Reads the deck code version and first part of number of heroes from the first byte."""
        self._version_and_heroes = self._binary[0]
        self.version = self._version_and_heroes >> 4
        if self.version not in SUPPORTED_VERSIONS:
            raise InvalidDeckString(f"Deck string has incompatible version '{self.version}', "
                                    f"supported versions are: {SUPPORTED_VERSIONS}")

    def _get_lengths_and_calc_checksum(self) -> None:
        """
        Depending on the deck code version reads where the card information starts,
        how long is the name of the deck and completes the checksum.
        """
        computed_checksum = 0
        if self.version == 1:
            self._name_length = 0
            computed_checksum += self._binary[2]
            self._card_bytes_start_index = 2
        else:
            self._name_length = self._binary[2]
            self._card_bytes_start_index = 3
        self._total_card_bytes = len(self._binary) - self._name_length

        computed_checksum = sum(b for b in self._binary[self._card_bytes_start_index:self._total_card_bytes])
        if self._binary[1] != (computed_checksum & 0xFF):
            raise InvalidDeckString("Checksum doesn't check out")

    def _read_var_encoded(self, base_value: int, base_bits: int, index: int, max_index: int) -> Tuple[int, int]:
        """
        Reads an encoded variable

        :param base_value:  When there was another int the byte at index, what that int was, so we can read the next one
        :param base_bits:   How many bits did the base value have
        :param index:       At which index of the binary data to start
        :param max_index:   At which index must the currently read variable end
        :return:            Tuple of the variable and new position of the index 'cursor' in the binary data
        """
        value = 0
        delta_shift = 0
        value, unknown_thing = _read_bits_chunk(base_value, base_bits, delta_shift, value)
        if (base_bits == 0) or unknown_thing:
            delta_shift += base_bits
            while True:
                if index > max_index:
                    raise DeckDecodeException("Couldn't read a variable from the string.")
                next_byte = self._binary[index]
                index += 1
                value, unknown_thing = _read_bits_chunk(next_byte, 7, delta_shift, value)
                if not unknown_thing:
                    break
                delta_shift += 7
        return value, index

    def _read_serialized_card(self, read_until_index: int) -> Tuple[int, int]:
        """
        Reads a serialized card.

        :param read_until_index:    At which index must the card end
        """
        # Check if we aren't already off limits
        if self._current_index > read_until_index:
            raise DeckDecodeException("Couldn't read a serialized card")

        # Header byte of the card contains the count (turn) information if it's lower than 3
        # and a first part of card id delta information after that
        header = self._binary[self._current_index]
        self._current_index += 1

        # Read the card id delta
        card_id_delta, self._current_index = self._read_var_encoded(header, 5, self._current_index, read_until_index)
        # Add the previous id to the delta we just decoded
        card_id = self._previous_card_base + card_id_delta
        # If the header didn't have the real count information, read it from the next bytes
        if (header >> 6) == 3:
            count, self._current_index = self._read_var_encoded(0, 0, self._current_index, read_until_index)
        else:
            # If the header had it, shift it and subtract 2 from it
            count = (header >> 6) + 1

        self._previous_card_base = card_id
        return count, card_id


def _read_bits_chunk(chunk: int, numb_bits: int, curr_shift: int, out_bits: int) -> Tuple[int, bool]:
    """Reads a chunk of bits from a byte."""
    continue_bit = 1 << numb_bits
    new_bits = chunk & (continue_bit - 1)
    out_bits |= (new_bits << curr_shift)
    return out_bits, (chunk & continue_bit) != 0
