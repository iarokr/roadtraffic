# import dependencies
import datetime
import os
import pathlib
import time
import typing
import warnings

import pandas as pd
import requests
from tqdm import tqdm

from .constants import (
    DEF_COL_NAMES_FINTRAFFIC,
    URL_FINTRAFFIC,
    DEF_FILENAME_U,
)


# Download the .csv report of `tms_id` station for the day `day_of_year`
def read_raw_report(
    tms_id: int,
    year: int,
    day: int,
    load_path: typing.Optional[str] = None,
    save: bool = False,
    save_path: typing.Optional[str] = None,
    sort_total_time: bool = True,
) -> pd.DataFrame:
    """
    Download the raw data from Fintraffic for the `tms_id` station for the `day` of the `year`. \
    By default the data is cleaned - faulty observations are deleted. \
    The type of vehicle is determined based on the classification from Fintraffic.

    | It is possible to save a `.pkl` file, setting `save` to True. The default filename format "lamraw_TMS_YY_DD_bz2.pkl" is used. 
    | It is possible to locally read a `.pkl` file locally, specifying a `path_name`. \
        At first, the search for the processed files is done. \
        If it is not found, then the unprocessed file is looked up. \
        Processed file is the one load with the use of this function. \
        Unprocessed file is the one loaded using some other way. 

    Parameters
    ----------
    tms_id : int
        The identity number of a traffic measurement station (TMS). \
        Meta-data about TMS is available `here <https://www.digitraffic.fi/en/road-traffic/#current-data-from-tms-stations>`_.
    year : int
        The year data was collected in the 4-digit format. Data is available starting from 1995 only. 
    day : int
        The day of the year the data was collected. \
        The day is provide as an integer in range(1, 366), with 1 - January 1st, \
        365 (366 in leap year) - December 31st. \
        To caclulate the day of the year from a date you can use `roadtraffic.utils.funcs.date_to_day()` function.
    save : bool, optional
        If specified, saves loaded data in the .pkl file format with bz2-compression with the default filename format "lamraw_TMS_YY_DD_bz2_u.pkl", by default False
    load_path : str, optional
        If specified, reads data from the `path_name` folder from a locally saved bz2-compressed .pkl file. \
        Unprocessed "lamraw_TMS_YY_DD_bz2_u.pkl" files can be read, by default None
    save_path : str, optional
        If specified, saves loaded data in the `save_path` folder in the .pkl file format with bz2-compression with \
        the default filename format "lamraw_TMS_YY_DD_bz2_u.pkl", by default None
    sort_total_time : bool, optional
        If specified, sorts the data by the `total_time` column, by default True

    Returns
    -------
    pd.DataFrame
        A `pd.DataFrame` with the raw data.
        
    Raises
    ------
    AssertionError
        The day is incorrect, it should be 1 < day < 366.
    AssertionError
        The data is available starting from year 1995 only.

    See Also
    --------
    :func:`roadtraffic.utils.funcs.date_to_day`
        A function to convert a date into day of the year. 
    """  # noqa E501
    # Initiate timer
    # start_time = time.perf_counter()

    # Check assert errors
    # fmt: off
    assert 1 <= day <= 366, "[LOG] AssertionError: the day is incorrect, it should be 1 < day < 366"  # noqa
    assert 1995 <= year, "[LOG] AssertionError: the data is available starting from year 1995 only "  # noqa
    # fmt: on

    # Create column names for the pd.DataFrame
    column_names = DEF_COL_NAMES_FINTRAFFIC

    # Initiate an empty pd.DataFrame
    df = pd.DataFrame()

    # Create the actual filename for processed data
    # file_name = DEF_FILENAME

    # file_name = (
    #    file_name.replace("TMS", str(tms_id))
    #    .replace("YY", str(year)[2:4])
    #    .replace("DD", str(day))
    # )

    # Create the actual filename for unprocessed data
    file_name_u = DEF_FILENAME_U

    file_name_u = (
        file_name_u.replace("TMS", str(tms_id))
        .replace("YY", str(year)[2:4])
        .replace("DD", str(day))
    )

    if load_path is not None:

        file_path_u = load_path + "/" + file_name_u
        file_path_u = pathlib.Path(file_path_u)

        if os.path.isfile(file_path_u):
            df = pd.read_pickle(file_path_u, compression="bz2")

        if df.empty:
            # Stop timer
            # end_time = time.perf_counter()
            message = f"[LOG] Warning: {file_name_u} is not found at {load_path}. An empty pd.DataFrame will be returned." # noqa E501
            warnings.warn(message=message)
            if save is True:
                warnings.warn(
                    "[LOG] Warning: It is impossible to save a file, as data was not loaded. Check warning above."
                    # noqa E501
                )
        else:

            # Stop timer
            # end_time = time.perf_counter()

            # print(
            #    f"File {file_name_u} is loaded. "
            #    + f"Time spent: {end_time - start_time:.4f} sec."  # noqa E501
            # )

            # Save to .pkl if necessary
            if save is True:
                if save_path is None:
                    s_path = file_name_u
                else:
                    s_path = os.path.join(save_path, file_name_u)
                df.to_pickle(s_path, compression="bz2")
                print(f"[LOG] Data is successfully saved to {s_path}")

    else:
        # Assign URL path for data loading
        url = URL_FINTRAFFIC

        # Create the actual url
        url = (
            url.replace("TMS", str(tms_id))
            .replace("YY", str(year)[2:4])
            .replace("DD", str(day))
        )

        # Call the link to receive the response
        r = requests.get(url)

        # Try to download the file
        if r.status_code != 404:
            # Check that there is no connection limit
            if r.status_code == 429:
                for i in range(59, 0, -1):
                    print(
                        f"[LOG] Too many requests, waiting {i} seconds to connect again",
                        end="\x1b[1K\r",
                        flush=True,
                    )
                    time.sleep(1)
                r = requests.get(url)
            if r.status_code == 429:
                message = "[LOG] The server is overloaded. Please, try to load the data later. An empty pd.DataFrame will be returned"  # noqa E501
                warnings.warn(message=message)
                return pd.DataFrame()
            elif r.status_code == 404:
                # Stop timer
                # end_time = time.perf_counter()
                # print(f"Time spent: {end_time - start_time:.4f} seconds")
                message = f"[LOG] Warning: file at {url} does not exist. Try to select another day. An empty pd.DataFrame will be returned."  # noqa E501
                warnings.warn(message=message)
                if save is True:
                    warnings.warn(
                        "[LOG] Warning: It is impossible to save a file, as data was not loaded. Check warning above."
                        # noqa E501
                    )
            else:
                with open(file_name_u[:-4] + ".csv", "wb") as f:
                    f.write(r.content)
                df = pd.read_csv(
                    file_name_u[:-4] + ".csv",
                    delimiter=";",
                    names=column_names,
                )
                os.remove(file_name_u[:-4] + ".csv")

                # Stop timer
                # end_time = time.perf_counter()
                # print(
                #    f"Download successful - file for the sensor {tms_id} for the day {day} in year {year} was loaded in {end_time - start_time:.4f} seconds"  # noqa E501
                #)  # noqa E501

                # Save to .pkl if necessary
                if save is True:
                    if save_path is None:
                        s_path = file_name_u
                    else:
                        s_path = os.path.join(save_path, file_name_u)
                    df.to_pickle(s_path, compression="bz2")
                    print(f"[LOG] Data is successfully saved to {s_path}")
        else:
            # Stop timer
            # end_time = time.perf_counter()
            # print(f"Time spent: {end_time - start_time:.4f} seconds")
            message = f"[LOG] Warning: file at {url} does not exist. Try to select another day. An empty pd.DataFrame will be returned."  # noqa E501
            warnings.warn(message=message)
            if save is True:
                warnings.warn(
                    "[LOG] Warning: It is impossible to save a file, as data was not loaded. Check warning above."
                    # noqa E501
                )

    if not df.empty and sort_total_time:
        df.sort_values(by=["total_time"], inplace=True, ignore_index=True)
    return df


