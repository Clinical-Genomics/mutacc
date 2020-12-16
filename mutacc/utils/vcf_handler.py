"Module to handle vcf files"

import logging

import yaml

from .constants import (
    COLON,
    COMMA,
    DOT,
    EQUALS,
    NEW_LINE,
    PIPE,
    SEMICOLON,
    SLASH,
    TAB,
    TYPES,
    VCF_FILEFORMAT,
    VCF_HEADER
)


LOG = logging.getLogger(__name__)


class INFOParser:
    """
        Class to customize parsing of INFO column in vcf
    """

    def __init__(self, parser_info: list, stream: str):

        if stream.lower() not in ("read", "write", "r", "w"):
            LOG.warning("The stream must be set to either 'read' or 'write' ")
        self.stream = stream.lower()[0]

        if not self._check(parser_info):
            LOG.warning("Parser info not given correctly")
            raise ValueError

        self.parsers = self._get_parsers(parser_info)

    def parse(self, record):
        """
            Given a vcf entry, parse the INFO column

            args:
                record (Cyvcf2.Variant or dict)
            returns:
                results (dict): Dictionary with the parsed fields or string if
                    stream = 'r'
        """

        if self.stream == "r":
            return self._read_vcf_record(record)

        return self._read_mongodb_record(record)

    def _read_vcf_record(self, record):
        """
            Parses a value from the INFO column to python dictionary

            Args:
                record (cyvcf2.Records): vcf record
            Returns:
                results (dict): dictionary with parsed value
        """

        results = {}
        for parser in self.parsers:
            info_id = parser["id"]
            display_name = parser["display_name"]
            if record.INFO.get(info_id):
                info_raw_value = record.INFO[info_id]
                results[display_name] = self._parser_func(
                    info_raw_value, parser["parse_info"]
                )
        return results

    def _read_mongodb_record(self, record: dict):

        """
        Parses a python dictionary to a INFO string

        Args:
            record (dict): dictionary to be parsed into INFO string
        """
        results = []
        for parser in self.parsers:
            record_key = parser["id"]
            if record.get(record_key):
                record_value = record[record_key]
                results.append(self._writer_func(record_value, parser["parse_info"]))
        return SEMICOLON.join(results)

    def _get_parsers(self, parse_info):
        """
            Gets a parser for each ID specified

            args:
                parse_info (list(dict)): list where each element gives specifications
                    on how an ID in the INFO column should be parsed

            returns:
                parsers (list): list of parsers
        """

        parsers = []
        for element in parse_info:
            parser = {}
            parser["id"] = element["id"]
            parser["display_name"] = element.get("out_name") or element["id"]
            parser["parse_info"] = element
            parsers.append(parser)
        return parsers

    @staticmethod
    def _parser_func(raw_value: str, parse_info: dict):
        """
            Converts a vcf INFO value to dictionary based on parsing specifications

            Args:
                raw_value (str): INFO value string
                parse_info (dict): dictionary containing parse information
            Returns:
                (any): parsed value
        """
        if parse_info["multi_value"]:
            return _parse_multi_value(raw_value=raw_value, parse_info=parse_info)
        elif parse_info.get("format") and parse_info.get("format_separator"):
            format_str = parse_info["format"]
            format_separator = parse_info["format_separator"]
            targets = parse_info["target"]
            out_type = parse_info.get("out_type")
            return _parse_format(
                raw_value, format_str, format_separator, targets, out_type
            )
        else:
            if parse_info.get("out_type"):
                type_cast = TYPES[parse_info["out_type"]]
                return type_cast(raw_value)
            return raw_value

    @staticmethod
    def _writer_func(raw_value, parse_info: dict):
        """
            Converts a python value into INFO string based on parse specifications

            Args:
                raw_value (any): raw value to be converted to INFO string
                parse_indo (dicy): dictionary containing parse information
            Returns:
                (str): INFO string
        """

        info_list = []
        if not isinstance(raw_value, (list, tuple)):
            raw_value = [raw_value]
        format_separator = parse_info.get("format_separator") or PIPE
        for element in raw_value:
            if isinstance(element, dict):
                if parse_info.get("target"):
                    targets = parse_info["target"]
                else:
                    targets = list(element.keys())
                target_list = [str(element[target]) for target in targets]
                target_str = format_separator.join(target_list)
                info_list.append(target_str)

            elif isinstance(element, (list, tuple)):
                target_list = [str(item) for item in element]
                target_str = format_separator.join(target_list)
                info_list.append(target_str)

            elif isinstance(element, (int, float, str)):
                info_list.append(str(element))

        out_name = parse_info["out_name"] or parse_info["id"]
        info_field = get_vcf_info_field(info_list, out_name)
        return info_field

    @staticmethod
    def _check(parse_info: list):

        """
            Checks if parse info is given in the correct format

            Args:
                parse_info list(dict): list with parsers
            Returns:
                (bool): True oif parser info is given in right format, False if not
        """

        if not isinstance(parse_info, list):
            LOG.warning("parser info must be given as a list")
            return False

        for entry in parse_info:

            if not isinstance(entry, dict):
                LOG.warning("Each entry must be a dictionary")
                return False

            if entry.get("multi_value", False) and not entry.get("separator", False):
                LOG.warning("a separator must be given if multi_value is set to True")
                return False

            if entry.get("target") and not isinstance(entry["target"], list):
                LOG.warning("target must be a list")
                return False

        return True


