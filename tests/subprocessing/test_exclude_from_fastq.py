import pytest
import subprocess

from mutacc.subprocessing.exclude_from_fastq import exclude_from_fastq

def test_exclude_from_fastq():

    with pytest.raises(subprocess.CalledProcessError) as error:

        exclude_from_fastq("ADSH3#12fds", "hgf#dfiASF654", "dfdfsfdsGHDF#54")
