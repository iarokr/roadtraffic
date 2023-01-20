# import dependencies
import pandas as pd
import time
import requests
import datetime
import warnings
import pathlib
import os

from .constant import (
    DEF_COL_NAMES_FINTRAFFIC,
    URL_FINTRAFFIC,
    DEF_FILENAME,
    DEF_FILENAME_U,
)


# Download the .csv report of `tms_id` station for the day `day_of_year`
def read_report(
    tms_id: int,
    year: int,
    day: int,
    direction: int,
    hour_from: int = 6,
    hour_to: int = 20,
    delete_if_faulty: bool = True,
    save: bool = False,
    path_name: str = None,
) -> pd.DataFrame:
    """
    Download the raw data from Fintraffic for the `tms_id` station for the `day` of the `year`. \
    By default the data is cleaned - faulty observations are deleted. \
    Also, the type of vehicle is determined based on the classification from Fintraffic.

    | It is possible to save a `.pkl` file, setting `save` to True. The default filename format "lamraw_TMS_YY_DD_bz2.pkl" is used. 
    | It is possible to locally read a `.pkl` file locally, specifying a `path_name`. \
        At first, the search for the processed files is done. \
        If it is not found, then the unprocessed file is looked up. 
    
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
    direction : int
        Flow direction of interest. Marked as 1 or 2. Check the TMS meta-data to get the necessary direction. 
    hour_from : int, optional
        Hour from which the data is loaded, by default 6
    hour_to : int, optional
        Hour until which the data is loaded (this our is not inclued), by default 20
    delete_if_faulty : bool, optional
        If `True`, observations with the `1` value for the column `if_faulty` will be deleted, by default True
    save : bool, optional
        If specified, saves loaded data in the .pkl file format with bz2-compression with the default filename format "lamraw_TMS_YY_DD_bz2.pkl", by default False
    path_name : str, optional
        If specified, reads data from the `path_name` folder from a locally saved bz2-compressed .pkl file. \
        Both processed "lamraw_TMS_YY_DD_bz2.pkl" and unprocessed "lamraw_TMS_YY_DD_bz2_u.pkl" files can be read, by default None

    Returns
    -------
    pd.DataFrame
        A `pd.DataFrame` with the raw data.

    See Also
    --------
    :func:`~roadtraffic.utils.funcs.date_to_day`
        A function to convert a date into day of the year. 
    """  # noqa E501
    # Initiate timer
    start_time = time.perf_counter()

    # Check assert errors
    # fmt: off
    assert 0 <= hour_from < 24, "Error: the hour_from is incorrect, it should be 0 <= hour_from < 24"  # noqa
    assert 0 < hour_to <= 24, "Error: the hour_to is incorrect, it should be 0 < hour_to <= 24"  # noqa
    assert hour_from < hour_to, "Error: the hour_to should be less than hour_to"  # noqa 
    assert 1 <= day <= 366, "Error: the day is incorrect, it should be 1 < day < 366" # noqa 
    assert 1995 <= year, "Error: the data is available starting from year 1995 only " # noqa
    assert direction == 1 or direction == 2, "Error: direction must be either 1 or 2, check TMS station description" # noqa
    # fmt: on

    # Create column names for the pd.DataFrame
    column_names = DEF_COL_NAMES_FINTRAFFIC

    # Initiate an empty pd.DataFrame
    df = pd.DataFrame()

    # Create the actual filename for processed data
    file_name = DEF_FILENAME

    file_name = (
        file_name.replace("TMS", str(tms_id))
        .replace("YY", str(year)[2:4])
        .replace("DD", str(day))
    )

    # Create the actual filename for unprocessed data
    file_name_u = DEF_FILENAME_U

    file_name_u = (
        file_name_u.replace("TMS", str(tms_id))
        .replace("YY", str(year)[2:4])
        .replace("DD", str(day))
    )

    if path_name is not None:

        # Make a unified location identifyer
        file_path = path_name + "/" + file_name
        file_path = pathlib.Path(file_path)

        file_path_u = path_name + "/" + file_name_u
        file_path_u = pathlib.Path(file_path_u)

        # Check that files exist and load it locally
        if os.path.isfile(file_path):
            df = pd.read_pickle(file_path, compression="bz2")
            f_type = 0
        elif os.path.isfile(file_path_u):
            df = pd.read_pickle(file_path_u, compression="bz2")
            f_type = 1

        if df.empty:
            # Stop timer
            end_time = time.perf_counter()
            print(f"Time spent: {end_time-start_time:0.4f} seconds")
            message = f"Warning: {file_name} or {file_name_u} are not found \
                at {path_name}. An empty pd.DataFrame will be returned."
            warnings.warn(message=message)
            if save is True:
                warnings.warn(
                    "Warning: It is impossible to save a file, as data was not loaded. Check warning above."  # noqa E501
                )
        else:
            if f_type == 1:
                df = _process_initially(
                    df, year, day, direction, hour_from, hour_to, delete_if_faulty # noqa E501
                )

            # Stop timer
            end_time = time.perf_counter()

            if f_type == 0:
                print(
                    f"File {file_name} is loaded. "
                    + f"Time spent: {end_time-start_time:0.4f} sec."  # noqa E501
                )
            else:
                print(
                    f"File {file_name_u} is loaded. "
                    + f"Time spent: {end_time-start_time:0.4f} sec."  # noqa E501
                )

            # Save to .pkl if necessary
            if save is True:
                df.to_pickle(file_name, compression="bz2")
                print(f"Data is successfully saved as {file_name}")

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

        # Check that there is no connection limit
        if r.status_code == 429:
            for i in range(60, 0, -1):
                print(
                    f"Too many requests, waiting {i} seconds to connect again",
                    end="\x1b[1K\r",
                    flush=True,
                )
                time.sleep(1)
            r = requests.get(url)
            if r.status_code == 429:
                print("The server is loaded. Please, try to load the data later.") # noqa E501
            elif r.status_code == 404:
                # Stop timer
                end_time = time.perf_counter()
                print(f"Time spent: {end_time-start_time:0.4f} seconds")
                message = f"Warning: file at {url} does not exist. \
                    Try to select another day. An empty pd.DataFrame will be returned." # noqa E501
                warnings.warn(message=message)
                if save is True:
                    warnings.warn(
                        "Warning: It is impossible to save a file, as data was not loaded. Check warning above."  # noqa E501
                    )
            else:
                with open(file_name[:-4] + ".csv", "wb") as f:
                    f.write(r.content)
                df = pd.read_csv(
                    file_name[:-4] + ".csv",
                    delimiter=";",
                    names=column_names,
                )
                os.remove(file_name[:-4] + ".csv")
                df = _process_initially(
                    df, year, day, direction, hour_from, hour_to, delete_if_faulty # noqa E501
                )

                # Save to .pkl if necessary
                if save is True:
                    df.to_pickle(file_name, compression="bz2")
                    print(f"Data is successfully saved as {file_name}")

        # Try to download the file
        if r.status_code != 404:

            # Download the file from the server
            with open(file_name[:-4] + ".csv", "wb") as f:
                f.write(r.content)
            df = pd.read_csv(
                file_name[:-4] + ".csv",
                delimiter=";",
                names=column_names,
            )
            os.remove(file_name[:-4] + ".csv")
            df = _process_initially(
                df, year, day, direction, hour_from, hour_to, delete_if_faulty
            )

            # Stop timer
            end_time = time.perf_counter()
            print(
                f"Download successful - file for the sensor {tms_id} for the day {day} in year {year} was loaded in {end_time-start_time:0.4f} seconds"  # noqa E501
            )

            # Save to .pkl if necessary
            if save is True:
                df.to_pickle(file_name, compression="bz2")
                print(f"Data is successfully saved as {file_name}")
        else:
            # Stop timer
            end_time = time.perf_counter()
            print(f"Time spent: {end_time-start_time:0.4f} seconds")
            message = f"Warning: file at {url} does not exist. \
                Try to select another day. An empty pd.DataFrame will be returned." # noqa E501
            warnings.warn(message=message)
            if save is True:
                warnings.warn(
                    "Warning: It is impossible to save a file, as data was not loaded. Check warning above."  # noqa E501
                )
    return df


