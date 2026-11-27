"""Check for "empty" values using rules per data type."""

from collections.abc import Mapping
from typing import TypeIs


class TipoNoSoportadoError(AttributeError):
    """
    Data type that ``is_empty()`` cannot check.

    It inherits from ``AttributeError``, the exception previously raised in
    this case, so as not to break code that already catches it.
    """

    def __init__(self, tipo: type) -> None:
        """
        Create the error with the unsupported type.

        :param tipo: Type of the value received.
        """
        super().__init__(
            'Tipo de dato no soportado por is_empty(): ' + str(tipo)
        )


class NoIndexableError(TypeError):
    """
    A value along the ``key`` path is not a dictionary.

    It is the ``TypeError`` previously raised when looking up the key in
    that value.
    """

    def __init__(self, tipo: type) -> None:
        """
        Create the error with the type of the value.

        :param tipo: Type of the value that is not a dictionary.
        """
        super().__init__(
            f"'{tipo.__name__}' no se puede indexar con una llave"
        )


def _es_mapeo(valor: object) -> TypeIs[Mapping[object, object]]:
    """
    Tell whether a value is a dictionary.

    :param valor: Value to check.
    :return: True if it is a ``dict``.
    :rtype: bool
    """
    return isinstance(valor, dict)


def _es_coleccion(
    valor: object,
) -> TypeIs[list[object] | tuple[object, ...] | set[object]]:
    """
    Tell whether a value is a list, a tuple or a set.

    :param valor: Value to check.
    :return: True if it is a ``list``, ``tuple`` or ``set``.
    :rtype: bool
    """
    return isinstance(valor, list | tuple | set)


def _is_empty_dict(var: Mapping[object, object], key: str | None) -> bool:
    """
    Tell whether a dictionary, or the value of one of its keys, is empty.

    :param var: Dictionary to check.
    :param key: Key (or ``a.b.c`` path) to check; if None, it checks that
        the dictionary has keys.
    :return: True if it is empty, or if the key does not exist or its value
        is empty.
    :rtype: bool
    """
    # without a specific key, check that the dictionary has something
    if key is None:
        return len(var) == 0
    # look up the final value of the variable following the given key
    valor: object = var
    for k in key.split('.'):
        if not _es_mapeo(valor):
            # in a list, tuple, set or string without the key, the key does
            # not exist; otherwise the key cannot be looked up
            if (_es_coleccion(valor) or isinstance(valor, str)) and (
                k not in valor
            ):
                return True
            raise NoIndexableError(type(valor))
        if k not in valor:
            return True
        valor = valor[k]
    # the key exists in the dictionary: check whether its value is non-empty
    return is_empty(valor)


def is_empty(var: object, key: str | None = None) -> bool:
    """
    Tell whether a variable is "empty", with rules based on its type.

    - ``None``: always empty.
    - Dictionaries: no keys; or, if ``key`` is given, the key does not exist
      or its value is empty. ``key`` can be a path (``a.b.c``).
    - Lists, tuples and sets: length 0.
    - Strings: ``''``, ``'0'`` or ``'0.0'``.
    - Integers and floats: 0. ``False`` counts as 0 (``bool`` is an
      ``int``).

    :param var: Variable to check.
    :param key: Key (or path of keys) to check if ``var`` is a dictionary.
    :return: True if the variable is empty according to the rules above.
    :rtype: bool
    :raises TipoNoSoportadoError: If the type of ``var`` is not one of the
        above.
    :raises NoIndexableError: If the ``key`` path goes through a value that
        is not a dictionary and the key cannot be looked up in it.
    """
    # if the variable is None the rest is not checked because it is empty
    if var is None:
        return True
    # dictionaries
    if _es_mapeo(var):
        return _is_empty_dict(var, key)
    # lists, tuples and sets
    if _es_coleccion(var):
        return len(var) == 0
    # strings
    if isinstance(var, str):
        return var in {'0', '0.0', ''}
    # integers (including bool) and floats
    if isinstance(var, int | float):
        return var == 0
    # data type not supported for the emptiness check
    raise TipoNoSoportadoError(type(var))
