import pytest

from mutacc.mutaccDB.query import mutacc_query

def test_mutacc_query(mock_adapter):

    cases = mutacc_query(
        mock_adapter,
        case_query = '{}',
        variant_query = None
        )

    assert len(cases) == 1

    assert cases[0].family_id in ["1111","2222"]

    cases = mutacc_query(
        mock_adapter,
        case_query = '{"case_id": "2222"}',
        variant_query = None
        )

    assert len(cases) == 1
    assert cases[0].family_id == "2222"

    cases = mutacc_query(
        mock_adapter,
        case_query = None,
        variant_query = '{}'
        )

    assert len(cases) == 1
    assert cases[0].family_id in ["1111","2222"]

    assert len(cases[0].regions) == 7
