"""
    Module for writing vcf files
"""
import logging

from mutacc.utils.vcf_handler import INFOParser

HEADER = (
    '##INFO=<ID=END,Number=1,Type=Integer,Description="Stop position of the interval">',
    '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant">',
    '##INFO=<ID=TYPE,Number=A,Type=String,Description="The type of allele, either snp, mnp, ins, del, or complex.">',
    '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
    '##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth (reads with MQ=255 or with bad mates are filtered)">',
    '##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">',
    '##FORMAT=<ID=AD,Number=R,Type=Integer,Description="Allelic depths for the ref and alt alleles in the order listed">',
)

FILEFORMAT = "##fileformat=VCFv4.2"

LOG = logging.getLogger(__name__)


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
        vcf_handle.write(FILEFORMAT + "\n")

        if vcf_parser is not None:
            write_info_header(vcf_parser, vcf_handle)
        for header_line in HEADER:
            vcf_handle.write(header_line + "\n")
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

            info = ";".join(info_list)
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
                gt_call.append("./.")

            format_list = ":".join(format_list)
            gt_call = ":".join(gt_call)

            vcf_entry = variant["vcf_entry"].strip("\n").split("\t")
            entry = (
                "\t".join(vcf_entry[0:7] + [info] + [format_list] + [gt_call]) + "\n"
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
        vcf_number = "." if field.get("multivalue") else "1"
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
        found_contigs.update(variant["chrom"])
        vcf_handle.write(template.format(variant["chrom"]) + "\n")
