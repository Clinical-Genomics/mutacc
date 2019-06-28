# Change Log
All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

- mutacc dumps files as json files for later import

### Added
- Padding is calculated with regards to the read lengths in the bam file. The aim
is to get an actual padding of 1000 bp around the variant region.
- The binaries of the external tools picard, and seqkit can be given in the config file.
- Case can be uploaded again if '--replace' flag is given when importing
- fastq-reads gets versioned by time of creation
- .github dir with CODEOWNERS and PULL_REQUEST_TEMPLATE

### Fixed

## [1.1.0]
- First release of mutacc
