import pytest

from mutacc.utils.region_handler import overlaps, overlapping_region

REG1 = {
    "start": 100000000,
    "end": 100001000,
    "chrom": 'chr4'
}

REG2 = {
    "start": 100000500,
    "end": 100001500,
    "chrom": 'chr4'
}

REG3 = {
    "start": 100000500,
    "end": 100001500,
    "chrom": 'chr7'
}


def test_overlaps():

    assert overlaps(REG1, REG2)
    assert not overlaps(REG1, REG3)

def test_overlapping_region():

    region_list = [REG2, REG3]

    assert overlapping_region(REG1, region_list)
    assert not overlapping_region(REG1, [REG3])
