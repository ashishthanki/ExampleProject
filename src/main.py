"""Main module."""
import logging
from pathlib import Path

from data.make_dataset import load_data, save_clean_data
from features.analysis import analysis_pipeline
from features.transformations import clean_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()


def main():
    logger.info(f"Running main file.")
    dataset_path = Path().absolute() / "data/raw/AirlineQuotesData.xlsx"
    # load data
    raw_data = load_data(dataset_path, "Flight Duplicate Quotes")

    # explore data - see Jupyter Notebooks in notebooks folder.
    # clean data names
    data = clean_data(raw_data, additional_filter=False)

    # save cleaned data into csv
    output_path = Path().absolute() / "data/processed"
    save_clean_data("cleaned_quote_data", data, output_path)

    analysis_pipeline(data)
    # create train test validation splits
    # train_set, valid_set, test_set = split_data(cleaned)

    # transform data

    # preprocess data and prepare for modelling

    # build models and shortlist best

    # run hyperparameter optimizer

    # fit model again with best_config

    # evaluate model

    # visual best features with Synergy
    return


if __name__ == "__main__":
    main()
