import pytest

from mutacc.mutaccDB.query import mutacc_query

def test_mutacc_query(mock_adapter):

    samples, regions, variants = mutacc_query(
        mock_adapter,
        case_query = {},
        variant_query = None,
        member = 'child'
        )

    assert len(samples) == 5

    samples, regions, variants = mutacc_query(
        mock_adapter,
        case_query = {},
        variant_query = None,
        member = 'mother'
        )

    assert len(samples) == 5
    assert len(variants) == 5
    assert len(regions) == 5

    samples, regions, variants = mutacc_query(
        mock_adapter,
        case_query = None,
        variant_query = {},
        member = 'father'
        )

    assert len(samples) == 5
    assert len(regions) == 5
