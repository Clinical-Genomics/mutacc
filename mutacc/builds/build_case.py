from bson.objectid import ObjectId

from mutacc.utils.fastq_handler import fastq_extract
from mutacc.utils.bam_handler import get_overlaping_reads
from mutacc.build.build_variant import get_variants

from mutacc.parse.yaml_parse import yaml_parse

class CompleteCase:
    """
        Class with methods for handling case objects
    """
    def __init__(self, case):
        """
            Object is initilized with a case, a dictionary giving all relevant information about
            the case
        """

        self.case = case["case"]
        self.variants = case["variants"]
        self.samples = case["samples"]

        self.sample_ids = [sample["sample_id"] for sample in self.samples]
        
    def get_variants(self, padding = 1000):
        """
            Method that parses the vcf in the case dictionary, adds an _id and foreign ids for case
            and samples that the variant belongs to
        """
        self.variants_object = []
        self.variants_id = []
        

        for variant in get_variants(self.variants):

            variant.find_region(padding)
            variant.build_variant_object()
            variant_object = variant.variant_object

            _id = ObjectId()

            variant_object["_id"] = _id

            self.variants_id.append(_id)

            variant_object["padding"] = padding

            variant_object["samples"] = self.sample_ids

            variant_object["case"] = self.case["case_id"]
            
            self.variants_object.append(variant_object)


    def get_samples(self):
        """
            Method makes a list of sample objects, ready to load into a mongodb. This includes
            looking for the raw reads responsible for the variants in the vcf for each sample,
            write them to fastq files, and add the path to these files in the sample object.
        """

        self.samples_object = []
        for sample_object in self.samples:
            
            bam_file = sample_object["bam_file"]

            
            read_ids = set() #Holds the read_ids from the bam file

            #For each variant, the reads spanning this genomic region in the bam file are found
            for variant in self.variants_object:
                
                
                read_ids = read_ids.union(get_overlaping_reads(start = variant["reads_region"]["start"], 
                                                               end = variant["reads_region"]["end"],
                                                               chrom = variant["chrom"],
                                                               fileName = bam_file))
            
            #Given the read_ids, and the fastq files, the reads are extracted from the fastq files    
            variant_fastq_files = fastq_extract(sample_object["fastq_files"], read_ids) 

            sample_object["variant_fastq_files"] = variant_fastq_files

            sample_object["variants"] = self.variants_id
            
            sample_object["case"] = self.case["case_id"]

            self.samples_object.append(sample_object)

  
    def get_case(self):
        
        """
            Completes the case object to be uploaded in mongodb
        """
        self.case_object = self.case
        self.case_object["samples"] = self.sample_ids
        self.case_object["variants"] = self.variants_id


