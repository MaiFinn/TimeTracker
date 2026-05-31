from datetime import time

from timetracker.utils.time_utils import calculate_total_time


def test_calculate_total_time():
    start_time = time(10, 0)
    end_time = time(12, 30)

    total_time = calculate_total_time(start_time, end_time)

    assert total_time == "2:30:00"