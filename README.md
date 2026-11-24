# derafu-support

Utilidades generales de Python, separadas de `django-sasco`. La librería no
depende de Django: lo que es de Django va en cada proyecto que lo usa.

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

## Pendiente: piezas de Django que siguen en django-sasco

Lo que es de Django se mueve a cada proyecto que lo usa, a medida que cada
proyecto deja `django-sasco`. Estas piezas no las usa BHExpress (el primer
proyecto migrado), así que quedan en `django-sasco` hasta migrar el proyecto
que sí las usa, y ahí se mueven a ese proyecto:

| Pieza en django-sasco | Proyecto que la usa |
|---|---|
| `forms.dictionary_selector`: `SelectorForm`, `SelectorCharField`, `SelectorEmailField`, `SelectorRegexField` (usa `selector()` de derafu-selector) | billmysales |
| `templatetags.date_string_to_date` | billmysales |
| `templatetags.mathematical_operations` (`multiplier`) | billmysales |

## Cambios respecto de django-sasco

- Los módulos `utils.datetime` y `utils.base64` se llaman `dates` y
  `encoding`, para no tapar los módulos de la biblioteca estándar.
- El formateo de números del tag `num` está en `format_number()`, que recibe
  el idioma (el tag de cada proyecto le pasa el idioma de Django).
- `is_set()` entrega sus mensajes de error sin traducción (antes usaba la
  traducción de Django).
- Las excepciones son subclases de las que se lanzaban antes
  (`AttributeError`, `TypeError`), así que quien las captura no cambia.
- `MemoryLogging` ya no falla cuando el llamador no tiene módulo (por
  ejemplo, código ejecutado con `exec`).

## Desarrollo

```sh
make install-dev PYTHON=python3.14   # crea venv/ con la librería y herramientas
make check                           # ruff, formato, mypy, pyright y pytest
```

## Licencia

MIT. Ver [LICENSE](LICENSE).
