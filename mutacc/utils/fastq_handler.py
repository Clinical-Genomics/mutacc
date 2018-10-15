import gzip
import logging
from pathlib import Path
from contextlib import ExitStack

from Bio.SeqIO.QualityIO import FastqGeneralIterator

from mutacc.parse.path_parse import parse_path, get_file_handle

LOG = logging.getLogger(__name__)

def fastq_extract(fastq_files: list, record_ids: set, dir_path = ''):

    """

        Given a list of read identifiers, and one or two (for paired end) fastq files, 
        creates new fastq files only containing the reads specified. 

        Args:
            
            fastq_files (list): List of fastq files
            record_ids (set): Set of read names
            dir_path (string): path to directory where new fastq files are written to
        
        Returns:

            out_paths (list): List of paths to newly created fastq files

    """
    
    
    fastq_files = [parse_path(fastq_file) for fastq_file in fastq_files]

    #Save the file names for the fastq files to be used later
    file_names = [Path(file_name).name.split(".")[0] for file_name in fastq_files]

    #expanduser() expands paths including '~' to the full path to the users home directory
    #absolute() expands relative path to the absolute path 
    dir_path = parse_path(dir_path, file_type = 'dir')

    #Uses ExitStack context manager to manage a variable number of
    #files
    with ExitStack() as stack:
        #Opens fastq files and places file handles in list fastq_handles and Opens __exit__ method 
        # to the ExitStack callback stack.
        fastq_handles = [stack.enter_context(get_file_handle(fastq_file)) \
                for fastq_file in fastq_files]
        
        #Opens fastq files to write found records.
        out_handles = [stack.enter_context(gzip.open(dir_path.joinpath(file_name + "_mutacc" +
            ".fastq.gz"), 'wt')) \
                for file_name in file_names]
        
        #Making buffers
        #out_buffers = [RecordBuffer(out_handle, buffer_size = buffer_size) for out_handle in out_handles]

        #parse fastq and places in list fastqs
        #FastqGeneralIterator parses each record as a tuple with name, seq, and quality
        #on index 0, 1, 2 respectively.
        fastqs = [FastqGeneralIterator(handle) for handle in fastq_handles]
        
        records_found = 0
        #Iterates over parsed fastq files simultaneously
        for count, records in enumerate(zip(*fastqs)):
            
            #Checks if current record name exists in record_ids. This Check is only done for one of the
            #fastq files (records[0]). It is thus assumed that paired end reads exists on the same
            #position in the two files
            #Example: if records[0][0] is 'ST-E00266:38:H2TF5CCXX:8:1101:2563:2170 1:N:0:CGCGCATT',
            # records[0][0].split()[0] is 'ST-E00266:38:H2TF5CCXX:8:1101:2563:2170'
            if records[0][0].split()[0].split("/")[0] in record_ids:
                
                records_found += 1

                #Writes current records from each fastq file to corresponding output file
                for record, out_handle in zip(records, out_handles):

                    out_handle.write("@{}\n{}\n+\n{}\n".format(record[0], record[1], record[2]))
                
                #removes found record name from the record_ids set
                record_ids.remove(records[0][0].split()[0].split("/")[0]) 
                
                #If record_ids is empty all records have been found so there is no need to iterate
                #further over the fastq files
                if len(record_ids) == 0:

                    break
            
            if count%1e6 == 0:
                #TO BE REPLACED WITH PROPER PROGRESS BAR/STATUS OF SOME KIND
                LOG.info("##### {}M READS PROCESSED: {} READS FOUND #####\r".format(
                    count/1e6,
                    records_found)
                    )
        
        #for out_buffer in out_buffers: out_buffer.flush()

    #Returns the file paths for the output fastq files, that should only contain the records
    #with its record name in record_ids
        out_paths = [out_handle.name for out_handle in out_handles]

    return out_paths

#Does the reverse as the above function
def fastq_exclude(fastq_files: list, record_ids: set, dir_path = ''):

    """

        Given a list of read identifiers, and one or two (for paired end) fastq files, 
        creates new fastq files excluding the reads specified. 

        Args:
            
            fastq_files (list): List of fastq files
            record_ids (set): Set of read names
            dir_path (string): path to directory where new fastq files are written to
        
        Returns:

            out_paths (list): List of paths to newly created fastq files

    """
    
    
    fastq_files = [parse_path(fastq_file) for fastq_file in fastq_files]

    file_names = [Path(file_name).name.split(".")[0] for file_name in fastq_files]

    dir_path = parse_path(dir_path, file_type = 'dir')

    with ExitStack() as stack:
        fastq_handles = [stack.enter_context(get_file_handle(fastq_file)) \
                for fastq_file in fastq_files]
        
        out_handles = [stack.enter_context(gzip.open(dir_path.joinpath(file_name + "_mutacc" +
            ".fastq.gz"), 'wt')) \
                for file_name in file_names]
        
        #out_buffers = [RecordBuffer(out_handle, buffer_size = buffer_size) for out_handle in out_handles]

        fastqs = [FastqGeneralIterator(handle) for handle in fastq_handles]
        
        record_count = 0
        for count, records in enumerate(zip(*fastqs)):
            #only difference from extract function above; here we want to find records with read
            #names NOT IN the record_ids            
            if records[0][0].split()[0].split("/")[0] not in record_ids:
                
                for record, out_handle in zip(records, out_handles):

                    out_handle.write("@{}\n{}\n+\n{}\n".format(record[0], record[1], record[2]))
                
            if count%1e6 == 0:
                print("##### {}M READS PROCESSED #####".format(count/1e6), end="\r")
        
        #for out_buffer in out_buffers: out_buffer.flush()

        out_paths = [out_handle.name for out_handle in out_handles]

    return out_paths

#To avoid writing to disk too many times (especially when using the fastq_exclude function)
#This buffer holds the fastq records and writes to disk when it is sufficiently large.
class RecordBuffer:

    def __init__(self, write_handle, buffer_size = 5000):
        """
            Buffer for fastq records

            Args:
                write_handle(file_handle): file handle opened with 'w' for output file
                buffer_size(int): size of maximum records to store in memory

        """
        self.buffer = ""
        self.record_count = 0
        self.write_handle = write_handle
        self.buffer_size = buffer_size

    def add(self, record):
        """
            adds record to buffer

            Args:
                record(string): record to be added to buffer
        """
        self.buffer += record
        self.record_count += 1

        if self.record_count == self.buffer_size:

            self.flush()

    def flush(self):
        """
            Flushing buffer to write_handle
        """
        self.write_handle.write(self.buffer)
        self.buffer = ""
        self.record_count = 0
        


