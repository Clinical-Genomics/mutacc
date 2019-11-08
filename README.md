# mutacc
[![Build Status](https://travis-ci.org/Clinical-Genomics/mutacc.png)](https://travis-ci.org/Clinical-Genomics/mutacc)
[![Coverage Status](https://coveralls.io/repos/github/Clinical-Genomics/mutacc/badge.svg?branch=master)](https://coveralls.io/github/Clinical-Genomics/mutacc?branch=master)
[![PyPI version](https://badge.fury.io/py/mutacc.svg)](https://badge.fury.io/py/mutacc)

## The mutation accumulation database

**mutacc** is a tool that makes it possible to create synthetic datasets to be used
for quality control or benchmarking of bioinformatic tools and pipelines intended
for variant calling of clinical variants. Using raw reads that supports a known
variant from a real NGS data, *mutacc* stores the relevant reads from each case into
a database. This database can then be queried to create synthetic datasets that can
be used as positive controls bioinformatics pipelines.

## Installation
### Conda
For installation of mutacc and the external prerequisites, this is made easy by
creating conda environment

```consol
conda create -n <env_name> python=3.6 pip numpy cython
```

activate environment

```consol
source activate <env_name>
```
### External Prerequisites
mutacc takes use of two external packages, [seqkit](https://github.com/shenwei356/seqkit)>=v0.9 ,
and [picard](https://github.com/broadinstitute/picard)>=v2.18. These can be
installed within a conda environment by

```console
conda install -c bioconda picard
conda install -c bioconda seqkit
```

### Install mutacc
Within the conda environment, do

```console
pip install mutacc
```

To install from PyPI, or clone this repo and install

```console
pip install git+https://github.com/Clinical-Genomics/mutacc
```

## Usage

### Configuration File

Some options are best passed to mutacc through a configuration file. below is an
example of a config file, using the YAML format.

```yaml
#EXAMPLE OF A CONFIGURATION FILE
host: <host>                  #Defaults to 'localhost'
port: <port>                  #Defaults to 27017
database: <database_name>     #Defaults to 'mutacc'
username: <username>          
password: <password>          
root_dir: <path_to_root>  
```

The 'root_dir' entry specifies an existing directory in the file system, where
all files generated by mutacc will be stored in corresponding subdirectories.
E.g. all generated fastq files will be stored in /.../root_dir/reads/


### Populate the mutacc database

To export data sets from the mutacc DB, the database must first be populated. To
extract the raw reads supporting a known variant, mutacc takes use some
relevant files generated from a NGS experiment up to the variant calling itself.
That is the bam file, and vcf file containing only the variants of interest.

This information is specified as a 'case', represented in yaml format

```yaml
#EXAMPLE OF A CASE

#THE CASE FIELD CONTAINS METADATA OF THE CASE ITSELF
case:
    case_id: 'case123' #REQUIRED CASE_ID

#LIST OF THE SAMPLES INVOLVED IN THE EXPERIMENT (MAY BE ONE, OR SEVERAL, E.G.
#A TRIO)
samples:
  - sample_id: 'sample1' #REQUIRED
    analysis_type: 'wgs' #REQUIRED
    sex: 'male'          #REQUIRED
    mother: 'sample2'    #REQUIRED (CAN BE 0 if no mother)
    father: 'sample3'    #REQUIRED (CAN BE 0 if no father)
    bam_file: /path/to/sorted_bam #REQUIRED
    phenotype: 'affected'

  - sample_id: 'sample2'
    analysis_type: 'wgs'
    sex: 'female'        
    mother: '0' #0 if no parent            
    father: '0'         
    bam_file: /path/to/sorted_bam
    phenotype: 'unaffected'

  - sample_id: 'sample2'
    analysis_type: 'wgs'
    sex: 'male'         
    mother: '0'             
    father: '0'            
    bam_file: /path/to/sorted_bam
    phenotype: 'affected'

#PATH TO VCF FILE CONTAINING VARIANTS OF INTEREST FROM CASE
variants: /path/to/vcf
```

This will find the reads from the bam files specified for each sample. If it
is desired that the reads are found from the fastq files instead, this can be
done by specifying the fastq-files as such

```yaml
  - sample_id: 'sample1'
    analysis_type: 'wgs'
    sex: 'male'          
    mother: 'sample2'    
    father: 'sample3'    
    bam_file: /path/to/sorted_bam
    fastq_files:
      - /path/to/fastq1
      - /path/to/fastq2
    phenotype: 'affected'
```
To extract the reads from the case

```console
mutacc --config-file <config_file> extract --padding 600 --case <case_file>
```
the --padding option takes the number of basepairs that the desired region is
padded with.

This will create a file <case_id>.json stored in the directory specified in the
/.../root_dir/imports directory.

To import the case into the database

```console
mutacc db import /.../root_dir/imports/<case_id>.json
```

The db command is called each time mutacc needs to do any operation against the
database.

This will try to establish a connection to an instance of mongodb, by default
running on 'localhost' on port 27017. If this is not wanted, it can be specified
with the --host and --port options.



```console
mutacc db -h <host> -p <port> import <case_id>.json
```

If authentication is required, this can be specified with the --username and
--password options.

or in a configuration file e.g.
```yaml
host: <host>
port: <port>
username: <username>
password: <password>
```

```console
mutacc --config-file <config.yaml> db import <case_id>.json
```


### Export datasets from the database
The datasets are exported one sample at the time. To export a synthetic
dataset, the export command is used together with options.
```
Usage: mutacc db export [OPTIONS]

  exports dataset from DB

Options:
  -c, --case-mongo TEXT           mongodb query language json-string to query
                                  for cases in database
  -v, --variant-mongo TEXT        mongodb query language json-string to query
                                  for variants in database
  -t, --variant-type TEXT         Type of variant
  -a, --analysis [wes|wgs]        Type of analysis
  --all-variants                  Export all variants in database
  -m, --member [father|mother|child|affected]
                                  Type of sample
  -s, --sex [male|female]         Sex of sample
  --vcf-dir PATH                  Directory where vcf is created. Defaults to
                                  mutacc-root/variants
  -p, --proband                   Variants from all affected samples,
                                  regardless of pedigree
  -n, --sample-name TEXT          Name of sample
  -j, --json-out                  Print results to stdout as json-string
  --help                          Show this message and exit.
```

example:

```console
mutacc --config-file <config.yaml> db export -m affected --all-variants
```
will find all the cases from the mutacc DB, and store this
information in a file /.../root_dir/queries/sample_name_query.mutacc.

to export an entire trio, this can be done by

```console
mutacc --config-file <config_file> db export -m child --all-variants -p -n child
mutacc --config-file <config_file> db export -m father --all-variants -n father
mutacc --config-file <config_file> db export -m mother --all-variants -n mother
```
This will create three files child_query_mutacc.json, father_query_mutacc.json, and
mother_query_mutacc.json.

the export subcommand will also generate a truth set vcf-file for each exported
samples, containing all queried variants.

To make a dataset (fastq-files) from a query file the synthesize command is used
with the following options

   -b/--background-bam \
    Path to the bam file for sample to be used as background

  -f/--background-fastq \
    Path to fastq file for sample to be used as background

  -f2/--background-fastq2 \
    Path to second fastq file (if paired end experiment)

  -q/--query \
    Path to the query json-files created with the export command

  --dataset-dir \
    Directory where fastq files will be stored. defaults to
    /.../root_dir/datasets


example, using the query files created above

```console
mutacc --config-file <config_file> synthesize -b <bam> -f <fastq1_child> -f2 <fastq2_child> -q child_query_mutacc.json
mutacc --config-file <config_file> synthesize -b <bam> -f <fastq1_father> -f2 <fastq2_father> -q father_query_mutacc.json
mutacc --config-file <config_file> synthesize -b <bam> -f <fastq1_mother> -f2 <fastq2_mother> -q mother_query_mutacc.json
```

The created fastq-files will be stored in the directory /.../root_dir/datasets/
or in directory specified by ---dataset-dir

### Remove case from database

To remove a case from the mutacc DB, and all the generated bam, and fastq files
generated from that case from disk, the remove command is used

```console
mutacc --config-file <config.yaml> db remove <case_id>
```