def read_many_reports(
        tms_id: int,
        days_list: list[tuple[int, int]],
        save: bool = False,
        load_path: typing.Optional[str] = None,
        save_path: typing.Optional[str] = None,
        sort_total_time: bool = True
) -> pd.DataFrame:
    """
    Download the raw data from Fintraffic for the specified station for a list of days.

    Parameters
    ----------
    tms_id: int
        The identity number of a traffic measurement station (TMS).
    days_list: list
        A list of tuples to download the data for. A format for each day is (year, day of year).
    load_path:
        If specified, reads data from the `path_name` folder from a locally saved bz2-compressed .pkl file. \
        Unprocessed "lamraw_TMS_YY_DD_bz2_u.pkl" files can be read, by default None
    save: bool, optional
        If specified, saves loaded data in the .pkl file format with bz2-compression with filename defined by
        `save_filename`, by default False
    save_path:
        If specified, saves data for each loaded day in the `save_path` folder in the .pkl file format with
        bz2-compression with a standard filename "lamraw_TMS_YY_DD_bz2_u.pkl", by default None
    sort_total_time : bool, optional
        If specified, sorts the data for each day by the `total_time` column and resets index , by default True

    Returns
    -------
    pd.DataFrame
        A `pd.DataFrame` with the raw data.
    """
    assert isinstance(days_list, list), "days_list must be a list."
    assert all([isinstance(day, tuple) for day in days_list]), "[LOG] AssertionError: days_list must contain only tuples." # noqa E501
    assert all([isinstance(day[0], int) for day in days_list]), "[LOG] AssertionError: days_list must contain only tuples of integers." # noqa E501
    assert all([isinstance(day[1], int) for day in days_list]), "[LOG] AssertionError: days_list must contain only tuples of integers." # noqa E501

    # Initiate timer
    start_time = time.perf_counter()
    total_files = len(days_list)
    loaded_files = 0

    # Initiate an empty pd.DataFrame
    df_all = pd.DataFrame()

    # Iterate over the list of days
    for year, day in tqdm(days_list, desc="Loading files", unit="files"):
        df = read_raw_report(
            tms_id=tms_id,
            year=year,
            day=day,
            load_path=load_path,
            save=save,
            save_path=save_path,
            sort_total_time=sort_total_time,
        )
        if not df.empty:
            if df_all.empty:
                df_all = df
            else:
                df_all = pd.concat([df_all, df], ignore_index=True)
            loaded_files += 1

    # Stop timer
    end_time = time.perf_counter()
    print(
        f"[LOG] Download finished - {loaded_files}/{total_files} files were loaded in {end_time - start_time:.4f} seconds" # noqa E501
    )

    return df_all


