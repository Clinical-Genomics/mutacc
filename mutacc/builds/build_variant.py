from cyvcf2 import VCF

from mutacc.parse.path_parse import parse_path

#A function for correctly parsing a vcf entry for the regions to look for in the bam file will be
# necessary. This will be the case for more complex structural variants. the find_region function
#attempts to 
class Variant:

    def __init__(self, vcf_entry):

        self.entry = vcf_entry
        
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
        if self.entry.INFO.get("SVTYPE"):

            vtype = self.entry.INFO.get("SVTYPE").upper()

            if vtype != "BND":
                
                region = {"start": self.entry.start - padding,
                          "end": self.entry.end + padding}

            #Find the region for variant with an 'SVTYPE' ID in the INFO field of the vcf entry
            else:
                
                #Depending on the direction of the break end, the region is extended either upstreams
                #or downstream of the position of the break end.
                if "[" in self.entry.ALT[0]:

                    region = {"start": self.entry.start - padding,
                              "end": self.entry.end}
                
                else:

                    region = {"start": self.entry.start,
                              "end": self.entry.end + padding}

        #For variants with an ID 'TYPE' in the INFO field         
        elif self.entry.INFO.get("TYPE"):
       
            vtype = self.entry.INFO.get("TYPE")
            region = {"start": self.entry.start - padding,
                      "end": self.entry.end + padding}

        else:

            vtype = 'None'
            region = {"start": self.entry.start - padding,
                      "end": self.entry.end + padding}
        self.vtype = vtype 
        self.region = region

    def build_variant_object(self):
        """
            makes a dictionary of the variant to be loaded into a mongodb
        """
        self.variant = {

                "variant_type": self.vtype,
                "alt": self.entry.ALT,
                "ref": self.entry.REF,
                "chrom": self.entry.CHROM,
                "start": self.entry.start,
                "end": self.entry.end,
                "vcf_entry": str(self.entry),
                "reads_region": self.region 
                
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

    for entry in vcf:

        yield Variant(entry)

    vcf.close()


