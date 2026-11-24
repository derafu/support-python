"""Funciones de codificación de datos."""

import base64
import re


def base64_decode(data: bytes, altchars: bytes = b'+/') -> bytes:
    """
    Decodifica datos en base64, con el relleno (``=``) opcional.

    Antes de decodificar se quitan los caracteres que no son de base64 (por
    ejemplo, saltos de línea) y se completa el relleno que falte.
    Basado en https://stackoverflow.com/a/9807138.

    :param data: Datos en base64 (texto ASCII en bytes).
    :param altchars: Los dos caracteres usados en lugar de ``+`` y ``/``.
    :return: Datos decodificados.
    :rtype: bytes
    """
    data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'=' * (4 - missing_padding)
    return base64.b64decode(data, altchars)
