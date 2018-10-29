import pytest

from mutacc.utils.pedigree import Individual, Family, make_family_from_case


def test_Individual(individuals_fixed):

    child = individuals_fixed[0]
    father = individuals_fixed[1]
    mother = individuals_fixed[2]

    assert child.affected
    assert child.variant_bam_file == "/path/to/bam"
    assert child.variant_fastq_files == ["/path/to/fastq1", "/path/to/fastq2"]
    assert child.sex == 1

    assert father.sex == 1
    assert (not father.affected)

def test_Family(individuals_fixed):

    family = Family(
        family_id = "family",
        variants = [],
        regions = []

    )

    for individual in individuals_fixed:

        family.add_individual(individual)

    family.family_check()

    child = family.get_individual('child')
    father = family.get_individual('father')
    mother = family.get_individual('mother')
    affected = family.get_individual('affected')

    assert child.individual_id == 'child'
    assert father.individual_id == 'father'
    assert mother.individual_id == 'mother'
    assert affected.affected

def test_make_family_from_case(individuals_fixed):

    c0 = {
        'case_id': 'test_family0',
        'variant_regions': [],
        'extended_variants': [],
        'samples': [
            {
                'sample_id': 'proband',
                'father': 'father',
                'mother': 'mother',
                'sex': 'male',
                'phenotype': 'affected',
                'variant_bam_file': 'example_bam',
                'variant_fastq_files': []
            },
            {
                'sample_id': 'father',
                'father': '0',
                'mother': '0',
                'sex': 'male',
                'phenotype': 'unaffected',
                'variant_bam_file': 'example_bam',
                'variant_fastq_files': []
            },
            {
                'sample_id': 'mother',
                'father': '0',
                'mother': '0',
                'sex': 'female',
                'phenotype': 'affected',
                'variant_bam_file': 'example_bam',
                'variant_fastq_files': []
            }
        ]
    }

    c1 = {
        'case_id': 'test_family1',
        'variant_regions': [],
        'extended_variants': [],
        'samples': [
            {
                'sample_id': 'single',
                'father': '0',
                'mother': '0',
                'sex': 'male',
                'phenotype': 'affected',
                'variant_bam_file': 'example_bam',
                'variant_fastq_files': []
            }
        ]
    }

    fam0 = make_family_from_case(c0)
    fam1 = make_family_from_case(c1)

    assert fam0.get_individual('child').individual_id == "proband"
    assert fam0.get_individual('father').individual_id == "father"
    assert fam0.get_individual('mother').individual_id == "mother"

    assert (not fam1.get_individual('child'))
    assert (not fam1.get_individual('father'))
    assert (not fam1.get_individual('mother'))
    assert fam1.get_individual('affected').affected
