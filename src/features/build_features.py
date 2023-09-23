"File used to load features into the data."

import pandas as pd


def load_features(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.sort_values("QuoteCreationDateTime", inplace=True)
    data["DaysToFlight"] = (
        data["FlightDate"].dt.date - data["QuoteCreationDateTime"].dt.date
    ) / pd.Timedelta(days=1)
    data["HoursToFlight"] = (
        data["FlightDate"].dt.date - data["QuoteCreationDateTime"].dt.date
    ) / pd.Timedelta(hours=1)

    # # add cumcounts counts
    data["PriorNumberQuoteCount"] = data.groupby("UserID").cumcount()

    # irrelevant column
    data.drop(columns=["QuoteID", "QuoteCreationDateTime", "FlightDate"], inplace=True)

    return data
