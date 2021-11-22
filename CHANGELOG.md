# Change Log
All notable changes to this project will be documented in this file.

## []
### Changed
- Build and use local Dockerfile when creating demo container in docker-compose
- Optimize Dockerfile by adding multi-stage vuild and basing builder on pre-existing cyvcf2 image
### Fixed
- Parse yaml config files using `yaml.safe_load` to avoid `missing Loader error` due to deprecation introduced by PyYAML 6.0
- Typo in docker-compose file

## [1.5]
### Added
- A docker-compose file that loads demo data on a MongoDB instance and exports results to the current directory of the user
- GitHub action building a repo image and pushing it to Docker Hub when a new release is published
- A command line option to allow mongo URI connections (already supported from config file)
- GitHub action building the software and publishing it to PyPI when a new release is published
### Changed
- Dockerfile now based on a miniconda3 image with commands runned as a non-root user

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
