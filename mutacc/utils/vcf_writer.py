
import logging

LOG = logging.getLogger(__name__)

def vcf_writer(found_variants, vcf_path, member):

    with open(vcf_path, "w") as vcf_handle:

        vcf_handle.write("##fileformat=VCFv4.2\n")
        vcf_handle.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{}\n".format(member))

        for variant in found_variants:

            genotype = variant.get("genotype") or './.'

            vcf_entry = variant["vcf_entry"].strip("\n").split("\t")
            entry = "\t".join(vcf_entry[0:8] + ["GT"] + [genotype]) + "\n"
            vcf_handle.write(entry)
