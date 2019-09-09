import logging
import json
import copy

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
    if case_query is not None:
        cases = mutacc_adapter.find_cases(case_query)
    else:
        cases = []

    #Make list of all case_id
    case_ids = [case['case_id'] for case in cases]

    #If variant_query is given, find the cases for the variants corresponding
    #to the query, if the case_id is not already in case_ids
    if variant_query is not None:
        variant_cases = cases_from_variants(mutacc_adapter, variant_query, case_ids)
        cases.extend(variant_cases)


    final_samples, final_regions, final_variants = get_samples_from_cases(
        mutacc_adapter,
        cases,
        sex = sex,
        member = member,
        proband = proband
    )

    return final_samples, final_regions, final_variants


def cases_from_variants(mutacc_adapter, query, not_cases=None):

    """
        Given a variant query, return the cases for these variants

        Args:
            mutacc_adapter (mutacc.mutaccDB.db_adapter.MutaccAdapter):
                Adapter to the mongod instance holding the mutacc database
            variant_query(str): String of valid JSON
            not_cases(list): list of case_ids that should NOT be queried for.

        Returns:
            cases (list): list of cases.

    """
    variant_query = copy.deepcopy(query)
    if not_cases:
        variant_query['case'] = {'$nin': not_cases}

    variants = mutacc_adapter.find_variants(variant_query)

    case_ids = [variant['case'] for variant in variants]

    case_query = {'case_id': {'$in': case_ids}}
    cases = mutacc_adapter.find_cases(case_query)

    return cases

def get_samples_from_cases(mutacc_adapter, cases, sex=None, member='affected', proband = False):

    """
        Filters out the relevant samples from a list of cases. Also provides a check,
        so that no variant from any sample overlap with another.

        Args:
            mutacc_adapter(mutacc.mutaccDB.db_adapter.MutaccAdapter):
                Adapter to the mongod instance holding the mutacc database
            cases (list): list of cases.
            sex(str): sex of sample to be found
            member(str): 'child', 'father', 'mother','affected'
            proband(bool): If true, returns the single sample from cases with
                only one sample.

    """

    #Lists to hold final samples, variants, and regions
    final_samples = []
    final_variants = []
    final_regions = []
    for case in cases:

        #Parse case with Family class
        family = make_family_from_case(case)

        #Try to find relevant individual from family
        individual = family.get_individual(member=member, sex=sex, proband=proband)

        if individual:

            individual_id = individual.individual_id

            #Find sample object
            target_sample = {}
            for sample in case['samples']:
                if sample['sample_id'] == individual_id:
                    target_sample = sample

            #Store variants and regions from case
            case_variants = []
            case_regions = []

            overlaps = False

            #Get variants from case from database
            variants = mutacc_adapter.find_variants({"_id": {"$in": case["variants"]}})

            for variant in variants:
                #Add correct genotype of sample to variant
                variant["genotype"] = variant["samples"].get(individual_id)
                region = {"chrom": variant["chrom"],
                          "start": variant["reads_region"]["start"],
                          "end": variant["reads_region"]["end"]}

                #See if region overlaps with already found regions
                #If it does, continue with next case
                if overlapping_region(region, final_regions):

                    log_msg = f"case {case['case_id']} contain overlapping variant"
                    LOG.warning(log_msg)
                    overlaps = True
                    break

                #remove _id (mongodb object id) from variant object so that it
                #can be serialized as json
                del variant['_id']

                case_variants.append(variant)
                case_regions.append(region)

            #If genomic regions from case does not overlap with any other,
            #Append sample, variant, and region to be returned from function.

            if not overlaps:
                final_samples.append(target_sample)
                final_variants.extend(case_variants)
                final_regions.extend(case_regions)

    return final_samples, final_regions, final_variants
