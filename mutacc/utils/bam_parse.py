#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pysam
from mutacc.utils.fastq_parse import fastq_extract

def get_overlaping_reads(fileName, chrom, start, end, padding = 300):
    """

        Extracts all read names from a bam file, overlapping the specified region.

        Args:

            fileName (string): name of bam file
            chrom (string): name of chromosome
            start (int): start of region
            end (int): end of region
            padding (int): optional padding of region. i.e. Reads in the vicinity vill also be detected
                           depending on the padding parameter. 

        Returns:

            reads (set): set of read names. 
        
    """
    sam_file = pysam.AlignmentFile(fileName, 'rb')
        
    reads = sam_file.fetch(reference = chrom, 
            start = start - padding, 
            end = end + padding)
    
    ids = [read.query_name for read in reads]

    return set(ids)
     
