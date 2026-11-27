"""Tests for ``encoding``, ``gravatar``, ``number_format`` and ``log``."""

import base64

import pytest

from derafu_support.encoding import base64_decode
from derafu_support.gravatar import email_md5, gravatar_url
from derafu_support.log import LogMessage, MemoryLogging
from derafu_support.number_format import format_number

# messages logged by _registrar(), one per level
MENSAJES_POR_NIVEL = 5
# level that is not a standard one
NIVEL_NO_ESTANDAR = 15


def test_base64_sin_relleno_y_con_saltos() -> None:
    """It decodes even with missing padding and line breaks."""
    codificado = base64.b64encode(b'hola mundo!').rstrip(b'=')
    assert base64_decode(codificado[:4] + b'\n' + codificado[4:]) == (
        b'hola mundo!'
    )


def test_gravatar() -> None:
    """The MD5 of the email address builds the Gravatar URL."""
    assert email_md5('a@b.cl') == '9912467c575f5763cc6be100baf86037'
    assert gravatar_url('a@b.cl') == (
        'https://gravatar.com/avatar/9912467c575f5763cc6be100baf86037'
    )


@pytest.mark.parametrize(
    ('valor', 'decimales', 'idioma', 'esperado'),
    [
        (1234567.891, None, 'es-cl', '1.234.568'),
        (1234567.891, True, 'es_CL', '1.234.567,89'),
        ('1234.5', 1, 'en-us', '1,234.5'),
        (2.5, 0, 'es_CL', '3'),
        (None, 2, 'es_CL', '0'),
        ('abc', 2, 'es_CL', 'abc'),
        (1.5, -1, 'es_CL', '1.5'),
        (1.5, '2', 'es_CL', '1.5'),
        (1.5, 2, 'xx_YY', '1.50'),
        (float('inf'), 2, 'es_CL', 'Infinity'),
    ],
)
def test_format_number(
    valor: object, decimales: object, idioma: str, esperado: str
) -> None:
    """Formatting with locale separators, and unformatted cases."""
    assert format_number(valor, decimales, idioma) == esperado


def _registrar(log: MemoryLogging) -> None:
    """Log one message per level (function that calls the log)."""
    log.debug('d')
    log.info('i', args={'x': 1}, data=[1])
    log.warning('w', category='otra')
    log.error('e')
    log.critical('c')


def test_log_en_memoria() -> None:
    """Keeps messages from the given level and records the caller."""
    log = MemoryLogging(category='cat')
    _registrar(log)
    mensajes = log.get_all()
    assert [m.level_name for m in mensajes] == [
        'INFO',
        'WARNING',
        'ERROR',
        'CRITICAL',
    ]
    assert {m.function_name for m in mensajes} == {'_registrar'}
    assert {m.module for m in mensajes} == {__name__}
    assert [m.category for m in mensajes] == ['cat', 'otra', 'cat', 'cat']
    assert log.get_all(as_dict=True)[0]['args'] == {'x': 1}
    assert str(mensajes[0]).endswith(
        f'cat INFO: i [{__name__}:{mensajes[0].line_number}]'
    )
    assert log.flush(as_dict=True)[0]['message'] == 'i'
    assert log.flush() == []


def test_log_nivel_debug() -> None:
    """With DEBUG level all messages are kept."""
    log = MemoryLogging(MemoryLogging.DEBUG)
    _registrar(log)
    assert len(log.flush()) == MENSAJES_POR_NIVEL


def test_log_message_directo() -> None:
    """A message created directly uses the ``general`` category."""
    mensaje = LogMessage(MemoryLogging.WARNING, 'm', caller_level=-2)
    assert mensaje.category == 'general'
    assert mensaje.to_dict()['level_name'] == 'WARNING'
    with pytest.raises(KeyError):
        _ = LogMessage(NIVEL_NO_ESTANDAR, 'm').level_name
