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

    
class BAMContext:
    """
        Context manager to deal with bam files
    """
    def __init__(self, bam_file, ends:int = 2):
        """
            Args:
                bam_file(str): path to bam file 
                ends(int): 2 if paired end reads, 1 if not
        """
        bam_file = parse_path(bam_file)
        self.file_name = bam_file.name
        self.sam = pysam.AlignmentFile(bam_file, 'rb')
        self.reads = {}
        self.ends = ends

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.sam.close()

    def find_reads_from_region(self, chrom, start, end):
        """
            Given a region defined by chrom, start, end, find all records overlapping with this
            region

            Args:
                chrom(str): chromosome/contig name
                start(int): start position
                end(int): end position
        """
        for read in self.sam.fetch(chrom, start, end):

            if read.query_name not in self.reads.keys(): self.reads[read.query_name] = []

            self.reads[read.query_name].append(read)
        
        unmatched = []
        for key in self.reads.keys():
            
            if len(self.reads[key]) < self.ends:

                try:
                    self.reads[key].append(self.sam.mate(self.reads[key][0]))

                except ValueError:
                    unmatched.append(self.reads[key][0].query_name)
                    print("Mate not found for read {}".format(self.reads[key][0].query_name))
        
        for read in unmatched: self.reads.pop(read)

    def record_number(self):

        return len(self.reads.keys())

    def dump_to_file(self, out_dir):
        """
            Dumps records in self.reads to a bam file

            Args:
                out_dir(str): path to directory
        """
        out_dir = parse_path(out_dir, file_type = "dir")
        out_name = out_dir.joinpath("mutacc_" + self.file_name)
        out_bam = pysam.AlignmentFile(out_name, 'wb', template = self.sam)

        for key in self.reads.keys():
            if len(self.reads[key]) == self.ends:
                for read in self.reads[key]: out_bam.write(read)
       
        
        out_bam.close()
        return str(out_name)

    #This method may be implemented using picard FilterSamReads or another faster command line
    #option later, rather than using pysam. 
    def dump_to_exclude_file(self, out_dir):
        """
            Writes bam file, excluding the reads in self.reads

            Args:
                out_dir(str): path to directory
        """
        names = set(self.reads.keys())

        out_dir = parse_path(out_dir, file_type = "dir")
        out_name = out_dir.joinpath("mutacc_" + self.file_name)
        out_bam = pysam.AlignmentFile(out_name, 'wb', template = self.sam)

        for count, read in enumerate(self.sam):
            
            if count%1e6 == 0:
                print("##### {}M READS PROCESSED #####".format(count/1e6), end = "\r")

            if read.query_name not in names:

                out_bam.write(read)

        out_names.close()                

