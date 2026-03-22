import logging
from app.core.logging import setup_logging, get_logger


class TestLogging:
    def test_get_logger_returns_logger(self):
        logger = get_logger("test")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_name(self):
        logger = get_logger("test_module")
        assert logger.name == "test_module"

    def test_get_logger_different_names_different_instances(self):
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        assert logger1.name != logger2.name

    def test_setup_logging_runs_without_error(self):
        setup_logging()

    def test_logger_can_log_messages(self):
        logger = get_logger("test")
        logger.info("Test message")
        logger.debug("Debug message")
        logger.warning("Warning message")
        logger.error("Error message")
