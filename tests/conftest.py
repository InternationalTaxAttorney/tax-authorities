import pandas as pd
import pytest


@pytest.fixture
def cases_df():
    return pd.DataFrame(
        [
            {
                'filename': 'case1.pdf',
                'year': 2020,
                'month': 1,
                'day': 5,
                'opinion_type': 'T.C. Memo',
                'opinion_name': 'Smith v. Commissioner',
                'num_pages': 10,
                'docket_number': '123-20',
                'judge_name': 'Judge A',
                'text': 'this opinion discusses innocent spouse relief in detail',
            },
            {
                'filename': 'case2.pdf',
                'year': 2021,
                'month': 2,
                'day': 6,
                'opinion_type': 'T.C. Memo',
                'opinion_name': 'Jones v. Commissioner',
                'num_pages': 8,
                'docket_number': '456-21',
                'judge_name': 'Judge B',
                'text': 'this opinion is about something unrelated',
            },
        ]
    )


@pytest.fixture
def rev_ruls_df():
    return pd.DataFrame(
        [
            {
                'ruling_type': 'Rev. Rul.',
                'ruling_year': 2019,
                'ruling_number': '12',
                'text': 'this ruling addresses innocent spouse relief',
            },
            {
                'ruling_type': 'Rev. Rul.',
                'ruling_year': 2020,
                'ruling_number': '5',
                'text': 'this ruling is unrelated',
            },
        ]
    )


@pytest.fixture
def plrs_df():
    return pd.DataFrame(
        [
            {'wd_number': '201901001', 'text': 'this letter ruling discusses innocent spouse relief'},
            {'wd_number': '202005002', 'text': 'this letter ruling is unrelated'},
        ]
    )
