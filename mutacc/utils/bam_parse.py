#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pysam

def getOverlapingReads(fileName, chrom, start, n=0):
    
    with pysam.AlignmentFile(fileName, 'rb') as file:
        
        reads = file.fetch(chrom, start - n, start + n)
    
    return [read.query_name for read in reads]



if __name__ == '__main__':
    
    FILENAME = ''
    CHROM = ''
    START = 0
    n = 0
    
    reads = getOverlapingReads(FILENAME, CHROM, START, n)
    
    
