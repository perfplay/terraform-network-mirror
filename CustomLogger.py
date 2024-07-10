#!/usr/bin/env python3

import logging
import os
import sys


class CustomLogger:
    def __init__(self):
        self.logger = self.setup_logging()

    @staticmethod
    def setup_logging():
        log_level = os.getenv('PY_LOG_LEVEL', 'DEBUG').upper()
        log_format = os.getenv('PY_LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        date_format = os.getenv('PY_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stderr_handler = logging.StreamHandler(sys.stderr)

        stdout_handler.setLevel(log_level)
        stderr_handler.setLevel(log_level)

        stdout_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
        stderr_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)

        if logger.hasHandlers():
            logger.handlers.clear()

        stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
        stderr_handler.addFilter(lambda record: record.levelno > logging.INFO)

        logger.addHandler(stdout_handler)
        logger.addHandler(stderr_handler)

        return logger

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
