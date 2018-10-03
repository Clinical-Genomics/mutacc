#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pysam

from mutacc.parse.path_parse import parse_path

def get_overlaping_reads(fileName, chrom, start, end):
    """

        Extracts all read names from a bam file, overlapping the specified region.

        Args:

            fileName (string): name of bam file
            chrom (string): name of chromosome
            start (int): start of region
            end (int): end of region

        Returns:

            reads (set): set of read names. 
        
    """
    fileName = parse_path(fileName)

    sam_file = pysam.AlignmentFile(fileName, 'rb')
        
    reads = sam_file.fetch(reference = chrom, 
            start = start, 
            end = end)
    
    ids = [read.query_name for read in reads]
    
    sam_file.close()

    return set(ids)
     
