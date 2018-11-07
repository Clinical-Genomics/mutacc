
import logging

LOG = logging.getLogger(__name__)

def vcf_writer(variants, vcf_path, member):

    with open(vcf_path, "w") as vcf_handle:

        vcf_handle.write("##fileformat=VCFv4.2\n")
        vcf_handle.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{}\n".format(member))

        for variant in variants:

            genotype = variant["genotype"] or './.'
            vcf_entry = variant["vcf_entry"].strip("\n").split("\t")
            entry = "\t".join(vcf_entry[0:8] + ["GT"] + [genotype]) + "\n"
            vcf_handle.write(entry)

def append_gt(variants, vcf_path, member):
    vcf_dir = vcf_path.parent
    vcf_name = vcf_path.stem + "_{}.vcf".format(member)
    out_path = vcf_dir.joinpath(vcf_name)

    with open(vcf_path, "r") as in_vcf:

        with open(out_path, "w") as out_vcf:
            variant_num = 0
            for old_entry in in_vcf:

                entry = old_entry.strip('\n')

                if entry.startswith("##"):

                    pass

                elif entry.startswith("#"):

                    entry = entry + "\t" + member

                else:

                    try:
                        genotype = variants[variant_num]["genotype"] or './.'

                    except IndexError:
                        LOG.critical("list index out of range")
                        raise
                    entry = entry + "\t" + genotype
                    variant_num += 1

                entry = entry + "\n"

                out_vcf.write(entry)
