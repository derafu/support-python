# derafu-support

Utilidades generales de Python. La librería no depende de Django.

Requiere Python 3.14.

## Instalación

```sh
pip install "derafu-support @ git+https://github.com/derafu/support-python.git"
```

## Contenido

| Módulo | Contenido |
|---|---|
| `dates` | Períodos AAAAMM (`period_current`, `period_previous`, `period_next`, `period_range`, `period_first_day`, `period_last_day`, `period_valid`), fechas (`date_normalize`, `date_add_days`, `date_count_days`) y meses (`month_from_string`, `month_from_index`, `month_from_number`) |
| `dictionary_merge` | `merge()`: combinación recursiva de diccionarios |
| `dictionary_file_operations` | `dict_save_to_json()`, `dict_save_to_csv()` y `dict_load_from_csv()` |
| `is_empty` / `is_set` | Revisión de valores vacíos y de llaves definidas |
| `log` | `MemoryLogging`: log en memoria que registra quién llamó |
| `number_format` | `format_number()`: separadores de miles y decimales según el idioma |
| `gravatar` | `email_md5()` y `gravatar_url()` |
| `encoding` | `base64_decode()` con relleno opcional |

Ejemplo: `from derafu_support.dates import period_current`.

El selector de diccionarios (`selector()`) está en la librería
[derafu-selector](https://github.com/derafu/selector-python).

## Desarrollo

```sh
make install-dev PYTHON=python3.14   # crea venv/ con la librería y herramientas
make check                           # ruff, formato, mypy, pyright y pytest
```

## Licencia

MIT. Ver [LICENSE](LICENSE).
