import re

from tax_authorities.main import search_cases, search_plrs, search_rrs


def make_pattern(term, before=5, after=5):
    return re.compile(rf'.{{{before}}}{re.escape(term)}.{{{after}}}', flags=re.DOTALL | re.IGNORECASE)


def test_search_cases_matches_and_formats_result(cases_df):
    pattern = make_pattern('innocent spouse')

    results = search_cases(cases_df, [], pattern, ['innocent'], [])

    assert len(results) == 1
    assert 'Smith v. Commissioner' in results[0]
    assert 'Judge A' in results[0]
    assert 'Docket No.:123-20' in results[0]


def test_search_cases_excluded_term_skips_row(cases_df):
    pattern = make_pattern('opinion')

    results = search_cases(cases_df, [], pattern, ['opinion'], ['unrelated'])

    assert len(results) == 1
    assert 'Smith v. Commissioner' in results[0]


def test_search_rrs_formats_ruling_type_year_number(rev_ruls_df):
    pattern = make_pattern('innocent spouse')

    results = search_rrs(rev_ruls_df, [], pattern, ['innocent'], [])

    assert len(results) == 1
    assert 'Rev. Rul. 2019-12' in results[0]


def test_search_plrs_formats_wd_number(plrs_df):
    pattern = make_pattern('innocent spouse')

    results = search_plrs(plrs_df, [], pattern, ['innocent'], [])

    assert len(results) == 1
    assert 'Written Determination Number: 201901001' in results[0]


def test_quoted_phrase_tokenization():
    all_items = re.findall(r'"(.*?)"|(\S+)', 'section 162(a) "ordinary and necessary" -fraud')
    all_items = [item for sublist in all_items for item in sublist if item]

    assert all_items == ['section', '162(a)', 'ordinary and necessary', '-fraud']


def test_included_excluded_split():
    all_items = ['section', '162(a)', 'ordinary and necessary', '-fraud']

    included = [item for item in all_items if not item.startswith('-')]
    excluded = [item[1:] for item in all_items if item.startswith('-')]

    assert included == ['section', '162(a)', 'ordinary and necessary']
    assert excluded == ['fraud']


def test_regex_escape_for_term_search():
    assert re.escape('162(a)') == '162\\(a\\)'
