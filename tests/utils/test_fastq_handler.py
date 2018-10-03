import pytest
import random
import gzip

from Bio import SeqIO

from mutacc.utils.fastq_handler import *

def test_fastq_extract(tmpdir):
    """
        Test function for fastq_extract
    """

    files = ['tests/fixtures/fastq1.fastq','tests/fixtures/fastq2.fastq']
    
    #Opens fastq files and parses with SeqIO.parse
    #Saves the records for both files in fastqs
    fastqs = []
    for file in files:
        
        with open(file, 'r') as handle: 
            
            fastqs.append(list(SeqIO.parse(handle, 'fastq')))
    
    #Samples random records from the fastq files        
    record_index = sorted(random.sample(range(0,len(fastqs[0])),5))
    fastqs[0] = [fastqs[0][index] for index in record_index]
    fastqs[1] = [fastqs[1][index] for index in record_index]

    #Make list of record IDs 
    ids = [record.id for record in fastqs[0] ]

    #Calls fastq_extract
    paths = fastq_extract(files, ids, tmpdir.mkdir("fastq_test"))

    #Compare the records in the files created by fastq_extract
    #with those in fastqs
    for path, fastq in zip(paths, fastqs):

        with gzip.open(path, 'rt') as handle:

           test_fastq = list(SeqIO.parse(handle, 'fastq'))
           
        for record, test_record in zip(fastq, test_fastq):

            assert record.id == test_record.id
            assert record.seq == test_record.seq
            assert record.letter_annotations['phred_quality'] == \
                    test_record.letter_annotations['phred_quality']

        assert len(fastq) == len(test_fastq) == 5       

    

    
