"""
    Module for writinh vcf files
"""
import logging

HEADER = (

    '##fileformat=VCFv4.2',

    '##INFO=<ID=END,Number=1,Type=Integer,Description="Stop position of the interval">',
    '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant">',
    '##INFO=<ID=TYPE,Number=A,Type=String,Description="The type of allele, either snp, mnp, ins, del, or complex.">',
    '##INFO=<ID=MutaccRankScore,Number=.,Type=String,Description="The rank score for this variant in this family. family_id:rank_score.">',
    '##INFO=<ID=RMV,Number=1,Type=Float,Description="Rank model version">',

    '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
    '##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth (reads with MQ=255 or with bad mates are filtered)">',
    '##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">',
    '##FORMAT=<ID=AD,Number=R,Type=Integer,Description="Allelic depths for the ref and alt alleles in the order listed">'

)



LOG = logging.getLogger(__name__)

def vcf_writer(found_variants, vcf_path, sample_name):

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

        for header_line in HEADER:
            vcf_handle.write(header_line + '\n')

        vcf_handle.write(f"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{sample_name}\n")

        for variant in found_variants:

            #Write info field
            info = ""
            info += f"END={variant['end']};"
            if variant.get('RankScore'):
                info += f"MutaccRankScore={variant['RankScore']};"
            if variant.get('rank_model_version'):
                info += f"RMV={variant['rank_model_version']};"

            if variant['variant_type'].upper() == 'SNV':
                info += f"TYPE={variant['variant_subtype']}"
            elif variant['variant_type'].upper() == 'SV':
                info += f"SVTYPE={variant['variant_subtype']}"


            #write format field and gt
            format_list = []
            gt_call = []

            #If genotype is given for sample
            if variant['genotype']:
                for key in variant['genotype'].keys():

                    if variant['genotype'][key] != -1:
                        format_list.append(key)
                        gt_call.append(str(variant['genotype'][key]))

            #If variant entry has no genotype
            else:
                format_list.append('GT')
                gt_call.append('./.')

            format_list = ':'.join(format_list)
            gt_call = ':'.join(gt_call)


            vcf_entry = variant["vcf_entry"].strip("\n").split("\t")
            entry = "\t".join(vcf_entry[0:7] + [info] + [format_list] + [gt_call]) + "\n"
            vcf_handle.write(entry)
