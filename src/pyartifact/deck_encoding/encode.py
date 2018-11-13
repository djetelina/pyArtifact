import re
from base64 import b64encode

from .types import DeckContents

ENCODED_PREFIX = 'ADC'
# Version 1: Heroes and Cards
# Version 2: Name, Heroes and Cards
SUPPORTED_VERSIONS = [2]
MAX_BYTES_FOR_VAR = 5
HEADER_SIZE = 3


def encode_deck(deck_contents: DeckContents, version: int = SUPPORTED_VERSIONS[-1]) -> str:
    """
    Encodes deck content into a deck code string.

    :param deck_contents:   A dictionary with name, heroes and cards (without those included automatically)
    :param version:         Deck code version, atm only 2 and higher is supported
    :return:                Deck code
    """
    encoder = Encoder(deck_contents, version=version)
    return encoder.deck_code


class Encoder:
    def __init__(self, deck_contents: DeckContents, version: int = SUPPORTED_VERSIONS[-1]) -> None:
        self.version = version
        self.deck_contents = deck_contents
        self.heroes = sorted(deck_contents['heroes'], key=lambda x: x['id'])
        self.cards = sorted(deck_contents['cards'], key=lambda x: x['id'])
        self.name = deck_contents.get('name', '')
        if self.name:
            self.name = re.sub('<[^<]+?>', '', self.name)
        self.byte_array = bytearray()

    @property
    def deck_code(self) -> str:
        # So we don't have to call encode manually every time
        if not self.byte_array:
            self.encode()
        encoded = b64encode(bytes(self.byte_array)).decode()
        deck_code = (ENCODED_PREFIX + encoded)
        deck_code = deck_code.replace('/', '-').replace('=', '_')
        return deck_code

    def encode(self) -> bytearray:
        version = (self.version << 4) | _extract_n_bits_with_carry(len(self.heroes), 3)
        self.byte_array.append(version)
        dummy_checksum = 0
        checksum_byte = len(self.byte_array)
        self.byte_array.append(dummy_checksum)
        if self.name:
            trim_len = len(self.name)
            while trim_len > 63:
                amount_to_trim = int((trim_len - 63) / 4)
                amount_to_trim = amount_to_trim if (amount_to_trim > 1) else 1
                self.name = self.name[:len(self.name) - amount_to_trim]
        self.byte_array.append(len(self.name))
        self._add_remaining_number_to_buffer(len(self.heroes), 3)

        previous_card_id = 0
        for hero in self.heroes:
            self._add_card_to_buffer(hero['turn'], hero['id'] - previous_card_id)
            previous_card_id = hero['id']

        previous_card_id = 0
        for card in self.cards:
            self._add_card_to_buffer(card['count'], card['id'] - previous_card_id)
            previous_card_id = card['id']
        string_byte_count = len(self.byte_array)
        name_bytes = bytearray(self.name.encode())
        for name_byte in name_bytes:
            self.byte_array.append(name_byte)
        full_checksum = self._compute_checksum(string_byte_count - HEADER_SIZE)
        small_checksum = full_checksum & 0x0FF
        self.byte_array[checksum_byte] = small_checksum
        return self.byte_array

    def _compute_checksum(self, number_of_bytes: int) -> int:
        checksum = 0
        for index in range(HEADER_SIZE, number_of_bytes + HEADER_SIZE):
            single_byte = self.byte_array[index]
            checksum += single_byte
        return checksum

    def _add_remaining_number_to_buffer(self, value: int, already_written_bits: int) -> None:
        value >>= already_written_bits
        # num_bytes seem unused, we'll see
        num_bytes = 0
        while value > 0:
            next_byte = _extract_n_bits_with_carry(value, 7)
            value >>= 7
            self.byte_array.append(next_byte)
            num_bytes += 1

    def _add_card_to_buffer(self, count, value) -> None:
        bytes_start = len(self.byte_array)
        first_byte_max_count = 0x03
        extended_count = ((count - 1) >= first_byte_max_count)
        first_byte_count = first_byte_max_count if extended_count else (count - 1)
        first_byte = first_byte_count << 6
        first_byte |= _extract_n_bits_with_carry(value, 5)
        self.byte_array.append(first_byte)
        self._add_remaining_number_to_buffer(value, 5)
        if extended_count:
            self._add_remaining_number_to_buffer(count, 0)
        count_bytes_end = len(self.byte_array)
        if count_bytes_end - bytes_start > 11:
            raise Exception("This library didn't work properly")


def _extract_n_bits_with_carry(value: int, num_bits: int) -> int:
    limit_bit = 1 << num_bits
    result = value & (limit_bit - 1)
    if value >= limit_bit:
        result |= limit_bit
    return result
