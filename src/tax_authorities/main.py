import os
import re
import subprocess
import sys
from pathlib import Path

import FreeSimpleGUI as sg
import pandas as pd

from tax_authorities.download import download_dataset, get_data_dir

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILENAMES = {
    'cases': 'cases.parquet',
    'rev_ruls': 'rev_ruls.parquet',
    'plrs': 'plrs.parquet',
}


def get_parquet_path(name):
    filename = FILENAMES[name]
    local_path = PROJECT_ROOT / filename

    if local_path.exists():
        return local_path
    return get_data_dir() / name / filename


def get_output_dir():
    output_dir = get_data_dir() / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def show_download_popup():
    layout = [[sg.Text('Downloading tax law data. This happens once and may take a few minutes...')]]
    window = sg.Window('Please wait', layout, finalize=True)
    window.read(timeout=0)
    return window


def load_dataframes():
    missing = [name for name in FILENAMES if not get_parquet_path(name).exists()]

    if missing:
        popup = show_download_popup()
        try:
            for name in missing:
                download_dataset(name)
        except Exception as e:
            sg.popup_error(f'Failed to download data:\n\n{e}')
            raise FileNotFoundError from e
        finally:
            popup.close()

    paths = {name: get_parquet_path(name) for name in FILENAMES}

    for name, path in paths.items():
        if not path.exists():
            sg.popup_error(f'Could not find parquet file:\n\n{path}')
            raise FileNotFoundError(path)

    return (
        pd.read_parquet(paths['cases']),
        pd.read_parquet(paths['rev_ruls']),
        pd.read_parquet(paths['plrs']),
    )


def write_results(results):
    results_path = get_output_dir() / 'results.txt'
    results_path.write_text(''.join(results), encoding='utf-8')
    if sys.platform == 'win32':
        os.startfile(results_path.resolve())
    elif sys.platform == 'darwin':
        subprocess.run(['open', results_path.resolve()])
    else:  # Linux
        subprocess.run(['xdg-open', results_path.resolve()])


def search_cases(df_cases, results, pattern, included, excluded):
    # iterate through the rows
    for _, row in df_cases.iterrows():
        # read the text and make it lowercase
        text = str(row['text']).lower()

        # skip if all search terms are not found
        if not all(item in text for item in included):
            continue

        # skip if any excluded search terms are found
        if any(item in text for item in excluded):
            continue

        # find matches
        match = pattern.search(text)

        # if there is a match, create an item to append to results
        if match:
            year = row['year']
            month = row['month']
            day = row['day']
            opinion_type = row['opinion_type']
            opinion_name = row['opinion_name']
            num_pages = row['num_pages']
            docket_num = row['docket_number']
            judge = row['judge_name']
            match = match.group()
            results.append(
                f'    Date: {year}-{month}-{day}, Opinion Type: {opinion_type}, Number of Pages: {num_pages}, Docket No.:{docket_num}, Judge: {judge}\n    Taxpayer Name: {opinion_name}\n{match}\n\n'
            )
    return results


def search_rrs(df_rrs, results, pattern, included, excluded):
    # iterate through the rows
    for _, row in df_rrs.iterrows():
        # read the text and make it lowercase
        text = str(row['text']).lower()

        # skip if all search terms are not found
        if not all(item in text for item in included):
            continue

        # skip if any excluded search terms are found
        if any(item in text for item in excluded):
            continue

        # find matches
        match = pattern.search(text)

        # if there is a match, create an item to append to results
        if match:
            ruling_type = row['ruling_type']
            ruling_year = row['ruling_year']
            ruling_number = row['ruling_number']
            match = match.group()
            results.append(f'    {ruling_type} {ruling_year}-{ruling_number}\n{match}\n\n')
    return results


