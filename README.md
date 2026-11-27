# derafu-support

General-purpose Python utilities. The library does not depend on Django.

Requires Python 3.14.

## Installation

```sh
pip install "derafu-support @ git+https://github.com/derafu/support-python.git"
```

## Contents

| Module | Contents |
|---|---|
| `dates` | YYYYMM periods (`period_current`, `period_previous`, `period_next`, `period_range`, `period_first_day`, `period_last_day`, `period_valid`), dates (`date_normalize`, `date_add_days`, `date_count_days`) and Spanish month names (`month_from_string`, `month_from_index`, `month_from_number`) |
| `dictionary_merge` | `merge()`: recursive merge of dictionaries |
| `dictionary_file_operations` | `dict_save_to_json()`, `dict_save_to_csv()` and `dict_load_from_csv()` |
| `is_empty` / `is_set` | Checks for empty values and defined keys |
| `log` | `MemoryLogging`: in-memory log that records the caller |
| `number_format` | `format_number()`: locale-aware thousands and decimal separators |
| `gravatar` | `email_md5()` and `gravatar_url()` |
| `encoding` | `base64_decode()` with optional padding |

Example: `from derafu_support.dates import period_current`.

The dictionary selector (`selector()`) lives in the
[derafu-selector](https://github.com/derafu/selector-python) library.

## Development

```sh
make install-dev PYTHON=python3.14   # creates venv/ with the library and tools
make check                           # ruff, formatting, mypy, pyright and pytest
```

## License

MIT. See [LICENSE](LICENSE).
