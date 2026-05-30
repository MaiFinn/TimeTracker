from timetracker.utils.logger import setup_logger


def test_setup_logger_writes_to_file(tmp_path) -> None:
    log_file = tmp_path / "run.log"

    logger = setup_logger(
        name="quant_research_lab.test_logger",
        log_file=log_file,
    )

    logger.info("Test log message")

    assert log_file.exists()

    log_text = log_file.read_text(encoding="utf-8")

    assert "Test log message" in log_text
    assert "INFO" in log_text


def test_setup_logger_without_file() -> None:
    logger = setup_logger(
        name="quant_research_lab.console_only_test",
        log_file=None,
    )

    logger.info("Console-only logger works")

    assert logger.name == "quant_research_lab.console_only_test"
    assert len(logger.handlers) == 1