"""
Logic for encoding deck into a deck code string.

Encoding is done by writing a few things into a bytearray thanks to the magic of bitwise operations.
That is then encoded to base64 and sanitized for url usage.
"""
import re
from base64 import b64encode

from pyartifact.exceptions import DeckEncodeException
from .types import DeckContents

# Version 1: Heroes and Cards
# Version 2: Name, Heroes and Cards
SUPPORTED_VERSIONS = [2]


def encode_deck(deck_contents: DeckContents, version: int = SUPPORTED_VERSIONS[-1]) -> str:
    """
    Encodes deck content into a deck code string.

    :param deck_contents:   A dictionary with name, heroes and cards (without those included automatically)
    :param version:         Deck code version, atm only 2 and higher is supported
    :return:                Deck code
    """
    return Encoder(deck_contents, version=version).deck_code


class Encoder:
    """
    Main purpose of this class is to hold shared data across the encoding process.

    There shouldn't be a need to use this part of the library, It offers a more low level access
    to the encoding process, but doesn't offer anything more practical than :py:func:`pyartifact.encode_deck` does.
    """
    header_size = 3
    prefix = 'ADC'

    def __init__(self, deck_contents: DeckContents, version: int = SUPPORTED_VERSIONS[-1]) -> None:
        """
        :param deck_contents:       The deck contents.
        :param version:             Version under which to encode, by default the newest version is used.
                                    Must be on of the supported versions for encoding (atm only V2).
        """
        self.version = version
        self.heroes = sorted(deck_contents['heroes'], key=lambda x: x['id'])
        self.cards = sorted(deck_contents['cards'], key=lambda x: x['id'])
        name = deck_contents.get('name', '')[:63]  # name has a hard limit of 63 characters (V2)
        self.name = re.sub('<[^<]+?>', '', name)
        self.binary = bytearray()  # This where all our hard work will end in, before being interpreted as string

    @property
    def deck_code(self) -> str:
        """Returns the deck code for the deck contents provided."""
        # So we don't have to call encode manually every time
        self._encode()
        # Binary to immutable bytes, then base64 encode and decode to unicode
        encoded = b64encode(bytes(self.binary)).decode()
        # Add prefix
        deck_code = f'{self.prefix}{encoded}'
        # url safe (no, base64.urlsafe_b64encode wouldn't do the trick, different replacements in this case)
        deck_code = deck_code.replace('/', '-').replace('=', '_')
        return deck_code

    def _encode(self) -> bytearray:
        """Heavy lifting for the encoding."""
        # First byte is version and number of heroes
        version = (self.version << 4) | _extract_n_bits(len(self.heroes), 3)
        self.binary.append(version)

        # Put placeholder for checksum as second byte
        placeholder_checksum = 0
        checksum_index = len(self.binary)
        self.binary.append(placeholder_checksum)

        # Length of the name string is the 3rd byte
        self.binary.append(len(self.name))
        # Add remaining number of heroes to the next byte if needed (happens with 8+ heroes)
        self._add_remaining_bits_from_number(len(self.heroes), 3)

        # Serialize and append heroes
        previous_card_id = 0
        for hero in self.heroes:
            self._add_card(hero['turn'], hero['id'] - previous_card_id)
            previous_card_id = hero['id']

        # Serialize and append cards
        previous_card_id = 0
        for card in self.cards:
            self._add_card(card['count'], card['id'] - previous_card_id)
            previous_card_id = card['id']

        # Now we'll be adding name of the deck, note down at which index we'll be starting
        name_start_index = len(self.binary)
        # Encode our beautiful unicode string to bytes, then convert to bytearray
        name_bytes = bytearray(self.name.encode())
        # Add the encoded name at the end
        for name_byte in name_bytes:
            self.binary.append(name_byte)

        # Compute the checksum and replace it at the index we previously indexed
        self.binary[checksum_index] = sum(b for b in self.binary[self.header_size:name_start_index]) & 255
        return self.binary

    def _add_remaining_bits_from_number(self, value: int, already_written_bits: int) -> None:
        """Adds the remaining bits from the number we extracted some bits from previously."""
        value >>= already_written_bits
        while value > 0:
            next_byte = _extract_n_bits(value, 7)
            value >>= 7
            self.binary.append(next_byte)

    def _add_card(self, count_or_turn: int, value: int) -> None:
        """Adds a card to the bytearray"""
        # Note down the index we start at
        bytes_start = len(self.binary)
        # max count in the first byte
        first_byte_max_count = 3
        # Whether the count (or count) exceeds the max
        extended_count = ((count_or_turn - 1) >= first_byte_max_count)
        # If up to number 3 was provided as first argument, we us that -1, otherwise we use the maximum - 3
        first_byte_count = first_byte_max_count if extended_count else (count_or_turn - 1)
        # This ends up being either 64, 128 or 192 depending on the count
        first_byte = first_byte_count << 6
        # We bitwise or the number we got with the first 5 bits of the value (card id difference)
        first_byte |= _extract_n_bits(value, 5)
        # And write the first byte into our array
        self.binary.append(first_byte)
        # After the first byte we add the value (difference in card_id from the previous card_id)
        self._add_remaining_bits_from_number(value, 5)
        # If we couldn't fit the count (or turn) into the first byte and we used 3, we need to add it here
        if extended_count:
            self._add_remaining_bits_from_number(count_or_turn, 0)
        count_bytes_end = len(self.binary)
        # If we exceeded 11 bytes, we are doomed, probably api version v3 will be needed by then, no instructions now
        if count_bytes_end - bytes_start > 11:
            raise DeckEncodeException("Something went horribly wrong")


def _extract_n_bits(value: int, num_bits: int) -> int:
    """Extracts n bits from a number"""
    limit_bit = 1 << num_bits
    result = value & (limit_bit - 1)
    if value >= limit_bit:
        result |= limit_bit
    return result
