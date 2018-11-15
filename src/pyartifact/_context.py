from typing import Any, Dict, List


class Context:
    all_sets = ['00', '01']

    def __init__(self, language: str = 'english') -> None:
        self.language: str = language
        self.cards_by_id: Dict[int, Any] = {}
        self.cards_by_name: Dict[str, Any] = {}
        self.loaded_sets: List[str] = []


ctx = Context()
