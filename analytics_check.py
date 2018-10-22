import pandas as pd


def run_check(data):
    assert isinstance(
        data, pd.DataFrame), "Expected data to be a pandas dataframe"
    errors = []

    # Number of rows is more than 0
    data_shape = data.shape
    if data_shape[0] <= 0:
        errors.append("Empty dataset")

    # Column check
    expected_keys = ["id", "data", "source", "target", "state"]
    columns = data.columns
    for key in expected_keys:
        if key not in columns:
            errors.append("{} column is missing".format(key))

    return errors
