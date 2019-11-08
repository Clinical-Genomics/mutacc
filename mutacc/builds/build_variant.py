"""
    Module with for building variant objects from a vcf
"""
import logging

from cyvcf2 import VCF
import yaml

from mutacc.parse.path_parse import parse_path

LOG = logging.getLogger(__name__)


class Variant(dict):

    """
        Class to represent variant
    """

    def __init__(self, vcf_entry, samples, padding, parser=None, rank_model_version=None):

        super(Variant, self).__init__()

        self.entry = vcf_entry
        self.samples = samples

        self.build_variant_object(padding, rank_model_version=rank_model_version)
        self.entry = str(self.entry)

        if parser is not None:
            self.update(parser.parse(vcf_entry))

    def _find_region(self, padding):
        """
            Given a vcf entry, this function attempts to return the relevant genomic regions
            to where the reads aligned that supports the given variant.

            Args:

                padding (int): given in bp, extends the region for where to look for reads in the
                alignment files.

            Returns:

                vtype (str): variant type
                region (dict): dictionary holding the start and end coordinates for a genomic region

        """

        #For variants with an ID 'SVTYPE' in the INFO field of the vcf entry
        start, end = self._find_start_end()

        region = {"start": start - padding,
                  "end": end + padding}

        return region

    def _find_type(self):

        variant_type = None
        variant_subtype = None

        if self.entry.INFO.get('TYPE') is not None:
            variant_type = 'SNV'
            variant_subtype = self.entry.INFO['TYPE']
        elif self.entry.INFO.get('SVTYPE') is not None:
            variant_type = 'SV'
            variant_subtype = self.entry.INFO['SVTYPE']

        return variant_type, variant_subtype

    def _find_start_end(self):
        start = self.entry.start
        if self.entry.INFO.get('END'):
            end = self.entry.INFO.get('END')
        else:
            end = self.entry.end
        return (int(start), int(end))


    def _find_genotypes(self):

        """
            Finds genotype calls for each sample, using the GT, DP, GQ, AD fields

        """

        samples = {}
        for i in range(len(self.samples)):

            sample_id = self.samples[i]

            #IDs from sample specific genotype field
            sample = {

                'GT': resolve_cyvcf2_genotype(self.entry.genotypes[i]),
                'DP': int(self.entry.gt_depths[i]),
                'GQ': int(self.entry.gt_quals[i]),
                'AD': int(self.entry.gt_alt_depths[i])

            }

            samples[sample_id] = sample

        return samples

    def build_variant_object(self, padding, rank_model_version=None):
        """
            makes a dictionary of the variant to be loaded into a mongodb
        """

        #Find genotype and sample id for the samples given in the vcf file
        region = self._find_region(padding)
        samples = self._find_genotypes()
        variant_type, variant_subtype = self._find_type()

        self['display_name'] = self.display_name
        self['variant_type'] = variant_type
        self['variant_subtype'] = variant_subtype
        self['alt'] = self.entry.ALT
        self['ref'] = self.entry.REF
        self['chrom'] = self.entry.CHROM
        self['start'] = self.entry.start
        self['end'] = self.entry.end
        self['vcf_entry'] = str(self.entry)
        self['reads_region'] = region
        self['samples'] = samples
        self['padding'] = padding

        #Add rank_model_version if given
        if rank_model_version is not None:
            self['rank_model_version'] = rank_model_version

    @property
    def display_name(self):

        """
            Make display name <chrom>_<pos>_<ref>_<alt>
        """

        display_name = '_'.join(
            [
                self.entry.CHROM,
                str(self.entry.POS),
                self.entry.REF,
                self.entry.ALT[0]
            ]
        )

        return display_name


