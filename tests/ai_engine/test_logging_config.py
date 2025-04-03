import unittest
import os
import json
import logging
import time
from src.ai_engine.logging_config import setup_logging, get_logger, JsonFormatter

class TestLoggingConfig(unittest.TestCase):
    def setUp(self):
        self.test_log_dir = "test_logs"
        self.logger = setup_logging(log_dir=self.test_log_dir)

    def tearDown(self):
        # Close all handlers
        if hasattr(self, 'logger'):
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)
        
        # Clean up test log files
        if os.path.exists(self.test_log_dir):
            time.sleep(0.1)  # Small delay to ensure files are released
            for file in os.listdir(self.test_log_dir):
                try:
                    os.remove(os.path.join(self.test_log_dir, file))
                except PermissionError:
                    pass  # Skip if file is still locked
            os.rmdir(self.test_log_dir)

    def test_logger_creation(self):
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(len(self.logger.handlers), 2)  # File and console handlers

    def test_json_formatting(self):
        test_logger = get_logger("test")
        test_logger.setLevel(logging.INFO)  # Ensure INFO level is enabled

        # Create a test handler that captures output
        class TestHandler(logging.Handler):
            def __init__(self):
                super().__init__()
                self.records = []

            def emit(self, record):
                self.records.append(self.format(record))

        handler = TestHandler()
        handler.setFormatter(JsonFormatter())
        test_logger.addHandler(handler)

        test_message = "Test log message"
        test_logger.info(test_message)

        # Ensure we have a record
        self.assertTrue(len(handler.records) > 0, "No log records were captured")
        # Verify JSON format
        log_record = json.loads(handler.records[0])
        self.assertEqual(log_record['message'], test_message)

    def test_correlation_id(self):
        logger1 = get_logger("test1")
        logger2 = get_logger("test2")
        self.assertNotEqual(logger1.correlation_id, logger2.correlation_id)

    def test_log_rotation(self):
        logger = setup_logging(
            log_dir=self.test_log_dir,
            max_bytes=100,  # Small size to trigger rotation
            backup_count=2
        )
        
        # Generate enough logs to trigger rotation
        for i in range(50):
            logger.info("X" * 10)  # Each log entry should be > 100 bytes when formatted
        
        log_files = os.listdir(self.test_log_dir)
        self.assertGreaterEqual(len(log_files), 2)  # Should have at least 2 files due to rotation
        