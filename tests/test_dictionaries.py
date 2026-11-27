"""Tests for ``is_empty``, ``is_set``, ``dictionary_merge`` and files."""

from pathlib import Path

import pytest

from derafu_support.dictionary_file_operations import (
    dict_load_from_csv,
    dict_save_to_csv,
    dict_save_to_json,
)
from derafu_support.dictionary_merge import merge
from derafu_support.is_empty import (
    NoIndexableError,
    TipoNoSoportadoError,
    is_empty,
)
from derafu_support.is_set import (
    SinDiccionarioError,
    SinLlavesError,
    is_set,
)

VACIOS: list[object] = [None, '', '0', '0.0', 0, 0.0, False, {}, [], (), set()]
NO_VACIOS: list[object] = [
    '1',
    'texto',
    1,
    1.1,
    True,
    {'a': 1},
    [1],
    (1,),
    {1},
]


@pytest.mark.parametrize('valor', VACIOS)
def test_vacios(valor: object) -> None:
    """Empty values according to their type."""
    assert is_empty(valor) is True


@pytest.mark.parametrize('valor', NO_VACIOS)
def test_no_vacios(valor: object) -> None:
    """Non-empty values according to their type."""
    assert is_empty(valor) is False


@pytest.mark.parametrize(
    ('datos', 'llave', 'vacio'),
    [
        ({'a': {'b': 0}}, 'a.b', True),
        ({'a': {'b': 1}}, 'a.b', False),
        ({'a': {'b': {'c': None}}}, 'a.b.c', True),
        ({'a': {'b': {'c': 'valor'}}}, 'a.b.c', False),
        ({'a': {'b': 1}}, 'a.c', True),
        ({'a': {}}, 'a.b', True),
        ({'a': 'xyz'}, 'a.b', True),
    ],
)
def test_vacios_con_llave(
    datos: dict[str, object], llave: str, vacio: bool
) -> None:
    """Key paths in nested dictionaries."""
    assert is_empty(datos, llave) is vacio


def test_vacio_errores() -> None:
    """Unsupported types and paths that cannot be walked."""
    with pytest.raises(TipoNoSoportadoError):
        is_empty(object())
    with pytest.raises(AttributeError):
        is_empty(b'')
    with pytest.raises(NoIndexableError):
        is_empty({'a': None}, 'a.b')
    with pytest.raises(TypeError):
        is_empty({'a': 'b'}, 'a.b')


def test_is_set() -> None:
    """Defined, missing and None paths."""
    datos: dict[str, object] = {'a': {'b': 1, 'c': None}}
    assert is_set(datos, 'a.b') is True
    assert is_set(datos, 'a.c') is False
    assert is_set(datos, 'a.x') is False
    with pytest.raises(SinDiccionarioError):
        is_set([], 'a')
    with pytest.raises(SinLlavesError):
        is_set(datos)
    with pytest.raises(TypeError):
        is_set({'a': 'texto'}, 'a.b')


def test_merge() -> None:
    """Merges recursively and the second dictionary wins."""
    a: dict[str, object] = {
        'otro': 1,
        'mas': {},
        'tipo': {'casa1': 1, 'casa': ['1', '2']},
    }
    b: dict[str, object] = {'tipo': {'casa': ['3', '4']}, 'nuevo': True}
    resultado = merge(a, b)
    assert resultado is a
    assert a == {
        'otro': 1,
        'mas': {},
        'tipo': {'casa1': 1, 'casa': ['3', '4']},
        'nuevo': True,
    }


def test_json(tmp_path: Path) -> None:
    """Saves data as indented JSON."""
    ruta = tmp_path / 'datos.json'
    dict_save_to_json(ruta, {'b': 1, 'a': [1, 2]}, sort_keys=True, indent=1)
    assert ruta.read_text(encoding='utf-8') == (
        '{\n "a": [\n  1,\n  2\n ],\n "b": 1\n}'
    )


def test_csv(tmp_path: Path) -> None:
    """Saves and reads CSV; without rows the file is left empty."""
    ruta = tmp_path / 'datos.csv'
    filas = [{'a': 'ñ', 'b': 1}, {'a': 'x', 'b': 2}]
    dict_save_to_csv(ruta, filas)
    assert dict_load_from_csv(ruta) == [
        {'a': 'ñ', 'b': '1'},
        {'a': 'x', 'b': '2'},
    ]
    dict_save_to_csv(ruta, [])
    assert not ruta.read_text(encoding='utf-8')
