import pymongo

from mongo_adapter import MongoAdapter

from mutacc.mutaccDB.schema.variant import VARIANT_VALIDATOR
from mutacc.mutaccDB.schema.case import CASE_VALIDATOR
from mutacc.mutaccDB.schema.sample import SAMPLE_VALIDATOR

class MutaccAdapter(MongoAdapter):
    """
        Class to handle connection to the mutacc mongodb. Inherit from mongo_adapter.MongoAdapter
    """
    def setup(self, db_name='mutacc'):
        """
            Setup mongodb for mutacc. Creates the collections (samples, cases, variants) with
            validators if the do not already exist
            
            Args:
                db_name(str): Name of database (defaults to 'mutacc')

        """
        if self.client is None:
            raise SyntaxError("No client is available")
        if self.db is None:
            self.db = self.client[db_name]
            self.db_name = db_name

        if "variants" not in self.db.collection_names():

            self.db.create_collection("variants", validator = VARIANT_VALIDATOR)
            
        if "cases" not in self.db.collection_names():

            self.db.create_collection("cases", validator = CASE_VALIDATOR)

        #if "samples" not in self.db.collection_names():

        #    self.db.create_collection("samples", validator = SAMPLE_VALIDATOR)
  
        self.variants_collection = self.db.variants
        self.cases_collection = self.db.cases
        #self.samples_collection = self.db.samples

    def add_variants(self, variants):
        """
            Adds variants to collection 'variants'
            
            Args:
                variants(list): List of variants, represented as dictionaries, to be uploaded to
                collection 'variants'

            Returns:
                VariantIds(list): list of ObjectIds for the variants inserted in the collection
                'variants'
        """
        result = self.variants_collection.insert_many(variants)
        return result.inserted_ids

    def add_case(self, case):
        """
            Adds case object to collection 'cases'

            Args:
                case(dict): dictionary containing information about the case.
        """
        self.cases_collection.insert_one(case)

    #def add_samples(self, samples):
    #    """
    #        Adds samples to collection 'samples'
    #
    #        Args:
    #            samples(list): list of samples, represented as dictionaries, containing information
    #            about the samples.
    #            
    #    """
    #    self.samples_collection.insert_many(samples)

    def case_exists(self, case_id):
        """
            Check if collection with field 'case_id': case_id exists.
            
            Args:
                case_id(str): name of case
            Returns:
                exists(bool): True if exists, else False
        """

        if self.cases_collection.find({"case_id": case_id}).count() > 0:
            return True

        return False

    #def sample_exists(self, sample_id):    
    #    """
    #        Check if sample with 'sample_id': sample_id exists.
    #
    #        Args:
    #            sample_id(str): name of sample
    #        Returns:
    #            exists(bool): True if exists, else False
    #    """
    #    if self.samples_collection.find({"sample_id": sample_id}).count() > 0:
    #        return True
    #
    #    return False
