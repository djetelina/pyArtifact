from typing import NamedTuple

import pytest

from pyartifact import Cards


@pytest.fixture(scope='package')
def cards():
    c = Cards()
    c.load_all_sets()
    return c


deck_codes = [
    dict(
        name='Blue/Red Example',
        string='ADCJQUQI30zuwEYg2ABeF1Bu94BmWIBTEkLtAKlAZakAYmHh0JsdWUvUmVkIEV4YW1wbGU_',
        version=2
    ),
    dict(
        name='Green/Black Example',
        string='ADCJWkTZX05uwGDCRV4XQGy3QGLmqUBg4GQJgGLGgO7AaABR3JlZW4vQmxhY2sgRXhhbXBsZQ__',
        version=2
    ),
    dict(
        name='',
        string='ADCFWllfTm7AYMJFXhdAbLdAYuapQGDgZAmAYsaA7sBoAE_',
        version=1
    )
]


@pytest.fixture(params=deck_codes)
def deck_code(request):
    yield request.param


class FindFoundPair(NamedTuple):
    find: str
    found: str


find_names = [
    FindFoundPair('strom spirit', 'Storm Spirit'),
    FindFoundPair('anihilation', 'Annihilation'),
    FindFoundPair('anihliation', 'Annihilation'),
    FindFoundPair('Centaur warrior', 'Centaur Warrunner'),
    FindFoundPair('Gang', 'Gank'),
    FindFoundPair('Gank', 'Gank'),
    FindFoundPair('And one for me', '...And One For Me'),
    FindFoundPair('Annih', 'Annihilation'),
    FindFoundPair('Bounty', 'Bounty Hunter'),
    FindFoundPair('Drow', 'Drow Ranger'),
    FindFoundPair('Farvhan', 'Farvhan the Dreamer'),
    FindFoundPair('Favrhan', 'Farvhan the Dreamer'),
    FindFoundPair('Dominator', 'Helm of the Dominator'),
    FindFoundPair('Wrathofgold ', 'Wrath of Gold'),
    FindFoundPair('Gold Wrath', 'Wrath of Gold'),
    FindFoundPair('Vesture', 'Vesture of the Tyrant'),
    FindFoundPair('Poisoned Strike', 'Poised to Strike'),
    FindFoundPair('Lajtnin Strike', 'Lightning Strike')
]


@pytest.fixture(params=find_names)
def find_name(request):
    yield request.param
