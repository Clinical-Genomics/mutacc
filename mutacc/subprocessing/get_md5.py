import subprocess
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)

def get_md5(file_path):
    """
        Use command line tool 'md5' to calculate md5 hash of file

        Args:
            file_path(str): absolute path to file
        Returns:
            md5_sum(str): md5 sum of file
    """

    md5_base = 'md5'

    md5_cmd = [
        md5_base,
        '-q',
        str(file_path)
    ]

    log_msg = f"finding md5sum for {file_path}"
    LOG.info(log_msg)

    md5_sum = subprocess.check_output(md5_cmd).decode().strip()

    log_msg = f"md5sum: {md5_sum}"
    LOG.info(log_msg)

    return md5_sum
