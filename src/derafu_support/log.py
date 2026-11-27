"""In-memory message log."""

import inspect
from collections.abc import Mapping
from datetime import datetime
from types import FrameType
from typing import ClassVar, Literal, overload, override

_NIVELES = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL',
}
# stack levels between the real caller and LogMessage.__init__: the
# MemoryLogging method that logs (debug, info, ...) and __write
_NIVELES_INTERNOS = 2


class LogMessage:
    """Log message, with data about who logged it."""

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
        Create the message and record the caller's module, file and line.

        :param level: Message level (10 DEBUG to 50 CRITICAL).
        :param message: Message text.
        :param args: Arguments associated with the message.
        :param category: Category; ``general`` by default.
        :param data: Additional data.
        :param caller_level: How many stack levels to go up to reach the
            caller; 1 by default (whoever called the log method).
        """
        caller_level = (
            1 if caller_level is None else int(caller_level)
        ) + _NIVELES_INTERNOS
        # log message data
        self.created = (
            datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')
        )
        self.category = category if category is not None else 'general'
        self.level = level
        self.message = message
        self.args = args
        self.data = data
        # add the data of whoever called the log
        caller_frame = self._get_caller_frame(caller_level)
        frame_info = inspect.getframeinfo(caller_frame)
        modulo = inspect.getmodule(caller_frame)
        # without a module (for example, code run with exec) the frame's
        # module name is used
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
        Name of the message level.

        :return: Level name (``DEBUG``, ``INFO``, etc.).
        :rtype: str
        :raises KeyError: If the level is not a standard one.
        """
        return _NIVELES[int(self.level)]

    @override
    def __str__(self) -> str:
        """
        Return the message in the log format.

        :return: Message formatted with ``log_format``.
        :rtype: str
        """
        return self.log_format % self.to_dict()

    def to_dict(self) -> dict[str, object]:
        """
        Return the message data.

        :return: Data of the message and of who logged it.
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
        Get the caller's frame N levels up the stack.

        If the stack is shorter, the last available frame is returned.

        :param caller_level: Levels to go up the stack.
        :return: Caller's frame.
        :rtype: FrameType
        :raises RuntimeError: If the interpreter does not allow reading the
            stack.
        """
        caller_level = (0 if caller_level is None else caller_level) + 1
        caller_frame = inspect.currentframe()
        if caller_frame is None:
            # only happens in interpreters without frame support
            msg = 'El intérprete no permite leer la pila de llamadas'
            raise RuntimeError(msg)
        for _ in range(caller_level):
            if caller_frame.f_back is None:
                break
            caller_frame = caller_frame.f_back
        return caller_frame


class MemoryLogging:
    """Log that keeps the messages in memory, in a list."""

    # message severity levels, from lowest to highest
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
        Create the empty log.

        :param level: Minimum level that is kept; ``INFO`` by default.
        :param category: Default category of the messages.
        :param caller_level: Default stack levels used to identify the
            caller.
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
        Create a message and keep it if it reaches the minimum level.

        :param level: Message level.
        :param message: Message text.
        :param args: Arguments associated with the message.
        :param category: Category; if None, the default one is used.
        :param data: Additional data.
        :param caller_level: Stack levels; if None, the default is used.
        :return: Created message (whether it is kept or not).
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
        Log a DEBUG level message.

        :param message: Message text.
        :param args: Arguments associated with the message.
        :param category: Message category.
        :param data: Additional data.
        :param caller_level: Stack levels used to identify the caller.
        :return: Created message.
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
        Log a INFO level message.

        :param message: Message text.
        :param args: Arguments associated with the message.
        :param category: Message category.
        :param data: Additional data.
        :param caller_level: Stack levels used to identify the caller.
        :return: Created message.
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
        Log a WARNING level message.

        :param message: Message text.
        :param args: Arguments associated with the message.
        :param category: Message category.
        :param data: Additional data.
        :param caller_level: Stack levels used to identify the caller.
        :return: Created message.
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
        Log a ERROR level message.

        :param message: Message text.
        :param args: Arguments associated with the message.
        :param category: Message category.
        :param data: Additional data.
        :param caller_level: Stack levels used to identify the caller.
        :return: Created message.
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
        Log a CRITICAL level message.

        :param message: Message text.
        :param args: Arguments associated with the message.
        :param category: Message category.
        :param data: Additional data.
        :param caller_level: Stack levels used to identify the caller.
        :return: Created message.
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
        Return the kept messages.

        :param as_dict: Return each message as a dictionary
            (``LogMessage.to_dict()``) instead of as a ``LogMessage``.
        :return: Messages, from oldest to newest.
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
        Return the kept messages and empty the log.

        :param as_dict: Return each message as a dictionary instead of as a
            ``LogMessage``.
        :return: Messages that were in the log.
        :rtype: list[LogMessage] | list[dict[str, object]]
        """
        logs = (
            [log.to_dict() for log in self.__logs] if as_dict else self.__logs
        )
        self.__logs = []
        return logs
