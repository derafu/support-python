"""Formato de números según el idioma (separadores de miles y decimales)."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from babel.core import UnknownLocaleError
from babel.numbers import format_decimal

# decimales cuando se pide formato con decimales (decimal_digits=True)
_DECIMALES_POR_DEFECTO = 2


def format_number(
    value: object, decimal_digits: object = None, locale: str = 'es_CL'
) -> str:
    """
    Formatea un número con los separadores de miles y decimales del idioma.

    El número se redondea "hacia arriba desde la mitad" (``ROUND_HALF_UP``)
    a la cantidad de decimales indicada.

    :param value: Número (o texto con un número) a formatear. ``None`` se
        muestra como ``0``.
    :param decimal_digits: Cantidad de decimales (entero); ``None`` o
        ``False`` es 0 y ``True`` es 2.
    :param locale: Idioma, por ejemplo ``es_CL`` o ``es-CL``.
    :return: Número formateado. Si el valor no es un número, la cantidad de
        decimales no es un entero o es negativa, o el idioma no existe, se
        entrega el valor sin formatear.
    :rtype: str
    """
    if value is None:
        return '0'
    try:
        numero = Decimal(str(value))
    except TypeError, ValueError, InvalidOperation:
        return str(value)
    if decimal_digits is None:
        decimal_digits = 0
    elif decimal_digits is True:
        decimal_digits = _DECIMALES_POR_DEFECTO
    if not isinstance(decimal_digits, int) or decimal_digits < 0:
        return str(numero)
    # Babel usa "_" para separar idioma y país
    locale = locale.replace('-', '_')
    try:
        # redondear el valor con Decimal
        numero = numero.quantize(
            Decimal('1.' + '0' * decimal_digits), rounding=ROUND_HALF_UP
        )
        format_pattern = '#,##0' + (
            '.' + '0' * decimal_digits if decimal_digits > 0 else ''
        )
        return format_decimal(numero, format=format_pattern, locale=locale)
    except InvalidOperation, ValueError, UnknownLocaleError:
        # error en el formateo: se entrega el valor sin formatear
        return str(numero)
