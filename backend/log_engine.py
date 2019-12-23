import logging
import settings


class LogEngine(object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._handler = logging.FileHandler(settings.LOG_FILE)
        self._formatter = logging.Formatter("%(levelname)s: %(asctime)s - %(funcName)s: %(message)s")  # Fuck PEP8
        self._handler.setFormatter(self._formatter)
        self._logger.addHandler(self._handler)
        self._logger.setLevel(logging.DEBUG)
