"File that prints out all userful information and saves visualizations."
import logging

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme()

logger = logging.getLogger(__name__)


def close_rate(data: pd.DataFrame) -> float:
    """Return close rate value.

    Args:
        data (pd.DataFrame): Quotes data that contains a binary Sale_Flag column.

    Returns:
        float: Close Rate value.
    """
    close_rate_val = data.Sale_Flag.value_counts(normalize=True).loc[1]

    sale_value_count = data.Sale_Flag.value_counts()
    sale_no = sale_value_count.loc[1]
    quote_no = sale_value_count.loc[0]

    msg = (
        f"Calculated close rate was: {close_rate_val: .1%}. "
        f"#Sales {sale_no} and #Quotes {quote_no}. "
        f"Total Rows: {sale_no + quote_no}."
    )
    logger.info(f"{msg}")
    return close_rate_val


def plot_close_ratio_over_months(data: pd.DataFrame, feature: str, title: str) -> None:
    temp = data.copy()
    temp["Month"] = temp[feature].dt.month
    temp = (
        temp[["Month", "Sale_Flag"]]
        .groupby(["Month", "Sale_Flag"], as_index=False)
        .size()
    )

    temp = pd.pivot_table(temp, values=["size"], index=["Month"], columns=["Sale_Flag"])

    temp["Close_Ratio"] = temp["size"][1] / (temp["size"][0] + temp["size"][1])
    temp["Close_Ratio"].plot(kind="line")
    plt.title(f"{title}: {feature}")
    plt.show()


def analysis_pipeline(data: pd.DataFrame) -> None:
    close_rate(data)
