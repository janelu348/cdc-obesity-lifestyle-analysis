import argparse
from pathlib import Path

import pandas as pd


YEARS = [2017, 2019, 2021]

STATE_ABBREVIATIONS = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE",
    "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
    "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
    "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC"
]

QUESTION_TO_COLUMN = {
    "Percent of adults aged 18 years and older who have obesity":
        "obesity_pct",

    "Percent of adults who engage in no leisure-time physical activity":
        "no_leisure_activity_pct",

    "Percent of adults who report consuming fruit less than one time daily":
        "low_fruit_consumption_pct"
}


def create_wide_table(data, index_columns):
    """Reshape the three selected questions into columns."""

    wide_data = (
        data.pivot_table(
            index=index_columns,
            columns="metric",
            values="Data_Value",
            aggfunc="first"
        )
        .dropna(
            subset=list(QUESTION_TO_COLUMN.values())
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    return wide_data


def prepare_data(input_file, output_directory):
    """Create the model and demographic datasets."""

    input_file = Path(input_file)
    output_directory = Path(output_directory)

    if not input_file.exists():
        raise FileNotFoundError(
            f"Original CSV was not found: {input_file}"
        )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # Load the original CDC CSV
    df = pd.read_csv(
        input_file,
        low_memory=False
    )

    required_columns = {
        "YearStart",
        "LocationAbbr",
        "LocationDesc",
        "Question",
        "Data_Value",
        "StratificationCategory1",
        "Stratification1"
    }

    missing_columns = required_columns.difference(
        df.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing columns: {sorted(missing_columns)}"
        )

    # Select the years, states, and questions
    selected_data = df[
        df["YearStart"].isin(YEARS)
        & df["LocationAbbr"].isin(STATE_ABBREVIATIONS)
        & df["Question"].isin(QUESTION_TO_COLUMN)
    ].copy()

    # Create shorter variable names
    selected_data["metric"] = selected_data[
        "Question"
    ].map(QUESTION_TO_COLUMN)

    # Convert the estimates to numbers
    selected_data["Data_Value"] = pd.to_numeric(
        selected_data["Data_Value"],
        errors="coerce"
    )

    # Create the state-year modeling data
    total_data = selected_data[
        selected_data["StratificationCategory1"] == "Total"
    ].copy()

    model_data = create_wide_table(
        total_data,
        [
            "LocationDesc",
            "LocationAbbr",
            "YearStart"
        ]
    )

    model_data = model_data.rename(
        columns={
            "LocationDesc": "state",
            "LocationAbbr": "state_abbr",
            "YearStart": "year"
        }
    )

    model_data = model_data[
        [
            "state",
            "state_abbr",
            "year",
            "obesity_pct",
            "no_leisure_activity_pct",
            "low_fruit_consumption_pct"
        ]
    ].sort_values(
        ["year", "state"]
    ).reset_index(drop=True)

    # Create the demographic dataset
    demographic_data = create_wide_table(
        selected_data,
        [
            "LocationDesc",
            "LocationAbbr",
            "YearStart",
            "StratificationCategory1",
            "Stratification1"
        ]
    )

    demographic_data = demographic_data.rename(
        columns={
            "LocationDesc": "state",
            "LocationAbbr": "state_abbr",
            "YearStart": "year",
            "StratificationCategory1":
                "stratification_category",
            "Stratification1": "stratification"
        }
    )

    demographic_data = demographic_data[
        [
            "state",
            "state_abbr",
            "year",
            "stratification_category",
            "stratification",
            "obesity_pct",
            "no_leisure_activity_pct",
            "low_fruit_consumption_pct"
        ]
    ].sort_values(
        [
            "year",
            "state",
            "stratification_category",
            "stratification"
        ]
    ).reset_index(drop=True)

    # Save the prepared files
    model_output = (
        output_directory
        / "obesity_lifestyle_model_data.csv"
    )

    demographic_output = (
        output_directory
        / "obesity_lifestyle_demographic_data.csv"
    )

    model_data.to_csv(
        model_output,
        index=False
    )

    demographic_data.to_csv(
        demographic_output,
        index=False
    )

    print("Data preparation completed.")
    print("Model data shape:", model_data.shape)
    print(
        "Demographic data shape:",
        demographic_data.shape
    )
    print("Model data saved to:", model_output)
    print(
        "Demographic data saved to:",
        demographic_output
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare the CDC obesity project data."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the original CDC CSV file."
    )

    parser.add_argument(
        "--output-dir",
        default="data",
        help="Folder for the prepared CSV files."
    )

    arguments = parser.parse_args()

    prepare_data(
        arguments.input,
        arguments.output_dir
    )
