"""
Funciones para períodos tributarios (AAAAMM), fechas y nombres de meses.

Un período es un entero con el año y el mes (``202611``). Las fechas se
reciben y entregan como texto ``AAAA-MM-DD``.
"""

from datetime import UTC, date, datetime, timedelta

# largo de un período mensual (AAAAMM) y de uno anual (AAAA)
_LARGO_PERIODO_MENSUAL = 6
_LARGO_PERIODO_ANUAL = 4
# mes que queda al restar o sumar un mes sin ajustar el año
_MES_ANTERIOR_A_ENERO = 0
_MES_SIGUIENTE_A_DICIEMBRE = 13
# meses del año
_MESES = 12
# partes de una fecha y hora con minutos ("31/12/2026 10:30")
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
    Entrega la fecha de hoy según la zona horaria local del sistema.

    :return: Fecha de hoy.
    :rtype: date
    """
    return datetime.now().astimezone().date()


def period_current() -> int:
    """
    Entrega el período (AAAAMM) actual.

    :return: Período actual.
    :rtype: int
    """
    return int(_hoy().strftime('%Y%m'))


def period_previous(period: int | None = None) -> int:
    """
    Entrega el período anterior al indicado.

    :param period: Período (AAAAMM). Si no se indica se usa el actual.
    :return: Período anterior; de enero pasa a diciembre del año anterior.
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
    Entrega el período siguiente al indicado.

    :param period: Período (AAAAMM). Si no se indica se usa el actual.
    :return: Período siguiente; de diciembre pasa a enero del año siguiente.
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
    Entrega los períodos entre dos períodos, ambos incluidos.

    :param period_from: Primer período (AAAAMM).
    :param period_to: Último período. Si no se indica se usa el actual.
    :return: Períodos en orden; vacío si el primero es mayor al último.
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
    Entrega el primer día de un período.

    :param period: Período (AAAAMM).
    :return: Fecha ``AAAA-MM-01``.
    :rtype: str
    """
    return str(period)[0:4] + '-' + str(period)[4:] + '-01'


def period_last_day(period: int) -> str:
    """
    Entrega el último día de un período.

    :param period: Período (AAAAMM).
    :return: Fecha ``AAAA-MM-DD`` del último día del mes.
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
    Indica si un período (AAAAMM) o un año (AAAA) es válido.

    :param period: Período o año, como número o texto.
    :param year_from: Primer año aceptado.
    :param year_to: Último año aceptado.
    :return: True si es un número de 4 o 6 dígitos con año (y mes) válidos.
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
    Cambia el formato de una fecha (por defecto, de DD/MM/AAAA a AAAA-MM-DD).

    Sin formatos, se reconocen ``DD/MM/AAAA``, ``DD/MM/AAAA HH:MM`` y
    ``DD/MM/AAAA HH:MM:SS``, y se entregan como ``AAAA-MM-DD``,
    ``AAAA-MM-DD HH:MM`` y ``AAAA-MM-DD HH:MM:SS``.

    :param date: Fecha en texto.
    :param format_from: Formato de entrada (``strptime``).
    :param format_to: Formato de salida (``strftime``).
    :return: Fecha con el formato de salida.
    :rtype: str
    :raises ValueError: Si la fecha no tiene el formato de entrada.
    :raises TypeError: Si se indica ``format_from`` pero no ``format_to``.
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
    # la zona horaria (UTC) sólo evita una fecha ingenua: no cambia el texto
    # de salida mientras format_to no pida la zona (%z o %Z)
    date_obj = datetime.strptime(date, format_from).replace(tzinfo=UTC)
    if format_to is None:
        # con format_from y sin format_to: igual que datetime.strftime(None)
        msg = 'strftime() argument 1 must be str, not None'
        raise TypeError(msg)
    return date_obj.strftime(format_to)


def date_add_days(days: int, from_date: str | None = None) -> str:
    """
    Suma (o resta) días a una fecha.

    :param days: Días que se suman; si es negativo, se restan.
    :param from_date: Fecha ``AAAA-MM-DD``. Si no se indica se usa hoy.
    :return: Fecha resultante ``AAAA-MM-DD``.
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
    Cuenta los días entre dos fechas, sin importar el orden.

    Se usa sólo la parte de la fecha (``AAAA-MM-DD``); la hora se ignora.

    :param date_from: Fecha (o fecha y hora) de inicio.
    :param date_to: Fecha (o fecha y hora) de término. Si no se indica se usa
        hoy.
    :return: Días entre ambas fechas, siempre positivo o cero.
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
    Entrega el número del mes (``01`` a ``12``) a partir de su nombre.

    :param month: Nombre del mes en español, sin importar mayúsculas.
    :return: Número del mes con dos dígitos, o el texto recibido si no es un
        nombre de mes.
    :rtype: str
    """
    month_lower = month.lower()
    if month_lower in _NOMBRES_MESES:
        return f'{_NOMBRES_MESES.index(month_lower) + 1:02d}'
    return month


def month_from_index(index: int | str) -> str:
    """
    Entrega el nombre del mes a partir de su índice (0 es enero).

    :param index: Índice del mes; se usa el resto de la división por 12.
    :return: Nombre del mes en español y en minúsculas.
    :rtype: str
    """
    return _NOMBRES_MESES[int(index) % _MESES]


def month_from_number(month: int | str) -> str:
    """
    Entrega el nombre del mes a partir de su número (1 es enero).

    :param month: Número del mes.
    :return: Nombre del mes en español y en minúsculas.
    :rtype: str
    """
    return month_from_index(int(month) - 1)
