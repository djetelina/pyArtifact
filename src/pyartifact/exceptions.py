class PyArtifactException(Exception):
    pass


class FilterException(PyArtifactException):
    pass


class UnknownFilterArgument(FilterException):
    pass


class InvalidDeck(PyArtifactException):
    pass


class InvalidDeckString(InvalidDeck):
    pass


class DeckDecodeException(PyArtifactException):
    pass


class DeckEncodeException(PyArtifactException):
    pass
