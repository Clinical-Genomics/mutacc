from cyvcf2 import VCF

from mutacc.parse.path_parse import parse_path

#A function for correctly parsing a vcf entry for the regions to look for in the bam file will be
# necessary. This will be the case for more complex structural variants. the find_region function
#attempts to
class Variant:

    def __init__(self, vcf_entry, samples):

        self.entry = vcf_entry
        self.samples = samples

    #At the moment there are a lot of if statements in this method checking
    #the variant type, even though all the variants are treated the same at the
    #moment. That is, the region to extract is simply the start and end positions
    #as given in the vcf, + the padding that is wanted. I'm thinking that I'll
    #leave it like this, in case we found out in the future that the variants
    #need to be treated differently depending on the type. 
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

        if self.entry.INFO.get("SVTYPE"):

            vtype = self.entry.INFO.get("SVTYPE").upper()

            if vtype != "BND":

                region = {"start": start - padding,
                          "end": end + padding}

            #Find the region for variant with an 'SVTYPE' ID in the INFO field of the vcf entry
            else:

                #Depending on the direction of the break end, the region is extended either upstreams
                #or downstream of the position of the break end.
                if "[" in self.entry.ALT[0]:

                    region = {"start": start - padding,
                              "end": end + padding}

                else:

                    region = {"start": start - padding,
                              "end": end + padding}

        #For variants with an ID 'TYPE' in the INFO field
        elif self.entry.INFO.get("TYPE"):

            vtype = self.entry.INFO.get("TYPE")
            region = {"start": start - padding,
                      "end": end + padding}

        else:

            vtype = 'None'
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

        if self.entry.genotypes:

            samples = [{ 'sample_id': self.samples[i],
                         'genotype': '/'.join(
                            [
                            str(self.entry.genotypes[i][0]),
                            str(self.entry.genotypes[i][1])
                            ]
                        )
                    } for i in range(len(self.samples))]

        else:

            samples = [{ 'sample_id': self.samples[i],
                           'genotype': "0"
                } for i in range(len(self.samples))]

        return samples


    def build_variant_object(self):
        """
            makes a dictionary of the variant to be loaded into a mongodb
        """

        #Find genotype and sample id for the samples given in the vcf file
        samples = self.find_genotypes()

        self.variant = {

                "display_name": '_'.join(
                    [
                        self.entry.CHROM,
                        str(self.entry.POS),
                        self.entry.REF,
                        self.entry.ALT[0]
                    ]
                ),
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
