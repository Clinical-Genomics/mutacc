# Change Log
All notable changes to this project will be documented in this file.

## [1.7.2]
### Fixed
- Picard version in Dockerfile to be 3.1.0

## [1.7.1]
### Fixed
- workflow step version in `docker_build_n_publish` GitHub action

## [1.7]
### Added
- Integration test with MongoDB v7 
### Changed
- Moved tests and coverage from Travis to GitHub actions
- Updated python version and versions of some GitHub actions
- Unfreeze cyvcf2 lib to be able to install the software with Python>=3.8
- Installation instructions on README page to install mutacc using Python 3.8
- Unfreeze pymongo requirement and removed deprecated pymongo code to support latest version of MongoDB
- Updated pythin version to 3.11 in Dockerfile
- Updated MongoDB version to 7 in docker-compose.yml file
### Fixed
- Badge on Readme page
- GitHub action to push the right image to Docker Hub
- Replaced deprecated `pkg_resources` lib with `importlib_resources`
- Path to app in tests_and_coverage.yml, coveralls step

## [1.6.3]
### Fixed
- Freeze PyMongo lib to version<4.0 to keep supporting previous MongoDB versions

## [1.6.2]
### Fixed
- Token name used by PyPI push action once again

## [1.6.1]
### Fixed
- Token name used by PyPI push action

## [1.6]
### Changed
- Build and use local Dockerfile when creating demo container in docker-compose
- Minify Docker image by adding a multi-stage build and manually installing Picard and the Java Virtual Machine
- Speed up Docker image building by basing it on another image with cyvcf2 already installed
### Fixed
- Parse yaml config files using `yaml.safe_load` to avoid `missing Loader error` due to deprecation introduced by PyYAML 6.0
- Typo in docker-compose file
- Fix mongo-adapter dependency to use version>=0.3.3. Previous versions have a way too short connection timeout and approximate URI log print

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
