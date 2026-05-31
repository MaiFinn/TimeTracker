from datetime import datetime


def calculate_total_time(start_time, end_time) -> str:
    """Calculate total working time between start and end time."""

    start_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)

    if end_datetime <= start_datetime:
        raise ValueError("End time must be after start time.")

    duration = end_datetime - start_datetime

    return str(duration)