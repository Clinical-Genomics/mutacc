# mutacc

## The mutation accumulation database

mutacc is a tool that makes it possible to create synthetic datasets to be used
for quality control or benchmarking of bioinformatic tools and pipelines intended
for variant calling. Using raw reads that supports a known variant from a real
NGS data, mutacc creates validation sets with true positives with the same
properties as a real life NGS run.

## Installation

```bash
git clone https://github.com/adrosenbaum/mutacc
cd mutacc
python setup.py install
```
## Usage

### Populate the mutacc database

To export data sets from the mutacc DB, the database must first be populated. To
extract the raw reads supporting a known variant, mutacc takes use of all
relevant files generated from a NGS experiment up to the variant calling itself.
That is the fastq files, bam file, and vcf file containing only the variants of
interest. 

This information is specified as a 'case', represented in yaml format

```python
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
    mother: 'sample2'    #REQUIRED (CAN BE None) 
    father: 'sample3'    #REQUIRED (CAN BE None)
    fastq_files:         #REQUIRED (LIST OF FASTQ PATHS FOR SAMPLE)
      - /path/to/fastq/fastq1
      - /path/to/fastq/fastq2
    bam_file: /path/to/sorted_bam #REQUIRED
    phenotype: 'affected'

  - sample_id: 'sample2'
    analysis_type: 'wgs'
    sex: 'female'        
    mother: None           
    father: None         
    fastq_files:    
      - /path/to/fastq/fastq1
      - /path/to/fastq/fastq2
    bam_file: /path/to/sorted_bam
   
  - sample_id: 'sample2' 
    analysis_type: 'wgs'
    sex: 'male'         
    mother: None             
    father: None            
    fastq_files:       
      - /path/to/fastq/fastq1
      - /path/to/fastq/fastq2
    bam_file: /path/to/sorted_bam 
  
#PATH TO VCF FILE CONTAINING VARIANTS OF INTEREST FROM CASE
variants: /path/to/vcf
```
 
To import the case into the database 

```bash
mutacc import --case <case.yaml> 
```

This will try to establish a connection to an instance of mongodb, by default
running on 'localhost' on port 27017. If this is not wanted, it can be specified
with the -h and -p options.
 
```bash
mutacc -h <host> -p <port> import --case <case.yaml> 
```

or in a configuration file e.g.
```python
#EXAMPLE OF A CONFIGURATION FILE
host: <host>
port: <port>
```

```bash
mutacc --config_file <config.yaml> import --case <case.yaml>
```

The generated fastq files containing the reads supporting the given variants
will not be stored in the database itself, but pointed to a by a path to the
file system. By default, the fastq files will be stored in the directory
~/mutacc_fastqs/. If another directory is wanted this can be required with the
--mutacc_dir option or as an entry 'mutacc_dir' in the configuration file.
   
### Export datasets from the database
TODO...

###Requirements

Python >3.6

see requirements.txt




 
