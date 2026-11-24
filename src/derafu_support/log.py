"""Registro (log) de mensajes en memoria."""

import inspect
from collections.abc import Mapping
from datetime import datetime
from types import FrameType
from typing import ClassVar, Literal, overload

_NIVELES = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL',
}
# niveles de la pila que separan al llamador real de LogMessage.__init__:
# el método de MemoryLogging que registra (debug, info, ...) y __write
_NIVELES_INTERNOS = 2


class LogMessage:
    """Mensaje de un log, con los datos de quién lo registró."""

    log_format: ClassVar[str] = (
        '%(created)s %(category)s %(level_name)s: %(message)s '
        '[%(module)s:%(line_number)s]'
    )

    def __init__(
        self,
        level: int,
        message: str,
        args: Mapping[str, object] | None = None,
        category: str | None = None,
        data: object = None,
        caller_level: int | None = None,
    ) -> None:
        """
        Crea el mensaje y registra el módulo, archivo y línea del llamador.

        :param level: Nivel del mensaje (10 DEBUG a 50 CRITICAL).
        :param message: Texto del mensaje.
        :param args: Argumentos asociados al mensaje.
        :param category: Categoría; por defecto ``general``.
        :param data: Datos adicionales.
        :param caller_level: Cuántos niveles de la pila subir para llegar al
            llamador; por defecto 1 (quien llamó al método del log).
        """
        caller_level = (
            1 if caller_level is None else int(caller_level)
        ) + _NIVELES_INTERNOS
        # datos del mensaje del log
        self.created = (
            datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')
        )
        self.category = category if category is not None else 'general'
        self.level = level
        self.message = message
        self.args = args
        self.data = data
        # agregar los datos del que llamó al log
        caller_frame = self._get_caller_frame(caller_level)
        frame_info = inspect.getframeinfo(caller_frame)
        modulo = inspect.getmodule(caller_frame)
        # sin módulo (por ejemplo, código ejecutado con exec) se usa el
        # nombre del módulo del frame
        self.module: str = (
            modulo.__name__
            if modulo is not None
            else str(caller_frame.f_globals.get('__name__', ''))
        )
        self.filename = frame_info.filename
        self.line_number = frame_info.lineno
        self.function_name = frame_info.function

    @property
    def level_name(self) -> str:
        """
        Entrega el nombre del nivel del mensaje.

        :return: Nombre del nivel (``DEBUG``, ``INFO``, etc.).
        :rtype: str
        :raises KeyError: Si el nivel no es uno de los estándar.
        """
        return _NIVELES[int(self.level)]

    def __str__(self) -> str:
        """
        Entrega el mensaje con el formato del log.

        :return: Mensaje formateado con ``log_format``.
        :rtype: str
        """
        return self.log_format % self.to_dict()

    def to_dict(self) -> dict[str, object]:
        """
        Entrega los datos del mensaje.

        :return: Datos del mensaje y de quién lo registró.
        :rtype: dict[str, object]
        """
        return {
            'created': self.created,
            'category': self.category,
            'level': self.level,
            'level_name': self.level_name,
            'message': self.message,
            'args': self.args,
            'data': self.data,
            'module': self.module,
            'filename': self.filename,
            'line_number': self.line_number,
            'function_name': self.function_name,
        }

    @staticmethod
    def _get_caller_frame(caller_level: int | None = None) -> FrameType:
        """
        Obtiene el frame del llamador N niveles hacia arriba en la pila.

        Si la pila es más corta, se entrega el último frame disponible.

        :param caller_level: Niveles que se sube en la pila.
        :return: Frame del llamador.
        :rtype: FrameType
        :raises RuntimeError: Si el intérprete no permite leer la pila.
        """
        caller_level = (0 if caller_level is None else caller_level) + 1
        caller_frame = inspect.currentframe()
        if caller_frame is None:
            # sólo pasa en intérpretes sin soporte de frames
            msg = 'El intérprete no permite leer la pila de llamadas'
            raise RuntimeError(msg)
        for _ in range(caller_level):
            if caller_frame.f_back is None:
                break
            caller_frame = caller_frame.f_back
        return caller_frame


