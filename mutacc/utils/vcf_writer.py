
def vcf_writer(variants, vcf_path, member):

    with open(vcf_path, "w") as vcf_handle:

        vcf_handle.write("##fileformat=VCFv4.2\n")
        vcf_handle.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{}\n".format(member))
        for variant in variants:

            genotype = variant["genotype"] or './.'
            vcf_entry = variant["vcf_entry"].split("\t")
            entry = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\tGT\t{}".format(
                vcf_entry[0], vcf_entry[1], vcf_entry[2], vcf_entry[3],
                vcf_entry[4], vcf_entry[5], vcf_entry[6], vcf_entry[7],
                genotype
            )
            vcf_handle.write(entry+"\n")
