"""
    Module with for building variant objects from a vcf
"""

from cyvcf2 import VCF

from mutacc.parse.path_parse import parse_path


#IDs in the INFO field that should be included in the database
INFO_IDS = (

    'RankScore',

)

#A function for correctly parsing a vcf entry for the regions to look for in the bam file will be
# necessary. This will be the case for more complex structural variants. the find_region function
#attempts to
class Variant(dict):

    """
        Class to represent variant
    """

    def __init__(self, vcf_entry, samples, padding):

        super(Variant, self).__init__()

        self.entry = vcf_entry
        self.samples = samples

        self.build_variant_object(padding)

        self.entry = str(self.entry)

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

        vtype = self.entry.INFO.get("TYPE") or self.entry.INFO.get("SVTYPE") or 'None'
        vtype = vtype.upper()

        region = {"start": start - padding,
                  "end": end + padding}

        return vtype, region

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


    def build_variant_object(self, padding):
        """
            makes a dictionary of the variant to be loaded into a mongodb
        """

        #Find genotype and sample id for the samples given in the vcf file
        vtype, region = self._find_region(padding)
        samples = self._find_genotypes()

        self['display_name'] = self.display_name
        self['variant_type'] = vtype
        self['alt'] = self.entry.ALT
        self['ref'] = self.entry.REF
        self['chrom'] = self.entry.CHROM
        self['start'] = self.entry.start
        self['end'] = self.entry.end
        self['vcf_entry'] = str(self.entry)
        self['reads_region'] = region
        self['samples'] = samples
        self['padding'] = padding

        #Add data from the info INFO field
        for info_id in INFO_IDS:
            if self.entry.INFO.get(info_id):
                self[info_id] = self.entry.INFO[info_id]

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


def get_variants(vcf_file, padding):

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

        yield Variant(entry, samples, padding)

    vcf.close()
