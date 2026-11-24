"""Revisión de llaves (o rutas de llaves) definidas en un diccionario."""

from collections.abc import Mapping
from typing import TypeIs


class IsSetArgumentoError(AttributeError):
    """
    Argumento inválido para ``is_set()``.

    Hereda de ``AttributeError``, la excepción que se lanzaba antes en estos
    casos, para no romper a quien ya la captura.
    """


class SinDiccionarioError(IsSetArgumentoError):
    """No se entregó un diccionario a ``is_set()``."""

    def __init__(self) -> None:
        """Crea el error con su mensaje."""
        super().__init__('No se especificó un diccionario')


class SinLlavesError(IsSetArgumentoError):
    """No se entregaron las llaves a ``is_set()``."""

    def __init__(self) -> None:
        """Crea el error con su mensaje."""
        super().__init__(
            'Se espera que se especifiquen las llaves del diccionario'
        )


class NoIndexableError(TypeError):
    """
    Un valor intermedio de la ruta no se puede indexar con una llave.

    Es el ``TypeError`` que se lanzaba antes al indexar, por ejemplo, un
    texto o un número.
    """

    def __init__(self, tipo: type) -> None:
        """
        Crea el error con el tipo del valor.

        :param tipo: Tipo del valor que no se puede indexar.
        """
        super().__init__(
            f"'{tipo.__name__}' no se puede indexar con una llave"
        )


def _es_dict(valor: object) -> TypeIs[dict[object, object]]:
    """
    Indica si un valor es un ``dict``.

    :param valor: Valor a revisar.
    :return: True si es un ``dict``.
    :rtype: bool
    """
    return isinstance(valor, dict)


def _es_mapeo(valor: object) -> TypeIs[Mapping[object, object]]:
    """
    Indica si un valor es un diccionario (o un mapeo).

    :param valor: Valor a revisar.
    :return: True si es un ``Mapping``.
    :rtype: bool
    """
    return isinstance(valor, Mapping)


def is_set(var: object, keys: str | None = None) -> bool:
    """
    Indica si una llave (o ruta ``a.b.c``) existe y no es ``None``.

    :param var: Diccionario donde se busca.
    :param keys: Llave o ruta de llaves separadas por punto.
    :return: True si la ruta existe completa y su valor no es ``None``.
    :rtype: bool
    :raises SinDiccionarioError: Si ``var`` no es un diccionario.
    :raises SinLlavesError: Si no se indican las llaves.
    :raises NoIndexableError: Si un valor intermedio de la ruta no es un
        diccionario (por ejemplo, un texto o un número).
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
