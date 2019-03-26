from cyvcf2 import VCF

from mutacc.parse.path_parse import parse_path

#IDs in the INFO field that should be included in the database
INFO_IDS = (

    'RankScore',

)

#A function for correctly parsing a vcf entry for the regions to look for in the bam file will be
# necessary. This will be the case for more complex structural variants. the find_region function
#attempts to
class Variant:

    def __init__(self, vcf_entry, samples):

        self.entry = vcf_entry
        self.samples = samples

    def find_region(self, padding):
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
        start, end = self.find_start_end()

        vtype = self.entry.INFO.get("TYPE") or self.entry.INFO.get("SVTYPE") or 'None'
        vtype = vtype.upper()

        region = {"start": start - padding,
                  "end": end + padding}

        self.vtype = vtype
        self.region = region

    def find_start_end(self):
        start = self.entry.start
        if self.entry.INFO.get('END'):
            end = self.entry.INFO.get('END')
        else:
            end = self.entry.end
        return (int(start), int(end))


    def find_genotypes(self):

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
                    'GQ': float(self.entry.gt_quals[i]),
                    'AD': int(self.entry.gt_alt_depths[i])

                }

            samples[sample_id] = sample

        return samples


    def build_variant_object(self):
        """
            makes a dictionary of the variant to be loaded into a mongodb
        """

        #Find genotype and sample id for the samples given in the vcf file
        samples = self.find_genotypes()

        self.variant = {

                "display_name": self.display_name,
                "variant_type": self.vtype,
                "alt": self.entry.ALT,
                "ref": self.entry.REF,
                "chrom": self.entry.CHROM,
                "start": self.entry.start,
                "end": self.entry.end,
                "vcf_entry": str(self.entry),
                "reads_region": self.region,
                "samples": samples
                }

        #Add data from the info INFO field
        for ID in INFO_IDS:
            if self.entry.INFO.get(ID):
                self.variant[ID] = self.entry.INFO[ID]

    @property
    def display_name(self):

        display_name = '_'.join(
                [
                    self.entry.CHROM,
                    str(self.entry.POS),
                    self.entry.REF,
                    self.entry.ALT[0]
                ]
            )

        return display_name

    @property
    def variant_object(self):

        return self.variant


def get_variants(vcf_file):

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

    for entry in vcf:

        yield Variant(entry, samples)

    vcf.close()

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
        a1 = '.'
    else:
        a1 = str(cyvcf2_gt[0])

    if cyvcf2_gt[1] == -1:
        a2 = '.'
    else:
        a2 = str(cyvcf2_gt[1])

    genotype = a1 + separator + a2

    return genotype
