"""
Functions for tax periods (YYYYMM), dates and month names.

A period is an integer with the year and month (``202611``). Dates are
received and returned as ``YYYY-MM-DD`` strings.
"""

from datetime import UTC, date, datetime, timedelta

# length of a monthly period (YYYYMM) and of a yearly one (YYYY)
_LARGO_PERIODO_MENSUAL = 6
_LARGO_PERIODO_ANUAL = 4
# month left after subtracting or adding a month without adjusting the year
_MES_ANTERIOR_A_ENERO = 0
_MES_SIGUIENTE_A_DICIEMBRE = 13
# months in a year
_MESES = 12
# parts of a date and time with minutes ("31/12/2026 10:30")
_PARTES_FECHA_HORA = 2
_LARGO_HORA_MINUTOS = 5

_NOMBRES_MESES = (
    'enero',
    'febrero',
    'marzo',
    'abril',
    'mayo',
    'junio',
    'julio',
    'agosto',
    'septiembre',
    'octubre',
    'noviembre',
    'diciembre',
)


def _hoy() -> date:
    """
    Return today's date in the system's local time zone.

    :return: Today's date.
    :rtype: date
    """
    return datetime.now().astimezone().date()


def period_current() -> int:
    """
    Return the current period (YYYYMM).

    :return: Current period.
    :rtype: int
    """
    return int(_hoy().strftime('%Y%m'))


def period_previous(period: int | None = None) -> int:
    """
    Return the period before the given one.

    :param period: Period (YYYYMM). If not given, the current one is used.
    :return: Previous period; January goes to December of the previous year.
    :rtype: int
    """
    if period is None:
        period = period_current()
    previous_period = period - 1
    if (
        len(str(period)) == _LARGO_PERIODO_MENSUAL
        and int(str(previous_period)[4:]) == _MES_ANTERIOR_A_ENERO
    ):
        previous_period = previous_period - 100 + _MESES
    return previous_period


def period_next(period: int | None = None) -> int:
    """
    Return the period after the given one.

    :param period: Period (YYYYMM). If not given, the current one is used.
    :return: Next period; December goes to January of the next year.
    :rtype: int
    """
    if period is None:
        period = period_current()
    next_period = period + 1
    if (
        len(str(period)) == _LARGO_PERIODO_MENSUAL
        and int(str(next_period)[4:]) == _MES_SIGUIENTE_A_DICIEMBRE
    ):
        next_period = next_period + 100 - _MESES
    return next_period


def period_range(period_from: int, period_to: int | None = None) -> list[int]:
    """
    Return the periods between two periods, both included.

    :param period_from: First period (YYYYMM).
    :param period_to: Last period. If not given, the current one is used.
    :return: Periods in order; empty if the first is after the last.
    :rtype: list[int]
    """
    if period_to is None:
        period_to = period_current()
    periods: list[int] = []
    period = period_from
    while period <= period_to:
        periods.append(period)
        period = period_next(period)
    return periods


def period_first_day(period: int) -> str:
    """
    Return the first day of a period.

    :param period: Period (YYYYMM).
    :return: Date ``YYYY-MM-01``.
    :rtype: str
    """
    return str(period)[0:4] + '-' + str(period)[4:] + '-01'


def period_last_day(period: int) -> str:
    """
    Return the last day of a period.

    :param period: Period (YYYYMM).
    :return: Date ``YYYY-MM-DD`` of the last day of the month.
    :rtype: str
    """
    first_day_next_period = date.fromisoformat(
        period_first_day(period_next(period))
    )
    return (first_day_next_period - timedelta(days=1)).isoformat()


def period_valid(
    period: int | str, year_from: int = 2000, year_to: int = 2100
) -> bool:
    """
    Tell whether a period (YYYYMM) or a year (YYYY) is valid.

    :param period: Period or year, as a number or a string.
    :param year_from: First accepted year.
    :param year_to: Last accepted year.
    :return: True if it is a 4 or 6 digit number with a valid year (and
        month).
    :rtype: bool
    """
    try:
        int(period)
    except ValueError:
        return False
    period = str(period)
    n_period = len(period)
    if n_period == _LARGO_PERIODO_ANUAL:
        return year_from <= int(period) <= year_to
    if n_period == _LARGO_PERIODO_MENSUAL:
        year = int(period[0:4])
        month = int(period[4:])
        return year_from <= year <= year_to and 1 <= month <= _MESES
    return False


