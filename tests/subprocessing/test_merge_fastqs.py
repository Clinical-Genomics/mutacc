from pathlib import Path
import gzip
import subprocess

import pytest


from mutacc.subprocessing.merge_fastqs import merge_fastqs

FASTQ = "tests/fixtures/one_entry.fastq.gz"

def test_merge_fastqs(tmpdir):

    out_dir = Path(tmpdir.mkdir("test_merge"))

    out_file = out_dir.joinpath('merged_fastq.fastq.gz')

    merge_fastqs([FASTQ]*100, out_file)

    with gzip.open(out_file, "rt") as handle:

        count = 0
        for line in handle:
            count += 1

    assert count == 400
    assert out_file.exists()

    with pytest.raises(subprocess.CalledProcessError) as error:

        merge_fastqs(["FSFAS#uygh4324", FASTQ], out_file)