def search_plrs(df_plrs, results, pattern, included, excluded):
    # iterate through the rows
    for _, row in df_plrs.iterrows():
        # read the text and make it lowercase
        text = str(row['text']).lower()

        # skip if all search terms are not found
        if not all(item in text for item in included):
            continue

        # skip if any excluded search terms are found
        if any(item in text for item in excluded):
            continue

        # find matches
        match = pattern.search(text)

        # if there is a match, create an item to append to results
        if match:
            written_determination_number = row['wd_number']
            match = match.group()
            results.append(f'    Written Determination Number: {written_determination_number}\n{match}\n\n')
    return results


def text_search(df_cases, df_rrs, df_plrs, text_to_search_for, num_before_chars, num_after_chars, include_cases, include_rev_ruls, include_plrs):
    # separate the arguments by whitespace, but keep strings in quotes as a single item
    all_items = re.findall(r'"(.*?)"|(\S+)', text_to_search_for)

    # flatten the tuple and remove any None values
    all_items = [item for sublist in all_items for item in sublist if item]

    # make all search terms lowercase
    all_items = [item.lower() for item in all_items]

    # generate a popup if search is clicked but no items were typed in
    if not all_items:
        sg.popup_error('Please enter search terms.')
        return

    # get the first item so that you know what to center on
    first_item = all_items[0]

    # if the first item includes regex characters, they need to be escaped
    # for example, 162(a) will not return any results unless it is escaped
    escaped_first_item = re.escape(first_item)

    # create the pattern to be searched for
    try:
        pattern = re.compile(rf'.{{{num_before_chars}}}{escaped_first_item}.{{{num_after_chars}}}', flags=re.DOTALL | re.IGNORECASE)
    except re.error as e:
        sg.popup_error(f'Invalid regex:\n\n{e}')
        return

    # create list of terms to find
    included = [item for item in all_items if not item.startswith('-')]

    # create list of terms to exclude
    excluded = [item[1:] for item in all_items if item.startswith('-')]

    # create a new list to be populated
    results = []

    # search cases, rrs, and plrs
    if include_cases:
        results = search_cases(df_cases, results, pattern, included, excluded)
    if include_rev_ruls:
        results = search_rrs(df_rrs, results, pattern, included, excluded)
    if include_plrs:
        results = search_plrs(df_plrs, results, pattern, included, excluded)

    results.insert(0, f'[Non-regex] Search Term(s): {text_to_search_for}\n\nNumber of documents found: {len(results)}\n\n')

    write_results(results)


def regex_search(df_cases, df_rrs, df_plrs, pattern, num_before_chars, num_after_chars, include_cases, include_rev_ruls, include_plrs):
    try:
        compiled_pattern = re.compile(rf'.{{{num_before_chars}}}{pattern}.{{{num_after_chars}}}', flags=re.DOTALL | re.IGNORECASE)
    except re.error as e:
        sg.popup_error(f'Invalid regex:\n\n{e}')
        return

    results = []

    if include_cases:
        for _, row in df_cases.iterrows():
            text = str(row['text'])
            match = compiled_pattern.search(text)

            # if there is a match, create an item to append to results
            if match:
                year = row['year']
                month = row['month']
                day = row['day']
                opinion_type = row['opinion_type']
                opinion_name = row['opinion_name']
                num_pages = row['num_pages']
                docket_num = row['docket_number']
                judge = row['judge_name']
                match = match.group()
                results.append(
                    f'    Date: {year}-{month}-{day}, Opinion Type: {opinion_type}, Number of Pages: {num_pages}, Docket No.:{docket_num}, Judge: {judge}\n    Taxpayer Name: {opinion_name}\n{match}\n\n'
                )

    if include_rev_ruls:
        for _, row in df_rrs.iterrows():
            text = str(row['text'])
            match = compiled_pattern.search(text)

            # if there is a match, create an item to append to results
            if match:
                ruling_type = row['ruling_type']
                ruling_year = row['ruling_year']
                ruling_number = row['ruling_number']
                match = match.group()
                results.append(f'    {ruling_type} {ruling_year}-{ruling_number}\n{match}\n\n')

    if include_plrs:
        for _, row in df_plrs.iterrows():
            text = str(row['text'])
            match = compiled_pattern.search(text)

            # if there is a match, create an item to append to results
            if match:
                written_determination_number = row['wd_number']
                match = match.group()
                results.append(f'    Written Determination Number: {written_determination_number}\n{match}\n\n')

    results.insert(0, f'Regex Pattern: {pattern}\n\nNumber of documents found: {len(results)}\n\n')
    write_results(results)


