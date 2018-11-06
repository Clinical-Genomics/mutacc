import pytest

from mutacc.mutaccDB.query import mutacc_query

def test_mutacc_query(mock_adapter):

    samples, regions, variants = mutacc_query(
        mock_adapter,
        case_query = '{}',
        variant_query = None,
        sex = 'male'
        )

    assert len(samples) == 1

    assert samples[0].family in ["1111","2222"]

    samples, regions, variants = mutacc_query(
        mock_adapter,
        case_query = '{"case_id": "2222"}',
        variant_query = None,
        member = 'mother'
        )

    assert len(samples) == 1
    assert len(variants) == 7
    assert len(regions) == 7
    assert samples[0].family == "2222"

    samples, regions, variants = mutacc_query(
        mock_adapter,
        case_query = None,
        variant_query = '{}'
        )

    assert len(samples) == 1
    assert samples[0].family in ["1111","2222"]

    assert len(regions) == 7
