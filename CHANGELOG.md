# Change Log
All notable changes to this project will be documented in this file.

## []
### Added
- A docker-compose file that loads demo data on a MongoDB instance and exports results to host current directory
### Changed
- Dockerfile now based on a miniconda3 image and commands are runned from non-root user

## [1.3.0]

### Added
- User can specify what meta data to import/export from the vcf in a yaml file

## [1.2.1]

### Changed

- mutacc dumps files as json files for later import

### Added
- Padding is calculated with regards to the read lengths in the bam file. The aim
is to get an actual padding of 1000 bp around the variant region.
- The binaries of the external tools picard, and seqkit can be given in the config file.
- Case can be uploaded again if '--replace' flag is given when importing
- fastq-reads gets versioned by time of creation
- added a demo option
- .github dir with CODEOWNERS and PULL_REQUEST_TEMPLATE
- version command, taking a directory as input, version dataset and loads it to database

### Fixed

## [1.1.0]
- First release of mutacc
