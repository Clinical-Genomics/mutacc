import pytest
import mongomock

import mongo_adapter

from mutacc.mutaccDB.db_adapter import MutaccAdapter

def test_MutaccAdapter():

    mutacc_client = mongomock.MongoClient(port = 27017, host = 'localhost')
    adapter = MutaccAdapter(client = mutacc_client, db_name = 'test_mutacc')

    adapter.add_variants([{"variant_id": "variant1"},
                          {"variant_id": "variant2"}])

    adapter.add_case({"case_id": "case1"})

    assert adapter.case_exists("case1")

    case = adapter.find_case({"case_id": "case1"})
    assert case["case_id"] == "case1"

    variant = adapter.find_variant({"variant_id": "variant2"})
    assert variant["variant_id"] == "variant2"
