# import dependencies
import datetime


def date_to_day(date: datetime.date) -> int:
    """
    Changes a date to the day serial number within the year.

    Parameters
    ----------
    date : datetime.time
        A date for which the day serial number is determined.

    Returns
    -------
    int
        A day serial number for the given date
    """
    day = abs(date - datetime.date(date.year, 1, 1)).days + 1
    return day


def day_to_date(year: int, day: int) -> datetime.date:
    """
    Determines the date for the given `day` of the given `year`

    Parameters
    ----------
    year : int
        Year of the day of interest
    day : int
        Day serial number within the `year`

    Returns
    -------
    datetime.date
        A date for the given `day`of the `year`
    """
    date = datetime.date(year, 1, 1) + datetime.timedelta(days=day - 1)
    return date
