from cyvcf2 import VCF

from mutacc.parse.path_parse import parse_path

#A function for correctly parsing a vcf entry for the regions to look for in the bam file will be
# necessary. This will be the case for more complex structural variants. the find_region function
#attempts to 

def make_variants(vcf_file, padding):

    """
        Given a vcf file, this function parses the file for variant and stores each variant
        together with relevant variant data. Furthermore, the region from where the aligned reads
        that supports this variant is extracted and returned for each variant.
         

        Args: 
            
            vcf_file (string): vcf file containing the variants 
            padding (int): given in bp, extends the region for where to look for reads in the
            alignment files.

        Returns: 

            regions (list): List where each element is a variant represented as a dictionary,
            containing all relevant data about variant.

    """
    
    vcf_file = parse_path(vcf_file)

    vcf = VCF(str(vcf_file), 'r')
    
    variants = []

    for entry in vcf:
        
        vtype, region = find_region(entry, padding)

        variant = {"ID": entry.ID,
                   "reads_region": region,
                   "type": vtype,
                   "vcf_entry": str(entry),
                   "chrom": entry.CHROM,
                   "pos": entry.POS,
                   "alt": entry.ALT,
                   "ref": entry.REF,
                   "start": entry.start,
                   "end": entry.end}

        variants.append(variant)

    vcf.close() 
    
    return variants

def find_region(entry, padding):
    """
        Given a vcf entry, this function attempts to return the relevant genomic regions
        to where the reads aligned that supports the given variant. 
        
        Args: 
            
            entry (cyvcf2.Variant): variant entry in vcf file 
            padding (int): given in bp, extends the region for where to look for reads in the
            alignment files.

        Returns: 

            vtype (str): variant type
            region (dict): dictionary holding the start and end coordinates for a genomic region


    """
    #For variants with an ID 'SVTYPE' in the INFO field of the vcf entry
    if entry.INFO.get("SVTYPE"):

        vtype = entry.INFO.get("SVTYPE").upper()

        if vtype in ("DEL", "INS", "DUP", "INV", "CNV"):
            
            region = {"start": entry.start - padding,
                      "end": entry.end + padding}

        #Find the region for variant with an 'SVTYPE' ID in the INFO field of the vcf entry
        elif vtype == "BND":
            
            #Depending on the direction of the break end, the region is extended either upstreams
            #or downstream of the position of the break end.
            if "[" in entry.ALT[0]:

                region = {"start": entry.start - padding,
                          "end": entry.end}
            
            else:

                region = {"start": entry.start,
                          "end": entry.end + padding}

    #For variants with an ID 'TYPE' in the INFO field         
    elif entry.INFO.get("TYPE"):
   
        vtype = entry.INFO.get("TYPE")

        region = {"start": entry.start - padding,
                  "end": entry.end + padding}

    else:

        vtype = None
        region = {"start": entry.start - padding,
                  "end": entry.end + padding}

    return (vtype, region)