# Donwload .csv reports of `tms_id` station for the `days_list` from Fintraffic
def read_several_reports(
    tms_id: int,
    year_day_list: list,
    direction: int,
    hour_from: int = 6,
    hour_to: int = 20,
    delete_if_faulty: bool = True,
    save: bool = False,
    path_name: str = None,
) -> pd.DataFrame:
    """
    Download the raw data from Fintraffic for the `tms_id` station for the `days_list` of the `year`. \
    Data for each day is loaded separately using :func:`~roadtraffic.utils.load.read_report` and then appended together.
    By default the data is cleaned - faulty observations are deleted. \
    Also, the type of vehicle is determined based on the classification from Fintraffic.

    | It is possible to save a `.pkl` file, setting `save` to True. The default filename format "lamraw_TMS_YY_DD_bz2.pkl" is used. 
    | It is possible to locally read a `.pkl` file locally, specifying a `path_name`. \
        At first, the search for the processed files is done. \
        If it is not found, then the unprocessed file is looked up. 

    Parameters
    ----------
    tms_id : int
        The identity number of a traffic measurement station (TMS). \
        Meta-data about TMS is available `here <https://www.digitraffic.fi/en/road-traffic/#current-data-from-tms-stations>`_.
    year_day_list : list
        A list of days in the format `[[year1, day1], [year2, day2],...]`
    direction : int
        low direction of interest. Marked as 1 or 2. Check the TMS meta-data to get the necessary direction. 
    hour_from : int, optional
        Hour from which the data is loaded, by default 6
    hour_to : int, optional
        Hour until which the data is loaded (this our is not inclued), by default 20
    delete_if_faulty : bool, optional
        If `True`, observations with the `1` value for the column `if_faulty` will be deleted, by default True
    save : bool, optional
        If specified, saves loaded data in the .pkl file format with bz2-compression with the default filename format "lamraw_TMS_YY_DD_bz2.pkl", by default False
    path_name : str, optional
        If specified, reads data from the `path_name` folder from a locally saved bz2-compressed .pkl file. \
        Both processed "lamraw_TMS_YY_DD_bz2.pkl" and unprocessed "lamraw_TMS_YY_DD_bz2_u.pkl" files can be read, by default None

    Returns
    -------
    pd.DataFrame
        A `pd.DataFrame` with loaded data

    See Also
    --------
    :func:`~roadtraffic.utils.load.read_report`
    """  # noqa E501
    # Initiate timer
    start_time = time.perf_counter()

    # Initiate counter
    counter = 0

    # Initiate an empty the pd.DataFrame
    df = pd.DataFrame()

    # Check assert errors
    # fmt: off
    assert 0 <= hour_from < 24, "Error: the hour_from is incorrect, it should be 0 <= hour_from < 24"  # noqa
    assert 0 < hour_to <= 24, "Error: the hour_to is incorrect, it should be 0 < hour_to <= 24"  # noqa
    assert hour_from < hour_to, "Error: the hour_to should be less than hour_to"  # noqa 
    assert direction == 1 or direction == 2, "Error: direction must be either 1 or 2, check TMS station description" # noqa
    # fmt: on

    # Interate through each day
    for count, value in enumerate(year_day_list):
        # Initiate loaded pd.DataFrame
        read_df = pd.DataFrame()

        if df.empty:
            read_df = read_report(
                tms_id,
                value[0],
                value[1],
                direction,
                hour_from,
                hour_to,
                delete_if_faulty,
                save=save,
                path_name=path_name,
            )
            if read_df.empty is False:
                df = read_df
                counter += 1
        else:
            read_df = read_report(
                tms_id,
                value[0],
                value[1],
                direction,
                hour_from,
                hour_to,
                delete_if_faulty,
                save=save,
                path_name=path_name,
            )
            if read_df.empty is False:
                df = pd.concat((df, read_df), ignore_index=True)
                counter += 1
    # Check that some data was loaded
    assert df.empty is False, "Error: Data was not loaded, check the input given." # noqa E501

    # Stop timer
    end_time = time.perf_counter()

    # Confirm the result
    print(
        f"Loading sucessful: {counter} out of {len(year_day_list)} files loaded in {end_time-start_time:0.4f} seconds"  # noqa E521
    )

    # Save to .pkl if necessary
    if save is True:
        df.to_pickle("data.pkl", compression="bz2")
        print("Data is successfully saved")

    return df


