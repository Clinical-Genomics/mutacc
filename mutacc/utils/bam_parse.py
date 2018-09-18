#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pysam

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

    reads (list): List of read identifiers. 
    
"""
    sam_file = pysam.AlignmentFile(fileName, 'rb')
        
    reads = sam_file.fetch(reference = chrom, 
            start = start - padding, 
            end = end + padding)
    
    return [read.query_name for read in reads]


     
    
