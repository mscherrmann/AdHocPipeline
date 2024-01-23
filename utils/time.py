# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 20:25:54 2024

@author: scherrmann
"""

from datetime import datetime, timedelta
import pandas as pd

def get_time_periods(start_date, end_date, period_length):
    """
    Generates a list of time periods between two specified dates.

    This function takes a start date and an end date in 'dd.mm.yyyy' format,
    along with a period length (in days). It then generates a list of time periods,
    each of a specified length. Each period is represented as a list containing two dates:
    the start and the end of the period. If the remaining days at the end of the range
    do not make up a full period, the last period is shortened accordingly.

    Parameters:
    start_date (str): The starting date in 'dd.mm.yyyy' format.
    end_date (str): The ending date in 'dd.mm.yyyy' format.
    period_length (int): The length of each period in days.

    Returns:
    list of lists: A list where each element is a period represented by a list of two dates:
                   the start and the end of that period in 'dd.mm.yyyy' format.

    Example:
    get_time_periods("01.01.2020", "07.01.2020", 2) should return
    [["01.01.2020", "02.01.2020"], ["03.01.2020", "04.01.2020"], ["05.01.2020", "06.01.2020"], ["07.01.2020", "07.01.2020"]]
    """
    # Convert start_date and end_date to datetime objects
    start = datetime.strptime(start_date, "%d.%m.%Y")
    end = datetime.strptime(end_date, "%d.%m.%Y")

    # Initialize the current period start date and the list of periods
    current_period_start = start
    periods = []

    # Iterate over the date range and create periods
    while current_period_start <= end:
        # Calculate the end date of the current period
        current_period_end = current_period_start + timedelta(days=period_length - 1)

        # Adjust the period end date if it exceeds the overall end date
        if current_period_end > end:
            current_period_end = end

        # Append the period to the list
        periods.append([
            current_period_start.strftime("%d.%m.%Y"),
            current_period_end.strftime("%d.%m.%Y")
        ])

        # Move to the next period
        current_period_start = current_period_end + timedelta(days=1)

    return periods

def date_conv(s):
    if "-" in s:
        return pd.to_datetime(s, format='%Y-%m-%d').strftime("%d.%m.%Y")
    else:
        return s