import logging

LOG_FILE = "app.log"
DEFAULT_LOG_MODE = logging.DEBUG

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


class LogHandler:
    _logger = None

    @classmethod
    def get_logger(cls, log_file=LOG_FILE):
        if cls._logger is None:
            cls._logger = logging.getLogger(__name__)
            cls._logger.setLevel(DEFAULT_LOG_MODE)

            # Create a file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(DEFAULT_LOG_MODE)

            # Create a log format
            formatter = logging.Formatter(LOG_FORMAT)
            file_handler.setFormatter(formatter)

            # Add the handlers to the logger
            cls._logger.addHandler(file_handler)

        return cls._logger


LOGGER = LogHandler().get_logger()
