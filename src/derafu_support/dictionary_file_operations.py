"""Read and write dictionaries from and to JSON and CSV files."""

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
    Save data to a JSON file.

    :param json_filename: File path (replaced if it exists).
    :param dict_data: Data to save (dictionaries, lists, etc.).
    :param sort_keys: Sort the dictionary keys.
    :param indent: Indentation spaces.
    """
    json_data = json.dumps(dict_data, sort_keys=sort_keys, indent=indent)
    Path(json_filename).write_text(json_data, encoding='utf-8')


def dict_save_to_csv(
    csv_filename: Ruta,
    dict_data: Sequence[Mapping[str, object]],
    delimiter: str = ';',
) -> None:
    """
    Save a list of dictionaries to a CSV file.

    The headers are the keys of the first dictionary. Without data, the file
    is left empty.

    :param csv_filename: File path (replaced if it exists).
    :param dict_data: Rows, one per dictionary.
    :param delimiter: Column separator.
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
    Read a CSV file as a list of dictionaries.

    The first row holds the headers, which are used as keys.

    :param csv_filename: File path.
    :param delimiter: Column separator.
    :return: Rows, one per dictionary.
    :rtype: list[dict[str, str]]
    """
    with Path(csv_filename).open(newline='', encoding='utf-8') as input_file:
        return list(csv.DictReader(input_file, delimiter=delimiter))
