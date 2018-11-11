class PyArtifactException(Exception):
    pass


class FilterException(PyArtifactException):
    pass


class UnknownFilterArgument(FilterException):
    pass
