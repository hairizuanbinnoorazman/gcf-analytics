import pandas as pd
import analytics_check

def test_run_check():
    test_dataset1 = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    errlist = analytics_check.run_check(test_dataset1)
    assert len(errlist) == 5, "Wrong input provided"