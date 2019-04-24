# Change Log
All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Padding is calculated with regards to the read lengths in the bam file. The aim
is to get an actual padding of 1000 bp around the variant region.
- The binaries of the external tools picard, and seqkit can be given in the config file.

## [1.1.0]
- First release of mutacc
