import logging
from taxotagger.logger import setup_logging


def test_setup_logging_default():
    setup_logging()
    logger = logging.getLogger("taxotagger")
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1  # 1 console RichHandler


def test_setup_logging_custom_level():
    setup_logging(level="DEBUG")
    logger = logging.getLogger("taxotagger")
    assert logger.level == logging.DEBUG


def test_setup_logging_file(tmp_path):
    log_file = tmp_path / "test_log.log"
    setup_logging(file=str(log_file))
    logger = logging.getLogger("taxotagger")
    assert len(logger.handlers) == 2  # 1 console RichHandler + 1 file RichHandler


def test_setup_logging_no_console():
    setup_logging(to_console=False)
    logger = logging.getLogger("taxotagger")
    assert len(logger.handlers) == 0
