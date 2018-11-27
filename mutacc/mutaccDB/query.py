import logging
import json

import pymongo

from mutacc.utils.region_handler import overlapping_region
from mutacc.utils.pedigree import make_family_from_case

LOG = logging.getLogger(__name__)

def mutacc_query(mutacc_adapter, case_query, variant_query, sex=None, member='affected', proband = False):
    """
        Given a case_query and a variant_query, this function finds the cases
        corresponding to the queries, where there are no overlaps of the variants
        of the cases.

        Args:
            mutacc_adapter(mutacc.mutaccDB.db_adapter.MutaccAdapter):
                Adapter to the mongod instance holding the mutacc database
            case_query(str): String of valid JSON
            variant_query(str): String of valid JSON
            sex(str): sex of sample to be found
            member(str): 'child', 'father', 'mother','affected'

        Returns:
            samples (list(mutacc.utils.pedigree.Individual)): list of samples, parsed
                with the Individual class from mutacc.utils.pedigree.
            regions (list(dict)): list of regions
            variants (list(dict)): list of variants
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
    final_samples = []
    final_variants = []
    final_regions = []
    for case in cases:

        family = make_family_from_case(case)
        individual = family.get_individual(member = member, sex = sex, proband = proband)
        if individual:

            individual_id = individual.individual_id
            case_variants = []
            case_regions = []
            overlaps = False
            variants = mutacc_adapter.find_variants(
                    {"_id": {"$in": case["variants"]}}
                )
            for variant in variants:
                #Add correct genotype of sample to variant
                variant["genotype"] = variant["samples"].get(individual_id)
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
                final_samples.append(individual)
                final_variants.extend(case_variants)
                final_regions.extend(case_regions)

    return final_samples, final_regions, final_variants
