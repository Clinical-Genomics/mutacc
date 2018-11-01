import pytest

from mutacc.mutaccDB.remove_case import remove_case_from_db

def test_remove_case_from_db(mock_adapter):

    remove_case_from_db(mock_adapter, "2222")

    assert mock_adapter.case_exists("2222") == False
    assert mock_adapter.case_exists("1111")

    remove_case_from_db(mock_adapter, "1111")
    assert mock_adapter.case_exists("1111") == False
