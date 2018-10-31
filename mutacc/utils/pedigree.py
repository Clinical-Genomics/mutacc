import ped_parser

class Individual(ped_parser.Individual):
    """
        Extension on ped_parser.Individual and allow for two extra attributes
        variant_bam_file and variant_fastq_files for each sample
    """
    def __init__(self, ind, family='0', mother='0', father='0',sex='0',phenotype='0',
        genetic_models=None, proband='.', consultand='.', alive='.', variant_bam_file = '',
        variant_fastq_files = ['','']):

        super(Individual, self).__init__(
            ind,
            family = family,
            mother = mother,
            father = father,
            sex = sex,
            phenotype = phenotype,
            genetic_models=genetic_models,
            proband=proband,
            consultand=consultand,
            alive=alive)

        self.variant_bam_file = variant_bam_file
        self.variant_fastq_files = variant_fastq_files

class Family(ped_parser.Family):
    """
        Extension on ped_parser.Family to allow extra attributes
        regions and variants for each family
    """
    def __init__(self, family_id, regions = [], variants = []):

        super(Family, self).__init__(family_id, individuals = {})

        self.regions = regions
        self.variants = variants

    @property
    def get_child(self):

        child = None

        for individual_id in self.individuals:

            individual = self.individuals[individual_id]

            if individual.has_both_parents:

                child = individual

        return child

    @property
    def get_father(self):

        child = self.get_child
        if not child:

            return None

        father_id = child.father

        father = None
        for individual_id in self.individuals:
            individual = self.individuals[individual_id]

            if individual.individual_id == father_id:

                father = individual
                break

        return father

    @property
    def get_mother(self):

        child = self.get_child

        if not child:
            return None

        mother_id = child.mother

        mother = None
        for individual_id in self.individuals:
            individual = self.individuals[individual_id]

            if individual.individual_id == mother_id:

                mother = individual
                break

        return mother

    @property
    def get_affected(self):

        affected = None

        for individual_id in self.individuals:
            individual = self.individuals[individual_id]

            if individual.affected:

                affected = individual

        return individual

    def get_individual(self, member):

        members = {'father',
                   'mother',
                   'child',
                   'affected'}

        if member not in members:
            raise ValueError('member must be father, mother, child, or affected')

        if member == 'father':
            return self.get_father
        elif member == 'mother':
            return self.get_mother
        elif member == 'child':
            return self.get_child
        elif member == 'affected':
            return self.get_affected

def make_family_from_case(case):
    """
        Given a case, parses it as a family with the Family class and checks
        if the pedigree structure is valid

        Args:
            case(dict): dictionary holding case information

        Returns:
            case(mutacc.utils.pedigree.Family): Object from Family class
            where each sample from case is parsed with the Individual class
            and added to the Family object.
    """
    family_id = case['case_id']
    variants = case['extended_variants']
    regions = case['variant_regions']
    fam = Family(
            family_id = case['case_id'],
            variants = case['extended_variants'],
            regions = case['variant_regions']
            )

    for sample in case['samples']:

        if sample['sex'] == 'male':
            sex = '1'
        elif sample['sex'] == 'female':
            sex = '2'
        else:
            sex = '0'

        if sample['phenotype'] == 'unaffected':
            phenotype = '1'
        elif sample['phenotype'] == 'affected':
            phenotype = '2'
        else:
            phenotype = '0'


        individual = Individual(
            ind = sample['sample_id'],
            family = family_id,
            mother = sample['mother'],
            father = sample['father'],
            sex = sex,
            phenotype = phenotype,
            variant_bam_file = sample['variant_bam_file'],
            variant_fastq_files = sample['variant_fastq_files']
        )

        fam.add_individual(individual)

    fam.family_check()

    return fam
