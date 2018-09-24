from mutacc.utils.fastq_handler import fastq_extract
from mutacc.utils.bam_handler import get_overlaping_reads
from mutacc.utils.vcf_handler import make_variants
class HandleCase:
    """
        Class with methods for handling case objects
    """
    
    @staticmethod
    def find_reads(case, padding = 500):
        """

            Given a case this function finds all relevant read from the given fastqfiles 
            for the vartiants of interest

            Args:

                case (dict): dictionary containing the case data to be uploaded to the 
                database
                
            Returns: 

                case (dict): updated case, containing the paths to the reads (fastq.files) 
                and additional meta data

        """
        #Parsing the vcf file given in the case, and replaces the variant field in the 
        #case object with a list of variants.
        case["variants"] = make_variants(case["variants"], padding)
        #list variant_reads will, for each sample in the case, store the paths to the fastq
        #files containing the reads around the variants.
        variant_reads = []    

        #for each sample in the case, find the reads around the variants specified from
        #the samples fastqs
        for sample in case['samples']:
            
            bam_file = sample['bam']
            
            #Find the sequence IDs from the bam samples bam file
            ids = set()
            for variant in case["variants"]:

                ids = ids.union(get_overlaping_reads(start = variant["reads_region"]["start"], 
                                           end = variant["reads_region"]["end"],
                                           chrom = variant["chrom"],
                                           fileName = bam_file))

            #Make new fastq_files containing the reads    
            sample_fastqs = fastq_extract(sample["fastq"], ids)
            
            #Make dictionary holding new data
            sample_reads = {"sample_id": sample["sample_id"],
                            "fastq_files": sample_fastqs,
                            "read_number": len(ids)}
            
            #Append to the list variant_reads
            variant_reads.append(sample_reads)
        
        #Append new key value pair to the case dictionary
        case["variant_reads"] = variant_reads
        
        return case


