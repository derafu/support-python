"""Tests for ``dates``."""

from datetime import date, datetime

import pytest

from derafu_support import dates

# days between January 1 and March 1, 2026 (31 + 28)
DIAS_ENERO_A_MARZO_2026 = 59


@pytest.mark.parametrize(
    ('periodo', 'anterior', 'siguiente'),
    [
        (202611, 202610, 202612),
        (202601, 202512, 202602),
        (202612, 202611, 202701),
        (2026, 2025, 2027),
    ],
)
def test_periodo_anterior_y_siguiente(
    periodo: int, anterior: int, siguiente: int
) -> None:
    """Periods roll over the year in January and December."""
    assert dates.period_previous(periodo) == anterior
    assert dates.period_next(periodo) == siguiente


def test_periodo_actual() -> None:
    """The current period is today's year and month."""
    hoy = datetime.now().astimezone().date()
    assert dates.period_current() == hoy.year * 100 + hoy.month
    assert dates.period_previous() == dates.period_previous(
        hoy.year * 100 + hoy.month
    )
    assert dates.period_next() == dates.period_next(hoy.year * 100 + hoy.month)


def test_rango_de_periodos() -> None:
    """The range includes both ends and crosses the year."""
    assert dates.period_range(202611, 202602 + 100) == [
        202611,
        202612,
        202701,
        202702,
    ]
    assert dates.period_range(202612, 202611) == []


def test_primer_y_ultimo_dia() -> None:
    """First and last day of the month, including a leap February."""
    assert dates.period_first_day(202402) == '2024-02-01'
    assert dates.period_last_day(202402) == '2024-02-29'
    assert dates.period_last_day(202612) == '2026-12-31'


@pytest.mark.parametrize(
    ('periodo', 'valido'),
    [
        (202611, True),
        ('202612', True),
        (202613, False),
        (2026, True),
        (1999, False),
        ('abc', False),
        (20261, False),
    ],
)
def test_periodo_valido(periodo: int | str, valido: bool) -> None:
    """Only years and periods with year and month in range are valid."""
    assert dates.period_valid(periodo) is valido


@pytest.mark.parametrize(
    ('fecha', 'normalizada'),
    [
        ('31/12/2026', '2026-12-31'),
        ('01/02/2026 10:30', '2026-02-01 10:30'),
        ('01/02/2026 10:30:15', '2026-02-01 10:30:15'),
    ],
)
def test_normalizar_fecha(fecha: str, normalizada: str) -> None:
    """DD/MM/YYYY dates (with or without time) become YYYY-MM-DD."""
    assert dates.date_normalize(fecha) == normalizada


def test_normalizar_fecha_con_formatos() -> None:
    """The input and output formats can be given."""
    assert dates.date_normalize('31/12/2026', '%d/%m/%Y', '%Y%m%d') == (
        '20261231'
    )
    with pytest.raises(TypeError):
        dates.date_normalize('31/12/2026', '%d/%m/%Y')
    with pytest.raises(ValueError, match='does not match'):
        dates.date_normalize('2026-12-31', '%d/%m/%Y')


def test_sumar_y_contar_dias() -> None:
    """Adding days and counting days between dates."""
    assert dates.date_add_days(1, '2024-02-28') == '2024-02-29'
    assert dates.date_add_days(-1, '2026-01-01') == '2025-12-31'
    assert dates.date_count_days('2026-03-01', '2026-01-01') == (
        DIAS_ENERO_A_MARZO_2026
    )
    assert dates.date_count_days(date(2026, 1, 1), '2026-01-02 10:00') == 1
    hoy = datetime.now().astimezone().date()
    assert dates.date_add_days(0) == hoy.isoformat()
    assert dates.date_count_days(hoy.isoformat()) == 0


def test_meses() -> None:
    """Conversion between month name, index and number."""
    assert dates.month_from_string('Marzo') == '03'
    assert dates.month_from_string('otro') == 'otro'
    assert dates.month_from_index(0) == 'enero'
    assert dates.month_from_index(13) == 'febrero'
    assert dates.month_from_number('12') == 'diciembre'