class INFOParser:
    """
        Class to customize parsing of INFO column in vcf
    """

    def __init__(self, parser_info_file):

        with open(parser_info_file) as parser_handle:
            parse_info = yaml.load(parser_handle, Loader=yaml.FullLoader)
            self.parsers = self._get_parsers(parse_info)


    def parse(self, vcf_entry):
        """
            Given a vcf entry, parse the INFO column

            args:
                vcf_entry (Cyvcf2.Variant)
            returns:
                results (dict): Dictionary with the parsed fields
        """
        results = {}
        for parser in self.parsers:
            if vcf_entry.INFO.get(parser['id']):
                info_id = parser['id']
                display_name = parser['display_name']
                parser_func = parser['parse_func']
                results[display_name] = parser_func(vcf_entry.INFO.get(info_id))
        return results

    def _get_parsers(self, parse_info):
        """
            Gets a parser for each ID specified

            args:
                parse_info (list(dict)): list where each element gives specifications
                    on how an ID in the INFO column should be parsed

            returns:
                parsers (list): list of parsers
        """

        if not self._check(parse_info):
            LOG.warning('Parser info not given correctly')
            raise ValueError

        parsers = []
        for entry in parse_info:
            parser = {}
            parser['id'] = entry['id']
            parser['display_name'] = entry.get('out_name') or entry['id']
            parser['parse_func'] = self._construct_parser(entry)
            parsers.append(parser)
        return parsers

    @staticmethod
    def _construct_parser(entry):
        """
            Constructs python function that based on the specifications
            given parses an id in the INFO column of the vcf.

            args:
                entry (dict): dictionary with instructions on how id is parsed
            returns:
                parser_func (function): Function that parse ID in INFO column
        """

        def _type_conv(type_str=None):
            if type_str == 'str':
                return lambda value: str(value)
            if type_str == 'int':
                return lambda value: int(value)
            if type_str == 'list':
                return lambda value: list(value)
            if type_str == 'float':
                return lambda value: float(value)
            return lambda value: value

        def _parser_func(raw_value):
            if entry['multivalue']:
                info_list = []
                for raw_value_entry in raw_value.split(entry['separator']):
                    info_dict = {}
                    if entry.get('format_separator'):
                        for target, value in zip(entry['format'].split(entry['format_separator']),
                                                 raw_value_entry.split(entry['format_separator'])):
                            target = target.strip()
                            if entry['target'] == 'all' or target in entry['target']:
                                info_dict[target] = value
                    info_list.append(info_dict)
                return _type_conv(entry.get('out_type'))(info_list)
            else:
                if entry.get('format') and entry.get('format_separator'):
                    for target, value in zip(entry['format'].split(entry['format_separator']),
                                             raw_value.split(entry['format_separator'])):
                        target = target.strip()
                        if target in entry['target']:
                            return _type_conv(entry.get('out_type'))(value)
                else:
                    return _type_conv(entry.get('out_type'))(raw_value)


        return _parser_func

    def _check(self, parse_info):

        """
            Checks if parse info is given in the correct format
        """

        if not isinstance(parse_info, list):
            LOG.warning("parser info must be given as a list")
            return False

        for entry in parse_info:

            if not isinstance(entry, dict):
                LOG.warning("Each entry must be a dictionary")
                return False

            if entry.get('multivalue', False) and not entry.get('separator', False):
                LOG.warning("a separator must be given if multivalue is set to True")
                return False

        return True





def resolve_cyvcf2_genotype(cyvcf2_gt):
    """
        Given a genotype given by cyvcf2, translate this to a valid
        genotype string.

        Args:
            cyvcf2_gt (cyvcf2.variant.genotypes)

        Returns:
            genotype (str)
    """

    if cyvcf2_gt[2]:
        separator = '|'
    else:
        separator = '/'
    if cyvcf2_gt[0] == -1:
        a_1 = '.'
    else:
        a_1 = str(cyvcf2_gt[0])
    if cyvcf2_gt[1] == -1:
        a_2 = '.'
    else:
        a_2 = str(cyvcf2_gt[1])
    genotype = a_1 + separator + a_2

    return genotype


def get_variants(vcf_file, padding, rank_model_version=None, vcf_parse=None):

    """

        Given a vcf file, this function parses through the file and yields the variant with all
        relevant information

        Args:
            vcf_file (string): Path to vcf file

        Yields:
            variant (mutacc.builds.build_variant.Variant): Variant object
    """

    vcf_file = parse_path(vcf_file)
    vcf = VCF(str(vcf_file), 'r')
    samples = vcf.samples
    parser = None
    if vcf_parse:
        parser = INFOParser(vcf_parse)
    for entry in vcf:
        yield Variant(entry, samples, padding, parser=parser, rank_model_version=rank_model_version)
    vcf.close()
