"""
    Module for writing vcf files
"""
import logging

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


def vcf_writer(found_variants, vcf_path, sample_name, adapter, variant_info_spec=None):

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

        if variant_info_spec is not None:
            write_info_header(variant_info_spec, vcf_handle)
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

            if variant_info_spec is not None:
                if variant_info_spec.get("variant"):
                    info_list.extend(
                        get_meta_info_from_dict(case, variant_info_spec["case"])
                    )
                if variant_info_spec.get("case"):
                    info_list.extend(
                        get_meta_info_from_dict(variant, variant_info_spec["variant"])
                    )

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


def get_meta_info_from_dict(input_dict: dict, variant_info_spec: list):
    """
        Get meta data from case that should be included in the INFO column

        Args:
            input_dict (dict): Dictionary to get info from
            variant_info_spec (dict): Dict specifying fields to extract into vcf

        Returns:
            (list): VCF INFO list
    """

    info_list = []
    for field in variant_info_spec:
        # print(field)
        in_id, out_id = field["id"].replace(" ", "").split(",")
        if input_dict.get(in_id) is not None:
            info_list.append(f"{out_id}={input_dict[in_id]}")
    return info_list


def write_info_header(variant_info_spec, vcf_handle):

    """
        Writes headers for INFO ids

        Args:
            variant_info_spec (dict): Dict specifying fields to extract into vcf
            vcf_handle (file handle): file handle to vcf_file

    """
    template = '##INFO=<ID={},Number=1,Type={},Description="{}">\n'
    for key in variant_info_spec.keys():
        for field in variant_info_spec[key]:
            vcf_id = field["id"].replace(" ", "").split(",")[-1]
            vcf_type = field["type"]
            vcf_desc = field["description"]
            vcf_handle.write(template.format(vcf_id, vcf_type, vcf_desc))


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
