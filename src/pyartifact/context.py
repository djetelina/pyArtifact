from typing import Any, Dict


class Context:
    def __init__(self, language: str = 'english') -> None:
        self.language: str = language
        self.cards_by_id: Dict[int, Any] = {}
        self.cards_by_name: Dict[str, Any] = {}


ctx = Context()
