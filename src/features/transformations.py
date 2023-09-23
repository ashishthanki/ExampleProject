"All Transformations in a single file."
import logging

import pandas as pd
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

flight_date_window_size = 28


def calculate_flight_delta(data: pd.DataFrame) -> pd.Series:
    return (data.FlightDate.diff().abs() / pd.Timedelta(days=1)).fillna(0.0)


def criteria_filter(group: pd.core.groupby.GroupBy) -> pd.DataFrame:
    # if there are sales in the group then return sales.
    if (group.Sale_Flag == 1).any():
        filtered_data = group[group.Sale_Flag == 1]

    # if entire group has no sale then return latest quote
    elif (group.Sale_Flag == 0).all():
        filtered_data = group[
            group.QuoteCreationDateTime == group.QuoteCreationDateTime.max()
        ]
        # handle USER_130, multiple quotes exactly same time
        if filtered_data.shape[0] > 1:
            filtered_data = filtered_data.tail(1)
    else:
        return None
    logger.info(
        f"Filtering for User ID: {filtered_data.UserID.unique()[0]} "
        f"Group: {filtered_data.QuoteGroup.unique()[0]}."
    )
    return filtered_data


def deduplicate(data: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate based on analyst criteria.

    Args:
        raw_data (pd.DataFrame): Userid group data.

    Returns:
        pd.DataFrame: Returns deduplicated data.
    """
    # for each group calculate the flight date delta from previous search
    logger.info(f"Data contains {data.shape[0]} rows before deduplication.")
    if data.QuoteID.value_counts().max() != 1:
        raise ValueError("There are duplicate quote IDs, check file.")

    # given that quote ID is not a duplicate, if all other rows are duplicates then
    # they should be removed too
    data.drop_duplicates(
        keep="last",
        subset=["UserID", "QuoteCreationDateTime", "FlightDate", "Price", "Sale_Flag"],
        inplace=True,
    )

    quote_id_to_keep = []
    for user_id in data.UserID.unique():
        logger.info(f"Deduplicating User ID: {user_id}.")

        user_data = data.loc[data["UserID"] == user_id].copy()

        # sort by flight date then quote creation
        user_data.sort_values(["FlightDate", "QuoteCreationDateTime"], inplace=True)

        # calculate the difference between flight dates rows
        user_data["FlightDateDelta"] = calculate_flight_delta(user_data)

        # get mask of quotes within window size
        flight_date_window_size_mask = (
            user_data["FlightDateDelta"] <= flight_date_window_size
        )

        # group window sized flight dates together
        user_data["QuoteGroup"] = user_data.groupby(
            (~flight_date_window_size_mask).cumsum()
        ).ngroup()

        deduplicated_user_quotes = user_data.groupby(["QuoteGroup"]).apply(
            criteria_filter
        )
        quote_id_to_keep.extend(deduplicated_user_quotes.QuoteID.tolist())

    # raise error if there are duplicate quotes being filtered
    if len(quote_id_to_keep) != len(set(quote_id_to_keep)):
        raise ValueError("There are duplicates quote IDs, check file.")

    deduplicate_data = data[data["QuoteID"].isin(quote_id_to_keep)]
    removed_quote_ids = data.loc[
        ~data["QuoteID"].isin(quote_id_to_keep), "QuoteID"
    ].tolist()

    logger.info(f"Data contains {deduplicate_data.shape[0]} rows after deduplication.")
    logger.info(f"Removed {len(removed_quote_ids)} quote IDs.")

    return deduplicate_data


def additional_deduplication(data: pd.DataFrame) -> pd.DataFrame:
    """This function is created to further filter the dataframe.

    Args:
        data (pd.DataFrame): Input quote data before deduplication filter.

    Returns:
        pd.DataFrame: Filtered data outside of scope.
    """
    logger.info("Performing additional filtering.")
    # remove quotes that are after the flight dates.
    data = data[data.QuoteCreationDateTime.dt.date <= data.FlightDate]

    # keep quotes that are within the 99th percentile.
    data = data[data.Price <= data.Price.quantile(0.90)]
    return data


def clean_data(raw_data: pd.DataFrame, additional_filter: bool = False) -> pd.DataFrame:
    """Filters data based on analyst criteria.

    Args:
        raw_data (pd.DataFrame): Raw data as loaded from excel file.

    Returns:
        pd.DataFrame: Returns filtered data.
    """
    # check data is clean
    assert raw_data.UserID.str.match(r"^USER_\d+$").all()
    assert raw_data.QuoteID.str.match(r"^QUOTE_\d+$").all()
    # sort by quote creation date time
    transformed_data = raw_data.sort_values(
        ["UserID", "QuoteCreationDateTime"], ascending=True
    )

    if additional_filter:
        transformed_data = additional_deduplication(transformed_data)

    # deduplicate data based on criteria
    deduplicated_data = deduplicate(transformed_data)

    # check data and raise error
    for user_id in raw_data.UserID.unique():
        if additional_filter:
            break
        if not deduplicated_data.UserID.isin([user_id]).any():
            raise ValueError(f"Error in cleaned data for User ID {user_id}.")

    logger.info("All User IDs are present in cleaned data.")

    # return in quote ID order
    return deduplicated_data.sort_values("QuoteID", ascending=True)


def split_data(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_set, val_test_set = train_test_split(data, random_state=42, test_size=0.4)
    valid_set, test_set = train_test_split(val_test_set, random_state=42, test_size=0.2)
    return train_set, valid_set, test_set
