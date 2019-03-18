import pytest

from mutacc.mutaccDB.remove_case import remove_case_from_db

def test_remove_case_from_db(mock_adapter):

    for case in mock_adapter.find_cases({}):
        case_id = case['case_id']
        assert mock_adapter.case_exists(case_id)
        remove_case_from_db(mock_adapter, case_id)
        assert not mock_adapter.case_exists(case_id)
