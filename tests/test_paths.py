import pytest
from tax_authorities import main
from tax_authorities.download import DATASETS


@pytest.mark.parametrize('name', ['cases', 'rev_ruls', 'plrs'])
def test_get_parquet_path_prefers_dev_local(tmp_path, monkeypatch, name):
    monkeypatch.setattr(main, 'PROJECT_ROOT', tmp_path)
    local_file = tmp_path / main.FILENAMES[name]
    local_file.write_text('', encoding='utf-8')

    assert main.get_parquet_path(name) == local_file


@pytest.mark.parametrize('name', ['cases', 'rev_ruls', 'plrs'])
def test_get_parquet_path_falls_back_to_user_data(tmp_path, monkeypatch, name):
    empty_project_root = tmp_path / 'project'
    empty_project_root.mkdir()
    data_dir = tmp_path / 'data'

    monkeypatch.setattr(main, 'PROJECT_ROOT', empty_project_root)
    monkeypatch.setattr(main, 'get_data_dir', lambda: data_dir)

    expected = data_dir / name / main.FILENAMES[name]
    assert main.get_parquet_path(name) == expected


def test_download_datasets_mapping():
    assert DATASETS == {
        'cases': 'andrew-mitchel/tax-court-opinions',
        'rev_ruls': 'andrew-mitchel/revenue-rulings',
        'plrs': 'andrew-mitchel/private-letter-rulings',
    }
