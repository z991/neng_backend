# __author__ = itsneo1990

import time
from datetime import datetime as py_time
from datetime import timedelta

from django.utils.timezone import is_naive, get_default_timezone, now, \
    make_naive, is_aware

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
STRATEGY_TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%s %s" % (DATE_FORMAT, TIME_FORMAT)
USE_MICROSECONDS = True


def time_to_str(time, format=STRATEGY_TIME_FORMAT):
    return time.strftime(format)


def date_to_str(date, format=DATE_FORMAT):
    return date.strftime(format)


def datetime_to_str(datetime, format=DATETIME_FORMAT):
    if is_aware(datetime):
        datetime = to_naive_datetime(datetime)

    return datetime.strftime(format)


def datetime_delta(datetime, **kwargs):
    delta = timedelta(**kwargs)
    return datetime + delta


def str_to_datetime(string, format=DATETIME_FORMAT):
    if isinstance(string, py_time):
        if is_naive(string):
            return to_aware_datetime(string)
        else:
            return string

    return to_aware_datetime(py_time.strptime(string, format))


def to_aware_datetime(value):
    time_zone = get_default_timezone()
    return time_zone.localize(value, is_dst=False)


def to_naive_datetime(value):
    time_zone = get_default_timezone()
    return make_naive(value, time_zone)


def datetime_now():
    return now()


def dates_during(from_date, to_date, weekdays=None):
    if weekdays is None:
        weekdays = range(1, 8)
    if not weekdays:
        weekdays = []

    dates = []
    delta_day = (to_date - from_date).days
    for delta in range(0, delta_day + 1):
        date = from_date + timedelta(days=delta)
        if date.weekday() + 1 in weekdays:
            dates.append(date)
    return dates


def get_weekday(datetime):
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return days[datetime.weekday()]


def datetime_to_timestamp(datetime, use_microseconds=USE_MICROSECONDS):
    if is_aware(datetime):
        datetime = to_naive_datetime(datetime)
    timetuple = datetime.timetuple()
    seconds = time.mktime(timetuple)
    if use_microseconds:
        return seconds * 1000
    else:
        return seconds


def date_to_timestamp(date, use_microseconds=USE_MICROSECONDS):
    timetuple = date.timetuple()
    seconds = time.mktime(timetuple)
    if use_microseconds:
        return seconds * 1000
    else:
        return seconds


def timestamp_to_datetime(timestamp, use_microseconds=USE_MICROSECONDS):
    if use_microseconds:
        timestamp = float(timestamp) / 1000
    else:
        timestamp = float(timestamp)

    datetime = py_time.fromtimestamp(timestamp)
    return datetime


def timestamp_to_date(timestamp, use_microseconds=USE_MICROSECONDS):
    datetime = timestamp_to_datetime(timestamp, use_microseconds)
    return datetime.date()


def str_to_time(input_str):
    from datetime import time
    hour, minute = input_str.split(":")
    return time(int(hour), int(minute))


def time_delta(from_time, seconds=3600):
    from datetime import date, datetime, timedelta
    dt = datetime.combine(date.today(), from_time) + timedelta(seconds=seconds)
    return dt.time()


def str_to_date(input_str):
    return str_to_datetime(input_str, DATE_FORMAT).date()


def str_to_birthday(input_str):
    if not input_str:
        return None
    return str_to_datetime(input_str, DATE_FORMAT).date()


def get_week_from_to(datetime):
    return datetime_delta(
        datetime,
        days=-datetime.weekday()
    ), datetime_delta(datetime, days=6 - datetime.weekday())


def datetime_in_start_end(datetime, start, end):
    compare_date = to_naive_datetime(datetime).date()
    start_date = to_naive_datetime(start).date()
    end_date = to_naive_datetime(datetime_delta(end, days=1)).date()

    if start_date <= compare_date < end_date:
        return True
    return False


def get_latest_from_to(start, end, days=1):
    if start and end:
        start = str_to_datetime(start, format=DATE_FORMAT)
        end = str_to_datetime(end, format=DATE_FORMAT)
        end = datetime_delta(end, days=1)
    else:
        today = str_to_datetime(
            date_to_str(to_naive_datetime(datetime_now()).date()),
            format=DATE_FORMAT)
        end = datetime_delta(today, days=1)
        start = datetime_delta(end, days=-days)

    return start, end


def compare_date(date1, date2):
    if date1 == 0 and date2 == 0:
        return ""
    elif date1 == 0 and date2 != 0:
        return date_to_str(date2, format='%Y-%m-%d %H:%M:%S')
    elif date1 != 0 and date2 == 0:
        return date_to_str(date1, format='%Y-%m-%d %H:%M:%S')
    elif date1 > date2:
        return date_to_str(date1, format='%Y-%m-%d %H:%M:%S')
    else:
        return date_to_str(date2, format='%Y-%m-%d %H:%M:%S')