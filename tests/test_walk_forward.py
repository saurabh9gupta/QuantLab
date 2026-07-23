import pandas as pd


def test_walk_forward_train_test_periods_do_not_overlap():
    """
    Walk-forward training and testing windows must not overlap.

    The test period must begin on or after the end of the
    corresponding training period.
    """

    parameter_history = pd.DataFrame(
        {
            "Train Start": [
                "2000-01-03",
                "2001-01-03",
                "2002-01-03",
            ],
            "Train End": [
                "2005-01-03",
                "2006-01-03",
                "2007-01-03",
            ],
            "Test Start": [
                "2005-01-03",
                "2006-01-03",
                "2007-01-03",
            ],
            "Test End": [
                "2006-01-03",
                "2007-01-03",
                "2008-01-03",
            ],
        }
    )

    for column in [
        "Train Start",
        "Train End",
        "Test Start",
        "Test End",
    ]:
        parameter_history[column] = pd.to_datetime(
            parameter_history[column]
        )

    assert (
        parameter_history["Test Start"]
        >= parameter_history["Train End"]
    ).all()

    assert (
        parameter_history["Test End"]
        > parameter_history["Test Start"]
    ).all()

    assert (
        parameter_history["Train End"]
        > parameter_history["Train Start"]
    ).all()