def process_data(
    df: pd.DataFrame,
    direction: typing.Optional[int] = None,
    lanes: typing.Optional[list] = None,
    delete_if_faulty: bool = True,
    hour_from: int = 0,
    hour_to: int = 23,
    assign_date: bool = True,
    calculate_vehicles: bool = True,
) -> pd.DataFrame:
    """Process raw data.

    Parameters
    ----------
    df : pd.DataFrame
        Data to be cleaned.
    direction : int, optional
        Direction of the traffic movement, can take values 1 or 2 only. Check your TMS for the direction,
        by default None
    lanes : list, optional
        Lanes to be included in the data, by default None
    delete_if_faulty : bool, optional
        If faulty data should be excluded, by default True
    hour_from : int, optional
        Hour from which beginning the data should be included, by default 0
    hour_to : int, optional
        Hour to which end the data should be included, by default 23
    assign_date : bool, optional
        If `True`, assigns the date to the data, by default True
    calculate_vehicles : bool, optional
        If `True`, calculates the number of different vehicles, by default True

    Raises
    ------
    AssertionError
        direction must be 1 or 2.
    AssertionError
        lanes must be a list.
    AssertionError
        lanes must contain only integers.
    AssertionError
        hour_from must be greater or equal to 0 but less than 23.
    AssertionError
        hour_to must be greater than hour_from and less than 24.

    Returns
    -------
    pd.DataFrame
        A `pd.DataFrame` with the processed data. Index is reset.
    """
    # DIRECTION
    if direction is not None:
        assert direction in [1, 2], "[LOG] AssertionError: direction must be 1 or 2."
        df = df[df["direction"] == direction]

    # LANES
    if lanes is not None:
        assert lanes is None or isinstance(lanes, list), "[LOG] AssertionError: lanes must be a list."
        assert lanes is None or all(
            [isinstance(lane, int) for lane in lanes]
        ), "[LOG] AssertionError: lanes must contain only integers."

        df = df[df["lane"].isin(lanes)]

    # HOUR_TO and HOUR_FROM
    assert (
        0 <= hour_from <= 23
    ), "[LOG] AssertionError: hour_from must be greater or equal to 0 but less or equal to 23."
    assert (
        hour_from <= hour_to < 24
    ), "[LOG] AssertionError: hour_to must be greater or equal to hour_from and less than 24."
    df = df[(df["hour"] >= hour_from) & (df["hour"] <= hour_to)]

    # IF_FAULTY
    if delete_if_faulty:
        df = df[df["faulty"] == 0]

    # Assign dates
    if assign_date:
        df["temp"] = df.year.astype("str") + "-" + df.day.astype("str")
        df["date"] = df.temp.apply(
            lambda x: datetime.date(int(x.split("-")[0]) + 2000, 1, 1)
            + datetime.timedelta(int(x.split("-")[1]) - 1)
        )
        df.drop(columns=['temp'], inplace=True)

    # Calculate the number of different vehicles
    if calculate_vehicles:
        df["cars"] = df["vehicle"].apply(lambda x: 1 if x == 1 else 0)
        df["buses"] = df["vehicle"].apply(lambda x: 1 if x == 3 else 0)
        df["trucks"] = df["vehicle"].apply(
            lambda x: 1 if x == 2 or x == 4 or x == 5 or x == 6 or x == 7 else 0
        )

    df.reset_index(drop=True, inplace=True)

    return df