def read_pkl(filepath: str) -> pd.DataFrame:
    """
    Reads a BZ2-compressed .pkl file containing raw data from Fintraffic, which was previously loaded.

    Parameters
    ----------
    filepath : str
        A string, which contains a path to the .pkl file.

    Returns
    -------
    pd.DataFrame
        A `pd.DataFrame` with loaded data

    Raises
    ------
    Exception
        Incorrect path provided or the file is empty.
    """  # noqa E501
    # Initialize timer
    start_time = time.perf_counter()

    # Initiation message
    print(f"Trying to load data locally from {filepath} ...")

    # Initialize pd.DataFrame
    df = pd.DataFrame()

    # Check assert errors
    # fmt: off
    assert filepath.lower().endswith('.pkl'), "Error: Wrong file format or a file is not found. Please, provide a valid .pkl file." # noqa E521
    # fmt: on

    # Make a unified location identifyer
    filepath = pathlib.Path(filepath)

    # Load a file locally
    if (os.path.exists(filepath) is True) and (os.path.getsize(filepath) != 0):
        df = pd.read_pickle(filepath, compression="bz2")
    else:
        warnings.warn(
            "File is empty or it does not exist at the given filepath. Please, check the file or the filepath."  # noqa E521
        )
        df = pd.DataFrame()

    # Stop the timer
    end_time = time.perf_counter()

    # Confirm the result
    print(
        f"Loading completed: the file was loaded in {end_time-start_time:0.4f} seconds"  # noqa E521
    )

    return df


