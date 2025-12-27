import sys
import logging
from loguru import logger
from src.config import Config

config = Config()

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def init_logger():
    """
    Настраивает логгер для всего приложения в зависимости от окружения.
    """

    if config.app.env == "testing":
        return

    # Удаляем стандартный обработчик, чтобы избежать дублирования
    logger.remove()

    # Определяем формат для консоли (разработка)
    dev_format = (
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )

    # Определяем формат для файла (продакшен)
    prod_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function} | {message}"

    # Настраиваем перехват логов из стандартного logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # В файл пишем все, в формате JSON для машинного анализа
    logger.add(
        config.logger.path,
        level=config.logger.level,
        rotation=config.logger.rotation,
        retention=config.logger.retention,
        compression=config.logger.compression,
        serialize=config.logger.serialize,  # Структурированное логирование в JSON
    )

    # Конфигурация для разработки (если не указано иное)
    if config.app.env == "dev":
        logger.add(sys.stderr, level="DEBUG", format=dev_format, colorize=True)
        logger.info("Режим разработки: логирование настроено для вывода в консоль.")

    # Конфигурация для продакшена
    elif config.app.env == "prod":
        # В консоль выводим только важные сообщения
        logger.add(sys.stderr, level="INFO", format=prod_format, colorize=False)
        logger.info("Режим продакшена: логирование настроено для вывода в консоль и файл.")