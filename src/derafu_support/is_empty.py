"""Revisión de valores "vacíos" según reglas por tipo de dato."""

from collections.abc import Mapping
from typing import TypeIs


class TipoNoSoportadoError(AttributeError):
    """
    Tipo de dato que ``is_empty()`` no sabe revisar.

    Hereda de ``AttributeError``, la excepción que se lanzaba antes en este
    caso, para no romper a quien ya la captura.
    """

    def __init__(self, tipo: type) -> None:
        """
        Crea el error con el tipo no soportado.

        :param tipo: Tipo del valor recibido.
        """
        super().__init__(
            'Tipo de dato no soportado por is_empty(): ' + str(tipo)
        )


class NoIndexableError(TypeError):
    """
    Un valor de la ruta de ``key`` no es un diccionario.

    Es el ``TypeError`` que se lanzaba antes al buscar la llave en ese valor.
    """

    def __init__(self, tipo: type) -> None:
        """
        Crea el error con el tipo del valor.

        :param tipo: Tipo del valor que no es diccionario.
        """
        super().__init__(
            f"'{tipo.__name__}' no se puede indexar con una llave"
        )


def _es_mapeo(valor: object) -> TypeIs[Mapping[object, object]]:
    """
    Indica si un valor es un diccionario.

    :param valor: Valor a revisar.
    :return: True si es un ``dict``.
    :rtype: bool
    """
    return isinstance(valor, dict)


def _es_coleccion(
    valor: object,
) -> TypeIs[list[object] | tuple[object, ...] | set[object]]:
    """
    Indica si un valor es una lista, una tupla o un conjunto.

    :param valor: Valor a revisar.
    :return: True si es ``list``, ``tuple`` o ``set``.
    :rtype: bool
    """
    return isinstance(valor, list | tuple | set)


def _is_empty_dict(var: Mapping[object, object], key: str | None) -> bool:
    """
    Indica si un diccionario, o el valor de una de sus llaves, está vacío.

    :param var: Diccionario a revisar.
    :param key: Llave (o ruta ``a.b.c``) a revisar; si es None se revisa que
        el diccionario tenga llaves.
    :return: True si está vacío, o si la llave no existe o su valor está
        vacío.
    :rtype: bool
    """
    # si no hay una llave específica, se revisa que el diccionario tenga algo
    if key is None:
        return len(var) == 0
    # buscar el valor final de la variable según la llave definida
    valor: object = var
    for k in key.split('.'):
        if not _es_mapeo(valor):
            # en una lista, tupla, conjunto o texto sin la llave, la llave no
            # existe; en otro caso no se puede buscar la llave
            if (_es_coleccion(valor) or isinstance(valor, str)) and (
                k not in valor
            ):
                return True
            raise NoIndexableError(type(valor))
        if k not in valor:
            return True
        valor = valor[k]
    # la llave existe en el diccionario: hay que ver si tiene un valor no vacío
    return is_empty(valor)


def is_empty(var: object, key: str | None = None) -> bool:
    """
    Indica si una variable está "vacía", con reglas según su tipo.

    - ``None``: siempre vacía.
    - Diccionarios: sin llaves; o, si se indica ``key``, la llave no existe o
      su valor está vacío. ``key`` puede ser una ruta (``a.b.c``).
    - Listas, tuplas y conjuntos: largo 0.
    - Textos: ``''``, ``'0'`` o ``'0.0'``.
    - Enteros y decimales: 0. ``False`` cuenta como 0 (``bool`` es un
      ``int``).

    :param var: Variable a revisar.
    :param key: Llave (o ruta de llaves) a revisar si ``var`` es un
        diccionario.
    :return: True si la variable está vacía según las reglas anteriores.
    :rtype: bool
    :raises TipoNoSoportadoError: Si el tipo de ``var`` no está entre los
        anteriores.
    :raises NoIndexableError: Si la ruta de ``key`` pasa por un valor que no
        es diccionario y no se puede buscar la llave en él.
    """
    # si la variable es None no se valida el resto porque es vacía
    if var is None:
        return True
    # diccionarios
    if _es_mapeo(var):
        return _is_empty_dict(var, key)
    # listas, tuplas y conjuntos
    if _es_coleccion(var):
        return len(var) == 0
    # textos
    if isinstance(var, str):
        return var in {'0', '0.0', ''}
    # enteros (incluye bool) y decimales
    if isinstance(var, int | float):
        return var == 0
    # tipo de dato no soportado para validar si es vacío
    raise TipoNoSoportadoError(type(var))
