import logging

from mongo_adapter import MongoAdapter

LOG = logging.getLogger(__name__)


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

        if "variants" not in self.db.list_collection_names():

            self.db.create_collection("variants")

        if "cases" not in self.db.list_collection_names():

            self.db.create_collection("cases")

        if "datasets" not in self.db.list_collection_names():
            self.db.create_collection("datasets")

        self.variants_collection = self.db.variants
        self.cases_collection = self.db.cases
        self.datasets_collection = self.db.datasets

    def add_dataset(self, dataset):
        
        self.datasets_collection.insert_one(dataset)

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

    def find_cases(self, query):

        return [case for case in self.cases_collection.find(query)]

    def find_case(self, query):

        return self.cases_collection.find_one(query)

    def find_variants(self, query):

        return [variant for variant in self.variants_collection.find(query)]

    def find_variant(self, query):

        return self.variants_collection.find_one(query)

    def remove_case(self, case_id):

        case = self.find_case({"case_id": case_id})
        if case:
            LOG.info("removing case {}".format(case_id))
            self.cases_collection.delete_one({"case_id": case_id})
            self.variants_collection.delete_many({"case": case_id})
        else:
            LOG.warning("No case with case_id {}".format(case_id))
        return case
