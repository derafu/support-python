"""Recursive merge of dictionaries."""

from typing import TypeIs


def _es_diccionario(valor: object) -> TypeIs[dict[object, object]]:
    """
    Tell whether a value is a dictionary.

    :param valor: Value to check.
    :return: True if it is a ``dict``.
    :rtype: bool
    """
    return isinstance(valor, dict)


def merge[K, V](
    dictionary_a: dict[K, V],
    dictionary_b: dict[K, V],
    path: list[str] | None = None,
) -> dict[K, V]:
    """
    Merge ``dictionary_b`` into ``dictionary_a``.

    The keys of ``dictionary_b`` are added to ``dictionary_a``. If a key is
    in both and both values are dictionaries, they are merged the same way;
    otherwise, the value of ``dictionary_b`` wins (lists are replaced, not
    joined).

    :param dictionary_a: Dictionary that is modified.
    :param dictionary_b: Dictionary with the values to add.
    :param path: Keys walked down to this level (internal use).
    :return: The modified ``dictionary_a``.
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