def main():
    try:
        df_cases, df_rrs, df_plrs = load_dataframes()
    except FileNotFoundError:
        return

    layout = [
        [sg.Text('Enter text in one of the two input fields below.')],
        [sg.Text('Search:', font=18, text_color='black')],
        [
            sg.Text('Search Term(s):'),
            sg.Input(key='text_to_search_for', size=(30, 1), default_text='', background_color='lightpink'),
            sg.Checkbox('Tax Court Opinions', default=True, key='include_cases'),
            sg.Checkbox('Revenue Rulings', default=True, key='include_rev_ruls'),
            sg.Checkbox('Private Letter Rulings', default=True, key='include_plrs'),
        ],
        [
            sg.Multiline(
                """    Items containing all search terms will be found.
    The text will be centered on the first term.
    Use quotes to search for multiple words in sequence.
    Use "-" to exclude terms, but don't use a dash before quoted text.
    Uppercase vs. lowercase is ignored.
    Tax Court Opinions are from 1997 to the present.
    Revenue Rulings also includes Notices, Announcements, and Revenue Procedures, from 1998 to the present.
    Private Letter Rulings includes IRS written determinations (PLRs, CCAs, TAMs, etc.) from 1999 to the present.
        """,
                size=(90, 8),
                disabled=True,
                no_scrollbar=True,
            )
        ],
        [
            sg.Text('Number of characters before search term(s):'),
            sg.Input(key='num_before_chars', size=(6, 1), default_text='300', background_color='lightpink'),
        ],
        [
            sg.Text('Number of characters after search term(s):'),
            sg.Input(key='num_after_chars', size=(6, 1), default_text='300', background_color='lightpink'),
        ],
        [sg.Text('')],
        [sg.Text('Regular Expression Search:', font=18, text_color='black')],
        [
            sg.Text('Regex Pattern:'),
            sg.Input(key='regex_pattern', size=(30, 1), default_text='', background_color='lightpink'),
        ],
        [sg.Text('After entering the terms, press enter or click on the Search button.', font=('Arial', 12, 'bold'), text_color='orange')],
        [
            sg.Button('Search'),
            sg.Button('Cancel'),
        ],
        [sg.Text('Andrew Mitchel LLC, Copyright (c) 2026', font=('Arial', 12, 'bold'), text_color='black')],
    ]

    window = sg.Window('Tax Authorities Search', layout, return_keyboard_events=True, finalize=True)
    window['text_to_search_for'].set_focus()

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, 'Cancel', 'Escape:27'):
            window.close()
            break

        if values['regex_pattern'] and values['text_to_search_for']:
            sg.popup_error('Use only one search type.')
            continue

        try:
            num_before_chars = int(values['num_before_chars'])
            num_after_chars = int(values['num_after_chars'])
        except ValueError:
            sg.popup_error('Character counts must be integers.')
            continue

        if event in ('Search', '\r') and values['text_to_search_for']:
            text_search(
                df_cases,
                df_rrs,
                df_plrs,
                values['text_to_search_for'],
                num_before_chars,
                num_after_chars,
                values['include_cases'],
                values['include_rev_ruls'],
                values['include_plrs'],
            )
            break

        if event in ('Search', '\r') and values['regex_pattern']:
            regex_search(
                df_cases,
                df_rrs,
                df_plrs,
                values['regex_pattern'],
                num_before_chars,
                num_after_chars,
                values['include_cases'],
                values['include_rev_ruls'],
                values['include_plrs'],
            )
            break

    window.close()


if __name__ == '__main__':
    main()
