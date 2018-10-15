#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

import pysam

from mutacc.parse.path_parse import parse_path

LOG = logging.getLogger(__name__)

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
    def __init__(self, bam_file, out_dir = None, ends:int = 2):
        """
            Args:
                bam_file(str): path to bam file 
                ends(int): 2 if paired end reads, 1 if not
        """
        bam_file = parse_path(bam_file)
        self.file_name = bam_file.name
        self.sam = pysam.AlignmentFile(bam_file, 'rb') #Make AlignmentFile object
        self.reads = {} #Dictionary to store read pairs under their query_name as key
        self.ends = ends 
        self.found_reads = set() #Set of query names where both mates are found
        if out_dir: #If out_dir is given, open a file to write found records
            self.out_dir = parse_path(out_dir, file_type = "dir")
            self.out_name = out_dir.joinpath("mutacc_" + self.file_name)
            self.out_bam = pysam.AlignmentFile(self.out_name, 'wb', template = self.sam)

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.sam.close()
        
        #If out_dir is given, also close the out_bam file created in __init__
        if self.out_dir: self.out_bam.close()

    def find_reads_from_region(self, chrom, start, end):
        """
            Given a region defined by chrom, start, end, find all reads, and mates to those reads 
            overlapping with this region.

            Args:
                chrom(str): chromosome/contig name
                start(int): start position
                end(int): end position
        """
        #Fetch iterator for reads in given region
        for read in self.sam.fetch(chrom, start, end):
            #If name of read not among the keys in reads dict AND if both mates have not been found
            #allready make list to hold mates
            if read.query_name not in self.reads.keys() and read.query_name not in self.found_reads: 
                
                self.reads[read.query_name] = []
            #If both mates are not found allready, append read to mate list in reads
            #and write to bam_out. Remove mates from reads dictionary, and add name to found_reads
            if read.query_name not in self.found_reads:       

                self.reads[read.query_name].append(read)

                if len(self.reads[read.query_name]) == self.ends: 

                    self.found_reads = self.found_reads.union({read.query_name})
                    
                    #Write to file only if a out_dir is given in __init__
                    if self.out_dir:
                        for mate in self.reads[read.query_name]: self.out_bam.write(mate)

                    self.reads.pop(read.query_name)

        
        #Find the mates of the reads not found in the same region
        keys = list(self.reads.keys())
        for key in keys:
            
            try:
                self.reads[key].append(self.sam.mate(self.reads[key][0]))

                if self.out_dir: 
                    for mate in self.reads[key]: self.out_bam.write(mate)
                self.reads.pop(key)
                self.found_reads = self.found_reads.union({key})

            #AlignmentSegment.mate raises ValueError if mate can not be found
            #If mate is not found, the single read is not added to the out_bam file
            #(Unless ends argument in __init__ is not set to 1)
            except ValueError:
                LOG.warning("Mate not found for read {}".format(key))
        
        
    @property
    def record_number(self):

        return len(self.found_reads)

    @property
    def out_file(self):

        return str(self.out_name)

    #This method may be implemented using picard FilterSamReads or another faster command line
    #option later, rather than using pysam. Currently this iterates through all records in a bam
    #file and writes the records with names not given in self.found_reads to a new bam. This is
    #however not much more efficient than to search for reads in fastq files.
    def dump_to_exclude_file(self, out_dir):
        """
            Writes bam file, excluding the reads in self.reads

            Args:
                out_dir(str): path to directory
        """

        out_dir = parse_path(out_dir, file_type = "dir")
        out_name = out_dir.joinpath("mutacc_" + self.file_name)
        out_bam = pysam.AlignmentFile(out_name, 'wb', template = self.sam)

        for count, read in enumerate(self.sam):
            
            if count%1e6 == 0:
                LOG.info("##### {}M READS PROCESSED #####\r".format(count/1e6))

            if read.query_name not in self.found_reads:

                out_bam.write(read)

        out_names.close()                

