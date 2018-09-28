import pymongo

from schema.variant import VARIANT_VALIDATOR
from schema.case import CASE_VALIDATOR
from schema.sample import SAMPLE_VALIDATOR

class MutaccDBClient(pymongo.MongoClient):

    def __init__(self, host = 'localhost', port = 27017, user = None, password = None):

        super(MutaccDBClient, self).__init__(host, port)

    def init_db(self):

        if 'mutacc' not in self.database_names():

            db = self.mutacc

            db.create_collection("variants", validator = VARIANT_VALIDATOR)

            db.create_collection("cases", validator = CASE_VALIDATOR)

            db.create_collection("samples", validator = SAMPLE_VALIDATOR)

    def import_variants(self, variant):
        variants = self.mutacc.variants
        variants.insert_many(variant)        
    
    def import_case(self, case):

        cases = self.mutacc.cases
        cases.insert_one(case)    

    def import_samples(self, sample):

        samples = self.mutacc.samples
        samples.insert_many(sample)    

