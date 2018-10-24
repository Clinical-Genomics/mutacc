import logging
import json

import pymongo

from mutacc.utils.region_handler import overlapping_region
from mutacc.utils.pedigree import make_family_from_case

LOG = logging.getLogger(__name__)

def mutacc_query(mutacc_adapter, case_query, variant_query):
    """
        Given a case_query and a variant_query, this function finds the cases
        corresponding to the queries, where there are no overlaps of the variants
        of the cases.

        Args:
            mutacc_adapter(mutacc.mutaccDB.db_adapter.MutaccAdapter):
                Adapter to the mongod instance holding the mutacc database
            case_query(str): String of valid JSON
            variant_query(str): String of valid JSON

        Returns:
            cases (list(mutacc.utils.pedigree.Family)): list of cases, parsed
            with the Family class from mutacc.utils.pedigree, where each object
            also contains a list of the regions, and a list of complete variant
            information for Each variant found in the case
    """
    #If a case_query is given, find the cases for the query
    if case_query:

        case_query = json.loads(case_query)
        cases = mutacc_adapter.find_cases(case_query)

    else:
        cases = []

    #Make list of all case_id
    case_ids = [case['case_id'] for case in cases]

    #If variant_query is given, find the cases for the variants corresponding
    #to the query, if the case_id is not already in case_ids
    if variant_query:

        variant_query = json.loads(variant_query)
        variants = mutacc_adapter.find_variants(variant_query)

        for variant in variants:

            if variant['case'] not in case_ids:

                new_case = mutacc_adapter.find_case({"case_id": variant['case']})
                cases.append(new_case)
                case_ids.append(variant['case'])

    #Scan through the found cases, and make sure that none of the variant regions
    #of any case overlaps with another
    final_cases = []
    final_variants = []
    final_regions = []
    for case in cases:

        case_variants = []
        case_regions = []
        overlaps = False
        variants = mutacc_adapter.find_variants(
                {"_id": {"$in": case["variants"]}}
            )
        for variant in variants:

            region =  {"chrom": variant["chrom"],
                       "start": variant["reads_region"]["start"],
                       "end": variant["reads_region"]["end"]}

            if overlapping_region(region, final_regions):
                LOG.warning("case {} contain overlapping variant".format(
                case["case_id"])
                )
                overlaps = True
                break
            case_variants.append(variant)
            case_regions.append(region)

        if not overlaps:
            #Add the regions and variants to each case before parsing
            #with make_family_from_case
            case['variant_regions'] = case_regions
            case['extended_variants'] = case_variants
            final_cases.append(make_family_from_case(case))
            final_variants.extend(case_variants)
            final_regions.extend(case_regions)

    return final_cases
