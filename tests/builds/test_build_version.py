import pytest
from unittest.mock import patch

from pathlib import Path
from mutacc.builds.build_version import VersionedDataset

SAMPLE_IDS = ('sample_1', 'sample_2', 'sample_3')
E_SAMPLE_ID = 'sample_4'

def test_find_sample_dir(dataset_dir):

    versioned_dataset = VersionedDataset(dataset_dir=dataset_dir)

    for sample_id in SAMPLE_IDS:
        dir = versioned_dataset.find_sample_dir(sample_id=sample_id)
        assert dir.exists()

    with pytest.raises(FileNotFoundError) as error:
        dir = versioned_dataset.find_sample_dir(E_SAMPLE_ID)

def test_find_file(dataset_dir):

    versioned_dataset = VersionedDataset(dataset_dir=dataset_dir)
    file = versioned_dataset._find_file(dir_path=dataset_dir, includes='.vcf')

    assert file.exists

    with pytest.raises(FileNotFoundError) as error:
        file = versioned_dataset._find_file(dir_path=dataset_dir, includes=E_SAMPLE_ID)

@patch('mutacc.builds.build_version.get_md5')
def test_build_dataset(mock_md5, dataset_dir):

    versioned_dataset = VersionedDataset(dataset_dir=dataset_dir)
    assert not list(versioned_dataset.keys())
    mock_md5.return_value = ''
    versioned_dataset.build_dataset(md5=True)
    assert set(versioned_dataset.keys()) == {'dataset_id', 'samples', 'vcf'}
    versioned_dataset.build_dataset(md5=True, comment='comment')
    assert set(versioned_dataset.keys()) == {'dataset_id', 'samples', 'vcf', 'comment'}
