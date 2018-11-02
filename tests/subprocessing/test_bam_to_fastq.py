import pytest
import subprocess

from mutacc.subprocessing.bam_to_fastq import bam_to_fastq

def test_bam_to_fastq():
    
    with pytest.raises(subprocess.CalledProcessError) as error:

        bam_to_fastq("ADSH3#12fds", "hgf#dfiASF654", "dfdfsfdsGHDF#54")