class MemoryLogging:
    """Log que guarda los mensajes en memoria, en una lista."""

    # niveles de severidad de los mensajes, de menor a mayor
    DEBUG: ClassVar[int] = 10
    INFO: ClassVar[int] = 20
    WARNING: ClassVar[int] = 30
    ERROR: ClassVar[int] = 40
    CRITICAL: ClassVar[int] = 50

    def __init__(
        self,
        level: int | None = None,
        category: str | None = None,
        caller_level: int | None = None,
    ) -> None:
        """
        Crea el log vacío.

        :param level: Nivel mínimo que se guarda; por defecto ``INFO``.
        :param category: Categoría por defecto de los mensajes.
        :param caller_level: Niveles de la pila por defecto para identificar
            al llamador.
        """
        self.__logs: list[LogMessage] = []
        self.logging_level = level if level is not None else MemoryLogging.INFO
        self.default_category = category
        self.caller_level = caller_level

    def __write(
        self,
        level: int,
        message: str,
        args: Mapping[str, object] | None,
        category: str | None,
        data: object,
        caller_level: int | None,
    ) -> LogMessage:
        """
        Crea un mensaje y lo guarda si alcanza el nivel mínimo.

        :param level: Nivel del mensaje.
        :param message: Texto del mensaje.
        :param args: Argumentos asociados al mensaje.
        :param category: Categoría; si es None se usa la por defecto.
        :param data: Datos adicionales.
        :param caller_level: Niveles de la pila; si es None se usa el por
            defecto.
        :return: Mensaje creado (se guarde o no).
        :rtype: LogMessage
        """
        if category is None:
            category = self.default_category
        caller_level = (
            caller_level if caller_level is not None else self.caller_level
        )
        log_message = LogMessage(
            level, message, args, category, data, caller_level
        )
        if level >= self.logging_level:
            self.__logs.append(log_message)
        return log_message

    def debug(
        self,
        message: str,
        args: Mapping[str, object] | None = None,
        category: str | None = None,
        data: object = None,
        caller_level: int | None = None,
    ) -> LogMessage:
        """
        Registra un mensaje de nivel DEBUG.

        :param message: Texto del mensaje.
        :param args: Argumentos asociados al mensaje.
        :param category: Categoría del mensaje.
        :param data: Datos adicionales.
        :param caller_level: Niveles de la pila para identificar al llamador.
        :return: Mensaje creado.
        :rtype: LogMessage
        """
        return self.__write(
            MemoryLogging.DEBUG, message, args, category, data, caller_level
        )

    def info(
        self,
        message: str,
        args: Mapping[str, object] | None = None,
        category: str | None = None,
        data: object = None,
        caller_level: int | None = None,
    ) -> LogMessage:
        """
        Registra un mensaje de nivel INFO.

        :param message: Texto del mensaje.
        :param args: Argumentos asociados al mensaje.
        :param category: Categoría del mensaje.
        :param data: Datos adicionales.
        :param caller_level: Niveles de la pila para identificar al llamador.
        :return: Mensaje creado.
        :rtype: LogMessage
        """
        return self.__write(
            MemoryLogging.INFO, message, args, category, data, caller_level
        )

    def warning(
        self,
        message: str,
        args: Mapping[str, object] | None = None,
        category: str | None = None,
        data: object = None,
        caller_level: int | None = None,
    ) -> LogMessage:
        """
        Registra un mensaje de nivel WARNING.

        :param message: Texto del mensaje.
        :param args: Argumentos asociados al mensaje.
        :param category: Categoría del mensaje.
        :param data: Datos adicionales.
        :param caller_level: Niveles de la pila para identificar al llamador.
        :return: Mensaje creado.
        :rtype: LogMessage
        """
        return self.__write(
            MemoryLogging.WARNING, message, args, category, data, caller_level
        )

    def error(
        self,
        message: str,
        args: Mapping[str, object] | None = None,
        category: str | None = None,
        data: object = None,
        caller_level: int | None = None,
    ) -> LogMessage:
        """
        Registra un mensaje de nivel ERROR.

        :param message: Texto del mensaje.
        :param args: Argumentos asociados al mensaje.
        :param category: Categoría del mensaje.
        :param data: Datos adicionales.
        :param caller_level: Niveles de la pila para identificar al llamador.
        :return: Mensaje creado.
        :rtype: LogMessage
        """
        return self.__write(
            MemoryLogging.ERROR, message, args, category, data, caller_level
        )

    def critical(
        self,
        message: str,
        args: Mapping[str, object] | None = None,
        category: str | None = None,
        data: object = None,
        caller_level: int | None = None,
    ) -> LogMessage:
        """
        Registra un mensaje de nivel CRITICAL.

        :param message: Texto del mensaje.
        :param args: Argumentos asociados al mensaje.
        :param category: Categoría del mensaje.
        :param data: Datos adicionales.
        :param caller_level: Niveles de la pila para identificar al llamador.
        :return: Mensaje creado.
        :rtype: LogMessage
        """
        return self.__write(
            MemoryLogging.CRITICAL, message, args, category, data, caller_level
        )

    @overload
    def get_all(self, as_dict: Literal[False] = False) -> list[LogMessage]: ...

    @overload
    def get_all(self, as_dict: Literal[True]) -> list[dict[str, object]]: ...

    def get_all(
        self, as_dict: bool = False
    ) -> list[LogMessage] | list[dict[str, object]]:
        """
        Entrega los mensajes guardados.

        :param as_dict: Entregar cada mensaje como diccionario
            (``LogMessage.to_dict()``) en vez de como ``LogMessage``.
        :return: Mensajes, del más antiguo al más reciente.
        :rtype: list[LogMessage] | list[dict[str, object]]
        """
        if as_dict:
            return [log.to_dict() for log in self.__logs]
        return self.__logs

    @overload
    def flush(self, as_dict: Literal[False] = False) -> list[LogMessage]: ...

    @overload
    def flush(self, as_dict: Literal[True]) -> list[dict[str, object]]: ...

    def flush(
        self, as_dict: bool = False
    ) -> list[LogMessage] | list[dict[str, object]]:
        """
        Entrega los mensajes guardados y vacía el log.

        :param as_dict: Entregar cada mensaje como diccionario en vez de como
            ``LogMessage``.
        :return: Mensajes que había en el log.
        :rtype: list[LogMessage] | list[dict[str, object]]
        """
        logs = (
            [log.to_dict() for log in self.__logs] if as_dict else self.__logs
        )
        self.__logs = []
        return logs