def date_normalize(
    date: str, format_from: str | None = None, format_to: str | None = None
) -> str:
    """
    Change the format of a date (by default, from DD/MM/YYYY to YYYY-MM-DD).

    Without formats, ``DD/MM/YYYY``, ``DD/MM/YYYY HH:MM`` and
    ``DD/MM/YYYY HH:MM:SS`` are recognized, and returned as ``YYYY-MM-DD``,
    ``YYYY-MM-DD HH:MM`` and ``YYYY-MM-DD HH:MM:SS``.

    :param date: Date as a string.
    :param format_from: Input format (``strptime``).
    :param format_to: Output format (``strftime``).
    :return: Date in the output format.
    :rtype: str
    :raises ValueError: If the date does not match the input format.
    :raises TypeError: If ``format_from`` is given but ``format_to`` is not.
    """
    if format_from is None:
        aux = date.split(' ')
        if len(aux) == _PARTES_FECHA_HORA:
            if len(aux[1]) == _LARGO_HORA_MINUTOS:
                format_from = '%d/%m/%Y %H:%M'
                format_to = '%Y-%m-%d %H:%M'
            else:
                format_from = '%d/%m/%Y %H:%M:%S'
                format_to = '%Y-%m-%d %H:%M:%S'
        else:
            format_from = '%d/%m/%Y'
            format_to = '%Y-%m-%d'
    # the time zone (UTC) only avoids a naive datetime: it does not change
    # the output text unless format_to asks for the zone (%z or %Z)
    date_obj = datetime.strptime(date, format_from).replace(tzinfo=UTC)
    if format_to is None:
        # format_from without format_to: same as datetime.strftime(None)
        msg = 'strftime() argument 1 must be str, not None'
        raise TypeError(msg)
    return date_obj.strftime(format_to)


def date_add_days(days: int, from_date: str | None = None) -> str:
    """
    Add (or subtract) days to a date.

    :param days: Days to add; if negative, they are subtracted.
    :param from_date: Date ``YYYY-MM-DD``. If not given, today is used.
    :return: Resulting date ``YYYY-MM-DD``.
    :rtype: str
    """
    if from_date is None:
        from_date = _hoy().strftime('%Y-%m-%d')
    y, m, d = from_date.split('-')
    return str(date(int(y), int(m), int(d)) + timedelta(days=days))


def date_count_days(
    date_from: str | date, date_to: str | date | None = None
) -> int:
    """
    Count the days between two dates, regardless of their order.

    Only the date part (``YYYY-MM-DD``) is used; the time is ignored.

    :param date_from: Start date (or date and time).
    :param date_to: End date (or date and time). If not given, today is
        used.
    :return: Days between both dates, always positive or zero.
    :rtype: int
    """
    if date_to is None:
        date_to = _hoy().strftime('%Y-%m-%d')
    y_from, m_from, d_from = str(date_from).split(' ')[0].split('-')
    y_to, m_to, d_to = str(date_to).split(' ')[0].split('-')
    delta = date(int(y_to), int(m_to), int(d_to)) - date(
        int(y_from), int(m_from), int(d_from)
    )
    return abs(delta.days)


def month_from_string(month: str) -> str:
    """
    Return the month number (``01`` to ``12``) from its name.

    :param month: Month name in Spanish, case-insensitive.
    :return: Two-digit month number, or the given text if it is not a month
        name.
    :rtype: str
    """
    month_lower = month.lower()
    if month_lower in _NOMBRES_MESES:
        return f'{_NOMBRES_MESES.index(month_lower) + 1:02d}'
    return month


def month_from_index(index: int | str) -> str:
    """
    Return the month name from its index (0 is January).

    :param index: Month index; the remainder of dividing by 12 is used.
    :return: Month name in Spanish and in lower case.
    :rtype: str
    """
    return _NOMBRES_MESES[int(index) % _MESES]


def month_from_number(month: int | str) -> str:
    """
    Return the month name from its number (1 is January).

    :param month: Month number.
    :return: Month name in Spanish and in lower case.
    :rtype: str
    """
    return month_from_index(int(month) - 1)