def _parse_format(
    raw_value: str,
    format_str: str,
    format_separator: str,
    targets: list = None,
    out_type: str = None,
):
    """
    Parse a string with a specified format, format_separator, and target keys

    Args:
        raw_value_element (str): The string representation of the value as given in vcf
        format (str): string defining the format of the value
        format_separator (str): substring that separates values in string
        targets (list): list of targets
        out_type (str): datatype that value is casted to

    Returns:
        info_dict (dict): dictionary representation of value
    """
    type_cast = TYPES[out_type]
    info_dict = {}
    keys = format_str.split(format_separator)
    values = raw_value.split(format_separator)
    for key, value in zip(keys, values):
        key = key.strip()
        if (targets is None) or (key in targets):
            info_dict[key] = type_cast(value)
    return info_dict


def _parse_multi_value(raw_value: str, parse_info: dict):
    """
    Parse a multi_valued key from a vcf

    Args:
        raw_value (str): string from INFO key in vcf
        parse_info (dict): python dict with parse instruction for vcf key
    """
    separator = parse_info.get("separator") or COMMA
    info_list = []
    for raw_value_element in raw_value.split(separator):
        element = None
        if parse_info.get("format_separator") and parse_info.get("format"):
            format_separator = parse_info["format_separator"]
            format_str = parse_info["format"]
            targets = parse_info.get("target")
            element = _parse_format(
                raw_value_element, format_str, format_separator, targets
            )
        else:
            element = raw_value_element
        info_list.append(element)
    return info_list


def get_vcf_info_field(info_list: list, vcf_name: str):

    return f"{vcf_name}{EQUALS}{COMMA.join(info_list)}"


def vcf_writer(found_variants, vcf_path, sample_name, adapter, vcf_parser=None):

    """
        Given a list of variants documents from the database,
        write them in VCF format.

        Args:
            found_variants (list): list of variants (dicts) from the database.
                Here the variants dictionary has the extra key 'genotype', which
                hold an embedded dict with genotype call information specific to
                the sample.
            vcf_path (path): path to new vcf file
            sample_name (str): Name of sample
    """

    with open(vcf_path, "w") as vcf_handle:
        vcf_handle.write(VCF_FILEFORMAT + NEW_LINE)

        if vcf_parser is not None:
            write_info_header(vcf_parser, vcf_handle)
        for header_line in VCF_HEADER:
            vcf_handle.write(header_line + NEW_LINE)
        write_filter_headers(found_variants, vcf_handle)
        write_contigs(found_variants, vcf_handle)
        vcf_handle.write(
            f"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{sample_name}\n"
        )

        for variant in found_variants:
            case = adapter.find_case(query={"case_id": variant["case"]})
            # Write info field
            info = ""
            info_list = []
            info_list.append(f"END={variant['end']}")
            if variant["variant_type"].upper() == "SNV":
                info_list.append(f"TYPE={variant['variant_subtype']}")
            elif variant["variant_type"].upper() == "SV":
                info_list.append(f"SVTYPE={variant['variant_subtype']}")

            if vcf_parser is not None:
                parser = INFOParser(vcf_parser, stream="write")
                info_list.extend([parser.parse(case)])
                info_list.extend([parser.parse(variant)])

            info = SEMICOLON.join(info_list)
            # write format field and gt
            format_list = []
            gt_call = []

            # If genotype is given for sample
            if variant["genotype"]:
                for key in variant["genotype"].keys():

                    if variant["genotype"][key] != -1:
                        format_list.append(key)
                        gt_call.append(str(variant["genotype"][key]))

            # If variant entry has no genotype
            else:
                format_list.append("GT")
                gt_call.append(DOT + SLASH + DOT)

            format_list = COLON.join(format_list)
            gt_call = COLON.join(gt_call)

            vcf_entry = variant["vcf_entry"].strip(NEW_LINE).split(TAB)
            entry = (
                TAB.join(vcf_entry[0:7] + [info] + [format_list] + [gt_call]) + NEW_LINE
            )
            vcf_handle.write(entry)


def write_info_header(vcf_parser, vcf_handle):

    """
        Writes headers for INFO ids

        Args:
            variant_info_spec (dict): Dict specifying fields to extract into vcf
            vcf_handle (file handle): file handle to vcf_file

    """
    template = '##INFO=<ID={},Number={},Type={},Description="{}">\n'
    for field in vcf_parser:
        vcf_id = field["out_name"]
        vcf_type = field["vcf_type"]
        vcf_desc = field["description"]
        vcf_number = DOT if field.get("multi_value") else "1"
        vcf_handle.write(template.format(vcf_id, vcf_number, vcf_type, vcf_desc))


def write_contigs(variants, vcf_handle):
    """
        Writes contig headers

        Args:
            variants(list(dict)): list of variants
            vcf_handle (file handle): file handle to vcf_file
    """
    template = "##contig=<ID={}>"
    found_contigs = set()
    for variant in variants:
        if variant["chrom"] in found_contigs:
            continue
        found_contigs.add(variant["chrom"])
        vcf_handle.write(template.format(variant["chrom"]) + NEW_LINE)


def write_filter_headers(variants, vcf_handle):
    """
        Writes filter headers

        Args:
            variants(list(dict)): list of variants
            vcf_handle (file handle): file handle to vcf_file
    """
    template = '##FILTER=<ID={},Description="{}">\n'
    found_filters = {"PASS", DOT}
    for variant in variants:
        variant_filter = variant["vcf_entry"].strip(NEW_LINE).split(TAB)[6]
        if variant_filter in found_filters:
            continue
        found_filters.add(variant_filter)
        vcf_handle.write(template.format(variant_filter, variant_filter))
