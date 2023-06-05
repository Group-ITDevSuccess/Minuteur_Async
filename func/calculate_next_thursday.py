import datetime


def calculate_next_thursday():
    current_datetime = datetime.datetime.now()
    days_ahead = (3 - current_datetime.weekday() + 7) % 7
    target_datetime = current_datetime + datetime.timedelta(days=days_ahead)
    target_datetime = target_datetime.replace(hour=9, minute=0, second=0, microsecond=0)
    return target_datetime

