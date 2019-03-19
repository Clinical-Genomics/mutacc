import logging
import os

import pymongo


LOG = logging.getLogger(__name__)

def remove_case_from_db(mutacc_adapter, case_id):

    case = mutacc_adapter.remove_case(case_id)

    for sample in case["samples"]:

        if sample.get("variant_bam_file"):
            try:
                os.remove(sample["variant_bam_file"])

            except FileNotFoundError as error:
                LOG.warning(f"{sample['variant_bam_file']} not found")


        if sample.get("variant_fastq_files"):

            for variant_fastq_file in sample["variant_fastq_files"]:

                try:
                    os.remove(variant_fastq_file)

                except FileNotFoundError as error:

                    LOG.warning(f"{variant_fastq_file} not found")
