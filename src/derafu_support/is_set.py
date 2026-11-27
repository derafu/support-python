"""Check for keys (or key paths) defined in a dictionary."""

from collections.abc import Mapping
from typing import TypeIs


class IsSetArgumentoError(AttributeError):
    """
    Invalid argument for ``is_set()``.

    It inherits from ``AttributeError``, the exception previously raised in
    these cases, so as not to break code that already catches it.
    """


class SinDiccionarioError(IsSetArgumentoError):
    """No dictionary was given to ``is_set()``."""

    def __init__(self) -> None:
        """Create the error with its message."""
        super().__init__('No se especificó un diccionario')


class SinLlavesError(IsSetArgumentoError):
    """No keys were given to ``is_set()``."""

    def __init__(self) -> None:
        """Create the error with its message."""
        super().__init__(
            'Se espera que se especifiquen las llaves del diccionario'
        )


class NoIndexableError(TypeError):
    """
    An intermediate value of the path cannot be indexed with a key.

    It is the ``TypeError`` previously raised when indexing, for example, a
    string or a number.
    """

    def __init__(self, tipo: type) -> None:
        """
        Create the error with the type of the value.

        :param tipo: Type of the value that cannot be indexed.
        """
        super().__init__(
            f"'{tipo.__name__}' no se puede indexar con una llave"
        )


def _es_dict(valor: object) -> TypeIs[dict[object, object]]:
    """
    Tell whether a value is a ``dict``.

    :param valor: Value to check.
    :return: True if it is a ``dict``.
    :rtype: bool
    """
    return isinstance(valor, dict)


def _es_mapeo(valor: object) -> TypeIs[Mapping[object, object]]:
    """
    Tell whether a value is a dictionary (or a mapping).

    :param valor: Value to check.
    :return: True if it is a ``Mapping``.
    :rtype: bool
    """
    return isinstance(valor, Mapping)


def is_set(var: object, keys: str | None = None) -> bool:
    """
    Tell whether a key (or ``a.b.c`` path) exists and is not ``None``.

    :param var: Dictionary to search.
    :param keys: Key, or path of keys separated by dots.
    :return: True if the whole path exists and its value is not ``None``.
    :rtype: bool
    :raises SinDiccionarioError: If ``var`` is not a dictionary.
    :raises SinLlavesError: If no keys are given.
    :raises NoIndexableError: If an intermediate value of the path is not a
        dictionary (for example, a string or a number).
    """
    if not _es_dict(var):
        raise SinDiccionarioError
    if keys is None:
        raise SinLlavesError
    var_search: object = var
    for key in keys.split('.'):
        if not _es_mapeo(var_search):
            raise NoIndexableError(type(var_search))
        try:
            var_search = var_search[key]
        except KeyError:
            return False
        if var_search is None:
            return False
    return True
