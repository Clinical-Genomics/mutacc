
import ped_parser

def parse_ped(ped_file) -> dict:

    family = dict()

    with open(ped_file, 'r') as ped_handle:
        ped_obj = ped_parser.FamilyParser(ped_handle)

    family_name, family_obj = list(ped_obj.families.items())[0]

    family['family_id'] = family_name

    samples = [
        {
            'sample_id': sample_id,
            'mother': ind.mother,
            'father': ind.father,
            'affected': ind.affected,
            'sex': ind.sex
            }
        for sample_id, ind in family_obj.individuals.items()
    ]

    family['samples'] = samples
    return family
