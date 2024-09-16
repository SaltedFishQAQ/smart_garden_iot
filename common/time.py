from datetime import datetime, timedelta


def time_to_str(time_obj, layout="%Y-%m-%d %H:%M:%S") -> str:
    return time_obj.strftime(layout)


def str_to_time(time_str, str_format="%Y-%m-%d %H:%M:%S") -> datetime:
    return datetime.strptime(time_str, str_format)


def time_add(time_obj, seconds: int):
    return time_obj + timedelta(seconds=seconds)
