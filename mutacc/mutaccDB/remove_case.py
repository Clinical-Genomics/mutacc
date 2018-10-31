import logging
import os

import pymongo


LOG = logging.getLogger(__name__)

def remove_case_from_db(mutacc_adapter, case_id):

    case = mutacc_adapter.remove_case(case_id)

    for sample in case["samples"]:

        os.remove(sample["variant_bam_file"])

        for variant_fastq_file in sample["variant_fastq_files"]:

            os.remove(variant_fastq_file)
