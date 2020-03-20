PADDING = 300
SV_PADDING = 1000

SUB_DIRS = {

    #Subdirectory for the extracted reads from the cases
    #Here all reads will be stored according to
    #  reads
    #      |
    #      case1
    #      |   |
    #      |   sample1
    #      |   |     |
    #      |   |     fastq_files
    #      |   sample2
    #      |   |     |
    #      |   |     fastq_files
    #      |   sample2
    #      |         |
    #      |         fastq_files
    #      case2
    #      ...
    'read_dir': 'reads',

    #Subdirectory for vcfs, containing the exported variants
    'vcf_dir': 'variants',

    #Subdirectory for cases to be imported
    'import_dir': 'imports',

    #Subdirectory for queries
    'query_dir': 'queries',

    #Subdirectory for synthetic datasets
    'dataset_dir': 'datasets',

    #Subdirectory for temp files such as
    #the files containing read_IDs for search in fastq files
    #and the fastq_files with some excluded reads.
    'temp_dir': 'temporaries'

}
