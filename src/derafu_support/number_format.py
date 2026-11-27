"""Locale-aware number formatting (thousands and decimal separators)."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from babel.core import UnknownLocaleError
from babel.numbers import format_decimal

# decimal places when decimals are requested (decimal_digits=True)
_DECIMALES_POR_DEFECTO = 2


def format_number(
    value: object, decimal_digits: object = None, locale: str = 'es_CL'
) -> str:
    """
    Format a number with the locale's thousands and decimal separators.

    The number is rounded "half up" (``ROUND_HALF_UP``) to the given number
    of decimal places.

    :param value: Number (or string with a number) to format. ``None`` is
        shown as ``0``.
    :param decimal_digits: Number of decimal places (integer); ``None`` or
        ``False`` is 0 and ``True`` is 2.
    :param locale: Locale, for example ``es_CL`` or ``es-CL``.
    :return: Formatted number. If the value is not a number, the number of
        decimal places is not an integer or is negative, or the locale does
        not exist, the value is returned unformatted.
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
    # Babel uses "_" to separate language and country
    locale = locale.replace('-', '_')
    try:
        # round the value with Decimal
        numero = numero.quantize(
            Decimal('1.' + '0' * decimal_digits), rounding=ROUND_HALF_UP
        )
        format_pattern = '#,##0' + (
            '.' + '0' * decimal_digits if decimal_digits > 0 else ''
        )
        return format_decimal(numero, format=format_pattern, locale=locale)
    except InvalidOperation, ValueError, UnknownLocaleError:
        # formatting error: the value is returned unformatted
        return str(numero)
