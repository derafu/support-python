"""Lectura y escritura de diccionarios en archivos JSON y CSV."""

import csv
import json
from collections.abc import Mapping, Sequence
from os import PathLike
from pathlib import Path

type Ruta = str | PathLike[str]


def dict_save_to_json(
    json_filename: Ruta,
    dict_data: object,
    sort_keys: bool = False,
    indent: int = 4,
) -> None:
    """
    Guarda datos en un archivo JSON.

    :param json_filename: Ruta del archivo (se reemplaza si existe).
    :param dict_data: Datos que se guardan (diccionarios, listas, etc.).
    :param sort_keys: Ordena las llaves de los diccionarios.
    :param indent: Espacios de indentación.
    """
    json_data = json.dumps(dict_data, sort_keys=sort_keys, indent=indent)
    Path(json_filename).write_text(json_data, encoding='utf-8')


def dict_save_to_csv(
    csv_filename: Ruta,
    dict_data: Sequence[Mapping[str, object]],
    delimiter: str = ';',
) -> None:
    """
    Guarda una lista de diccionarios en un archivo CSV.

    Los títulos son las llaves del primer diccionario. Sin datos, el archivo
    queda vacío.

    :param csv_filename: Ruta del archivo (se reemplaza si existe).
    :param dict_data: Filas, una por diccionario.
    :param delimiter: Separador de columnas.
    """
    ruta = Path(csv_filename)
    if len(dict_data) > 0:
        keys = dict_data[0].keys()
        with ruta.open('w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(
                output_file, fieldnames=list(keys), delimiter=delimiter
            )
            dict_writer.writeheader()
            dict_writer.writerows(dict_data)
    else:
        ruta.write_text('', encoding='utf-8')


def dict_load_from_csv(
    csv_filename: Ruta, delimiter: str = ';'
) -> list[dict[str, str]]:
    """
    Lee un archivo CSV como una lista de diccionarios.

    La primera fila son los títulos, que se usan como llaves.

    :param csv_filename: Ruta del archivo.
    :param delimiter: Separador de columnas.
    :return: Filas, una por diccionario.
    :rtype: list[dict[str, str]]
    """
    with Path(csv_filename).open(newline='', encoding='utf-8') as input_file:
        return list(csv.DictReader(input_file, delimiter=delimiter))
