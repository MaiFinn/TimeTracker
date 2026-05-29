import logging
from timetracker.work_entry_handler import create_work_entry
from timetracker.utils.logging import setup_logger

setup_logger(name="timetracker", log_file="artifacts/logs/timetracker.log")
logger = logging.getLogger("timetracker.scripts.work_entry_handler_test")

date = "2026-02-11"
start_time = "11:00"
end_time = "12:00"

logger.info(f"Create worke entry with date: {date}, start time: {start_time} and end time: {end_time}.")

create_work_entry(date, start_time, end_time)