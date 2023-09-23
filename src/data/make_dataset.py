"File to create a pandas DataFrame from raw data file."
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger()


def load_data(file: Path, sheet_name: str) -> pd.DataFrame:
    """Loads raw flight quote data

    Args:
        file (Path): Path to raw data file. Defaults to "data/raw/data.csv".

    Raises:
        FileNotFoundError: Raises error if file not found in directory. Pull data from kaggle site.

    Returns:
        pd.DataFrame: DataFrame object of flight quote data.
    """
    logger.info(f"Reading data from {file}.")
    # raise error if file does not exist
    if not Path(file).exists():
        raise FileNotFoundError
    return pd.read_excel(
        Path(file),
        sheet_name=sheet_name,
        parse_dates=["QuoteCreationDateTime", "FlightDate"],
        dtype={"QuoteID": "category", "UserID": "category"},
    )


def save_clean_data(name: str, data: pd.DataFrame, path: Path) -> None:
    logger.info(f"Attempting to save data to {path}.")
    # raise error if file does not exist
    if not Path(path).exists():
        raise NotADirectoryError
    file_path = path / Path(name)
    data.to_csv(f"{file_path}.csv", index=False)
    logger.info(f"Saved data to {file_path}.csv")
    return
