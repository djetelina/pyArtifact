import pytest

from pyartifact import Cards


@pytest.fixture()
def cards():
    c = Cards()
    c.load_all_sets()
    return c


deck_codes = [
    dict(
        name='Blue/Red Example',
        string='ADCJQUQI30zuwEYg2ABeF1Bu94BmWIBTEkLtAKlAZakAYmHh0JsdWUvUmVkIEV4YW1wbGU_'
    ),
    dict(
        name='Green/Black Example',
        string='ADCJWkTZX05uwGDCRV4XQGy3QGLmqUBg4GQJgGLGgO7AaABR3JlZW4vQmxhY2sgRXhhbXBsZQ__'
    )
]


@pytest.fixture(params=deck_codes)
def deck_code(request):
    yield request.param
