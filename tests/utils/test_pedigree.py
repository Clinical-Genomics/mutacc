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


def test_make_family_from_trio():
    # GIVEN a trio case
    case = {
        'case_id': 'test_family0',
        'samples': [
            {
                'sample_id': 'child',
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

    # WHEN trio is converted to a family object
    family = make_family_from_case(case)

    # THEN the child is found
    assert family.get_individual('child').individual_id == "child"

    # THEN the father is found
    assert family.get_individual('father').individual_id == "father"

    # THEN the mother is found
    assert family.get_individual('mother').individual_id == "mother"

    # THEN no female child is found
    assert not family.get_individual('child', sex = 'female')

    # THEN a male child is found
    assert family.get_individual('child', sex = 'male').individual_id == "child"

    # THEN mother is found when searching for an affected female individual
    assert family.get_individual('affected', sex = 'female').individual_id == "mother"

    # THEN the child is found when searching for an affected male
    assert family.get_individual('affected', sex = 'male').individual_id == "child"


def test_make_family_from_single():

    # GIVEN a case with a single affected individual
    case = {
        'case_id': 'test_family1',
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

    # WHEN case is converted to a family object
    family = make_family_from_case(case)

    # THEN no child is found
    assert (not family.get_individual('child'))

    # THEN no father is found
    assert (not family.get_individual('father'))

    # THEN no mother is found
    assert (not family.get_individual('mother'))

    # THEN an affected is found
    assert family.get_individual('affected').affected

    # THEN no affected female is found
    assert not family.get_individual('affected', sex ='female')

    # THEN an affected male is found and is the individual
    assert family.get_individual('affected', sex ='male')
    assert family.get_individual('affected', sex = 'male').individual_id == "single"


def test_make_family_from_quertet():

    # GIVEN a case with two siblings, where just one is affected
    case = {
        'case_id': 'test_family0',
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
                'sample_id': 'sibling',
                'father': 'father',
                'mother': 'mother',
                'sex': 'male',
                'phenotype': 'unaffected',
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

    # WHEN case is converted to a family object
    family = make_family_from_case(case)

    # THEN the affected sibling is found and not the unaffected
    assert family.get_individual('child').affected
    assert family.get_individual('child').individual_id == 'proband'
