import pytest

from pyartifact import Cards


@pytest.fixture
def cards():
    c = Cards()
    c.load_all_sets()
    return c
