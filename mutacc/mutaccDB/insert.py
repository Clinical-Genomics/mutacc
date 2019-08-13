"""
    Module with functions to insert into database
"""

import datetime
import logging
from copy import deepcopy

LOG = logging.getLogger(__name__)

def insert_entire_case(mutacc_adapter, case, replace=False):
    """
        Insert an entire case into mongodb database. That is, case, samples, and variants.

        Args:
            mutacc_adapter(mutacc.mutaccDB.db_client.MutaccAdapter): Adapter instantiated with a
            client to mongodb instance and db name.

            case(mutacc.builds.build_case.CompleteCase): Instance of class CompleteCase containing
            information about the case, variants, and samples in the case.

    """
    # Save case_id
    case_id = case['case']['case_id']

    # If replace flag is specified, remove case and variants associated with case
    if replace:
        mutacc_adapter.remove_case(case_id)

    # copy variants-, samples-, and case from case object.
    variants = deepcopy(case['variants'])
    samples = deepcopy(case['samples'])
    case = deepcopy(case['case'])

    # add case_id field for variant objects, pointing to the case where
    # the variants come from
    for variant in variants:

        variant["case"] = case_id

    # Insert variants into db and save ObjectIds for the documents as variant_ids
    variant_ids = mutacc_adapter.add_variants(variants)

    # Add variant_ids and sample objects to case object
    case["variants"] = variant_ids
    case["samples"] = samples
    case["modified"] = datetime.datetime.utcnow()

    # Insert case into db

    mutacc_adapter.add_case(case)

    LOG.info("Case added to mutaccDB")

def insert_version(mutacc_adapter, dataset):
    mutacc_adapter.add_dataset(dataset)
