"""Combinación recursiva de diccionarios."""

from typing import TypeIs


def _es_diccionario(valor: object) -> TypeIs[dict[object, object]]:
    """
    Indica si un valor es un diccionario.

    :param valor: Valor a revisar.
    :return: True si es un ``dict``.
    :rtype: bool
    """
    return isinstance(valor, dict)


def merge[K, V](
    dictionary_a: dict[K, V],
    dictionary_b: dict[K, V],
    path: list[str] | None = None,
) -> dict[K, V]:
    """
    Combina ``dictionary_b`` dentro de ``dictionary_a``.

    Las llaves de ``dictionary_b`` se agregan a ``dictionary_a``. Si una
    llave está en ambos y los dos valores son diccionarios, se combinan de la
    misma forma; si no, gana el valor de ``dictionary_b`` (las listas se
    reemplazan, no se juntan).

    :param dictionary_a: Diccionario que se modifica.
    :param dictionary_b: Diccionario con los valores que se agregan.
    :param path: Llaves recorridas hasta este nivel (uso interno).
    :return: ``dictionary_a`` modificado.
    :rtype: dict
    """
    if path is None:
        path = []
    for key, valor_b in dictionary_b.items():
        if key in dictionary_a:
            valor_a = dictionary_a[key]
            if _es_diccionario(valor_a) and _es_diccionario(valor_b):
                merge(valor_a, valor_b, [*path, str(key)])
            elif valor_a != valor_b:
                dictionary_a[key] = valor_b
        else:
            dictionary_a[key] = valor_b
    return dictionary_a
