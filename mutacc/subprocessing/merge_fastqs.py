import subprocess
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)

def merge_fastqs(fastq_files: list, out_file: str):

    merge_cmd = ['cat']

    merge_cmd.extend(fastq_files)

    with open(out_file, 'w') as out_handle:

        try:
            subprocess.check_call(merge_cmd, stdout = out_handle)

        except subprocess.CalledProcessError as error:

            LOG.critical("Merge of fastq files failed with exit code {}".format(
                    error.returncode
                )
            )

            raise

    if not Path(out_file).exists():

        LOG.critical("file {} was not created".format(str(out_file)))
        raise FileNotFoundError
