import pandas as pd
import analytics_check


def test_run_incorrect_check():
    test_dataset1 = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    errlist = analytics_check.run_check(test_dataset1)
    assert len(errlist) == 5, "Wrong input provided"


def test_run_correct_file_check():
    data = pd.read_csv("test_correct_data.csv")
    errlist = analytics_check.run_check(data)
    assert len(errlist) == 0, "No errors expected from the csv"


def test_run_incorrect_file_check():
    data = pd.read_csv("test_incorrect_data.csv")
    errlist = analytics_check.run_check(data)
    assert len(errlist) == 1, "1 error expected from this"
