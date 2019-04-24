import subprocess
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)

def exclude_from_fastq(name_file, out_file, fastq_file, seqkit_exe=None):
    """
        Use command line tool 'seqkit grep' to exclude reads
        from fastq file

        Args:
            name_file(str): File containing read names to be removed (one name
                per line)
            out_file(str): Name of fastq file with excluded reads
            fastq_file(str): Name of input fastq file
    """

    seqkit_base = seqkit_exe or "seqkit"
    seqkit_cmd = [
        seqkit_base,
        "grep",
        "-v",
        "--pattern-file",
        name_file,
        "-o",
        out_file,
        fastq_file
    ]

    LOG.info("excluding reads from {}".format(fastq_file))

    try:
        subprocess.check_call(seqkit_cmd)

    except subprocess.CalledProcessError:
        LOG.critical("{} failed to run".format(
            " ".join(seqkit_cmd)
            )
        )
        raise

    #Make sure new fastq has been created
    exists = Path(out_file).exists()
    if not exists:
        LOG.critical("Failed to create fastq file")
        raise FileNotFoundError