def _process_initially(
    df: pd.DataFrame,
    year: int,
    day: int,
    direction: int,
    hour_from: int = 6,
    hour_to: int = 20,
    delete_if_faulty: bool = True,
) -> pd.DataFrame:
    """Takes unprocessed raw Fintraffic data and makes initial processing.

    Parameters
    ----------
    df : pd.DataFrame
        Unprocessed raw Fintraffic data.
    year : int
        The year data was collected in the 4-digit format. Data is available starting from 1995 only. 
    day : int
        The day of the year the data was collected. \
        The day is provide as an integer in range(1, 366), with 1 - January 1st, \
        365 (366 in leap year) - December 31st. \
        To caclulate the day of the year from a date you can use `roadtraffic.utils.funcs.date_to_day()` function.
    direction : int
        Flow direction of interest. Marked as 1 or 2. Check the TMS meta-data to get the necessary direction.
    hour_from : int, optional
        Hour from which the data is loaded, by default 6
    hour_to : int, optional
        Hour until which the data is loaded (this our is not inclued), by default 20
    delete_if_faulty : bool, optional
        If `True`, observations with the `1` value for the column `if_faulty` will be deleted, by default True

    Returns
    -------
    pd.DataFrame
        Processed raw Fintraffic data.
    """  # noqa E501
    # Assign dates
    df["date"] = datetime.date(year, 1, 1) + datetime.timedelta(day - 1)

    # Calculate the number of different vehicles
    df["cars"] = df["vehicle"].apply(lambda x: 1 if x == 1 else 0)
    df["buses"] = df["vehicle"].apply(lambda x: 1 if x == 3 else 0)
    df["trucks"] = df["vehicle"].apply(
        lambda x: 1 if x == 2 or x == 4 or x == 5 or x == 6 or x == 7 else 0
    )

    # Delete faulty data point
    if delete_if_faulty is True:
        df = df[df.faulty != 1]

    # Select data only from the specified timeframe
    df = df[df.total_time >= hour_from * 60 * 60 * 100]
    df = df[df.total_time <= hour_to * 60 * 60 * 100]

    # Filter the correct direction
    df = df[df.direction == direction]

    return df
