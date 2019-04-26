"""
    Functions to sort variants
"""


CHROMOSOMES = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
               '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X',
               'Y', 'MT')

# Maps chromosomes to integers
CHROMOSOME_INTEGERS = {chrom: i+1 for i, chrom in enumerate(CHROMOSOMES)}

def sort_variants(variants):

    """
        Sort variants
    """

    variant_chromosomes = []
    for variant in variants:

        chrom_int = CHROMOSOME_INTEGERS.get(variant['chrom'])

        variant_chromosomes.append((chrom_int, variant['start'], variant))

    variant_chromosomes.sort(key=lambda x: (x[0], x[1]))

    sorted_variants = [variant[2] for variant in variant_chromosomes]

    return sorted_variants
