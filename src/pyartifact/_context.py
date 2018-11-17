from collections import defaultdict
from typing import Any, Dict, List, DefaultDict


class Context:
    all_sets = ['00', '01']

    def __init__(self, language: str = 'english') -> None:
        self.language: str = language
        self.cards_by_id: Dict[int, Any] = {}
        self.cards_by_name: DefaultDict[List[Any]] = defaultdict(list)
        self.loaded_sets: List[str] = []

    def __repr__(self):
        return f'<Context: {self.__dict__}>'


ctx = Context()
