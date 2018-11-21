import pytest
import random
from mutacc.utils.sort_variants import sort_variants

VARIANTS = [

    {"chrom": "1", "start": 111},
    {"chrom": "1", "start": 222},
    {"chrom": "1", "start": 333},
    {"chrom": "3", "start": 111},
    {"chrom": "3", "start": 444},
    {"chrom": "6", "start": 222},
    {"chrom": "6", "start": 888},
    {"chrom": "6", "start": 1111},
    {"chrom": "8", "start": 222},
    {"chrom": "X", "start": 222},
    {"chrom": "X", "start": 1000},
    {"chrom": "X", "start": 2000},
    {"chrom": "Y", "start": 222},
    {"chrom": "Y", "start": 333},
    {"chrom": "Y", "start": 444},
    {"chrom": "MT", "start": 222},
    {"chrom": "MT", "start": 444},
]

def test_sort_variants():

    scrambled_variants = VARIANTS[:]
    random.shuffle(scrambled_variants)

    assert scrambled_variants != VARIANTS

    sorted_variants = sort_variants(scrambled_variants)

    assert sorted_variants == VARIANTS
