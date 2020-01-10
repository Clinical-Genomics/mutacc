"Module to handle vcf files"

import logging

import yaml

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

    def parse(self, vcf_entry):
        """
            Given a vcf entry, parse the INFO column

            args:
                vcf_entry (Cyvcf2.Variant or dict)
            returns:
                results (dict): Dictionary with the parsed fields
        """

        if self.stream == "r":
            results = {}
            for parser in self.parsers:
                if vcf_entry.INFO.get(parser["id"]):
                    info_id = parser["id"]
                    display_name = parser["display_name"]
                    parser_func = parser["parse_func"]
                    results[display_name] = parser_func(vcf_entry.INFO.get(info_id))
            return results

        results = []
        for parser in self.parsers:
            if vcf_entry.get(parser["id"]):
                info_id = parser["id"]
                parser_func = parser["parse_func"]
                results.append(parser_func(vcf_entry[info_id]))
        return ";".join(results)

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
        for entry in parse_info:
            parser = {}
            parser["id"] = entry["id"]
            parser["display_name"] = entry.get("out_name") or entry["id"]
            if self.stream == "r":
                parser["parse_func"] = self._construct_parser(entry)
            else:
                parser["parse_func"] = self._construct_writer(entry)
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
            if type_str == "str":
                return lambda value: str(value)
            if type_str == "int":
                return lambda value: int(value)
            if type_str == "list":
                return lambda value: list(value)
            if type_str == "float":
                return lambda value: float(value)
            return lambda value: value

        def _parser_func(raw_value):
            if entry["multivalue"]:
                info_list = []
                for raw_value_entry in raw_value.split(entry["separator"]):
                    element = None
                    if entry.get("format_separator"):
                        info_dict = {}
                        for target, value in zip(
                            entry["format"].split(entry["format_separator"]),
                            raw_value_entry.split(entry["format_separator"]),
                        ):
                            target = target.strip()
                            if entry["target"] == "all" or target in entry["target"]:
                                info_dict[target] = value
                        element = info_dict
                    else:
                        element = raw_value_entry
                    info_list.append(element)
                return _type_conv(entry.get("out_type"))(info_list)
            else:
                if entry.get("format") and entry.get("format_separator"):
                    for target, value in zip(
                        entry["format"].split(entry["format_separator"]),
                        raw_value.split(entry["format_separator"]),
                    ):
                        target = target.strip()
                        if target in entry["target"]:
                            return _type_conv(entry.get("out_type"))(value)
                else:
                    return _type_conv(entry.get("out_type"))(raw_value)

        return _parser_func

    @staticmethod
    def _construct_writer(entry):
        """
            Constructs python function that based in key, value pairs in a dictionary
            creates a INFO entry string in the vcf format

            args:
                entry (dict): dictionary with instructions on how id is parsed
            returns:
                parser_func (function): Function that parse ID in INFO column

        """

        def _writer_func(raw_value):

            info_list = []
            if not isinstance(raw_value, (list, tuple)):
                raw_value = [raw_value]
            for element in raw_value:
                if (
                    entry.get("target")
                    and entry.get("format_separator")
                    and isinstance(element, dict)
                ):
                    target_list = (
                        list(element.keys())
                        if entry["target"] == "all"
                        else entry["target"]
                    )
                    info_list.append(
                        entry["format_separator"].join(
                            [str(element[target]) for target in target_list]
                        )
                    )

                elif isinstance(element, (list, tuple)) and entry.get(
                    "format_separator"
                ):
                    info_list.append(
                        entry["format_separator"].join([str(item) for item in element])
                    )

                elif isinstance(element, (int, float, str)):
                    info_list.append(str(element))

            info_entry = f"{entry['out_name']}={','.join(info_list)}"
            return info_entry

        return _writer_func

    @staticmethod
    def _check(parse_info):

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

            if entry.get("multivalue", False) and not entry.get("separator", False):
                LOG.warning("a separator must be given if multivalue is set to True")
                return False

            if entry.get("target") and not (
                isinstance(entry["target"], list) or entry["target"] == "all"
            ):
                LOG.warning("target must be a list")
                return False

        return True
