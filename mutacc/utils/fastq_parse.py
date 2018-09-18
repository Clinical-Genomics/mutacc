import gzip
from pathlib import Path
from contextlib import ExitStack

from Bio.SeqIO.QualityIO import FastqGeneralIterator

def fastq_extract(fastq_files: list, record_ids: list, dir_path = ''):

    """

        Given a list of read identifiers, and one or two (for paired end) fastq files, 
        creates new fastq files only containing the reads specified. 

        Args:
            
            fastq_files (list): List of fastqfiles
            record_ids (list): List of read identifiers
            dir_path (string): path to directory where new fastq files are written to
        
        Returns:

            out_paths (list): List of paths to newly created fastq files

    """


    file_names = [Path(file_name).name for file_name in fastq_files]
    dir_path = Path(dir_path).expanduser().absolute()

    if not dir_path.exists():
        raise FileNotFoundError('path not found:  %s' % (dir_path))

    with ExitStack() as stack:
        #Opens fastq files and places file handles in list fastq_handles
        fastq_handles = [stack.enter_context(get_file_handle(fastq_file)) \
                for fastq_file in fastq_files]
        
        #Opens fastq files to write
        out_handles = [stack.enter_context(open(dir_path.joinpath('ex_' + file_name), 'wt')) \
                for file_name in file_names]

        #parse fastq and places in list fastqs
        fastqs = [FastqGeneralIterator(handle) for handle in fastq_handles]

        #Iterates over parsed fastq files simultaneously
        for records in zip(*fastqs):

            if records[0][0].split()[0] in record_ids:
                
                for record, out_handle in zip(records, out_handles):

                    out_handle.write("@%s\n%s\n+\n%s\n" % (record[0], record[1], record[2]))

                record_ids.remove(records[0][0].split()[0])

                if len(record_ids) == 0:

                    break
        
        out_paths = [out_handle.name for out_handle in out_handles]

    return out_paths

      

def get_file_handle(file_name):
    
    file_name = Path(file_name).expanduser().absolute()


    if file_name.name.endswith('.gz'):

        return gzip.open(file_name, 'rt')
    
    else:

        return open(file_name, 'r')


