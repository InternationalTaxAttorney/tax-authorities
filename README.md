# Tax Authorities

A small desktop GUI for searching the full text of U.S. Tax Court opinions, IRS revenue rulings (also covering Notices, Announcements, and Revenue Procedures), and IRS private letter rulings / written determinations — no coding required.

## Features
- Search across all three datasets at once, or toggle any combination off with checkboxes
- Plain-text search supports multiple terms (AND logic), `"quoted phrases"` for exact word sequences, and a `-term` prefix to exclude documents containing that term
- Full regex pattern search as an alternative to plain text
- Matching is case-insensitive
- Choose how many characters of surrounding context to show before/after each match
- Results are written to a text file that opens automatically when the search finishes

## Installation
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install tax-authorities
tax-auth
```
The first command installs [uv](https://docs.astral.sh/uv/), a fast Python package/tool manager. Already have Python set up your own way? `pip install tax-authorities` works too, as long as `tax-auth` ends up on your PATH.

The first time `tax-auth` runs, it automatically downloads all three datasets from Hugging Face. That download only happens once — new documents are added to the datasets periodically, but `tax-auth` won't pick them up on its own. Run `tax-authorities download-data` any time to pull the latest versions of all three.

## Usage
Fill in exactly one of the two search fields, then press Enter or click **Search**:

- **Search Term(s)** — one or more words to match, without regex syntax:
  - Every term must be present in a document for it to match (AND logic).
  - Wrap multiple words in quotes (e.g. `"innocent spouse"`) to require that exact sequence.
  - Prefix a term with `-` (e.g. `-partnership`) to exclude documents containing it.
- **Regex Pattern** — a standard Python regular expression, matched against each document's text.

Use the checkboxes to choose which of the three datasets to search: **Tax Court Opinions**, **Revenue Rulings**, and **Private Letter Rulings**. Use the **Number of characters before/after** fields to control how much surrounding context is shown around each match (300 characters on each side by default).

When the search finishes, the results file opens automatically. It's also saved under your user data folder if you want to find it again later.

## Data
Three datasets, each hosted on Hugging Face:

- **Tax Court Opinions** — [andrew-mitchel/tax-court-opinions](https://huggingface.co/datasets/andrew-mitchel/tax-court-opinions) — 14,830 opinions, 1997 to the present.
- **Revenue Rulings** — [andrew-mitchel/revenue-rulings](https://huggingface.co/datasets/andrew-mitchel/revenue-rulings) — 3,475 documents, also including Notices, Announcements, and Revenue Procedures, 1998 to the present.
- **Private Letter Rulings** — [andrew-mitchel/private-letter-rulings](https://huggingface.co/datasets/andrew-mitchel/private-letter-rulings) — 45,348 IRS written determinations (PLRs, CCAs, TAMs, etc.), 1999 to the present.

These documents were originally published by the Tax Court and the IRS as PDFs, then converted to text and compiled into parquet files.

## License
[MIT](LICENSE)
