import datetime

def calculate_time_remaining():
    current_datetime = datetime.datetime.now()
    target_datetime = current_datetime.replace(hour=9, minute=0, second=0, microsecond=0)
    days_ahead = (3 - current_datetime.weekday() + 7) % 7

    if current_datetime >= target_datetime:
        days_ahead += 7

    target_datetime += datetime.timedelta(days=days_ahead)
    time_remaining = target_datetime - current_datetime
    return time_remaining
