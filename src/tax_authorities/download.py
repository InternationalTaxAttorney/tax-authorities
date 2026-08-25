from pathlib import Path

from huggingface_hub import snapshot_download
from platformdirs import user_data_dir

APP_NAME = 'tax_authorities'

DATASETS = {
    'cases': 'andrew-mitchel/tax-court-opinions',
    'rev_ruls': 'andrew-mitchel/revenue-rulings',
    'plrs': 'andrew-mitchel/private-letter-rulings',
}


def get_data_dir():
    return Path(user_data_dir(APP_NAME))


def download_dataset(name):
    dataset_dir = get_data_dir() / name

    snapshot_download(
        repo_id=DATASETS[name],
        repo_type='dataset',
        local_dir=dataset_dir,
        local_dir_use_symlinks=False,
    )

    return dataset_dir


def download_data():
    return {name: download_dataset(name) for name in DATASETS}
