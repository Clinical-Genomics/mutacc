"""
    Functions to handle regions
"""

def overlaps(region_1, region_2):
    """
        Find if two regions overlaps
        a region is defined as dictionary with
        chromosome/contig, start- and end position given

        Args:
            region_1/region_2(dict): dictionary holding region information

        Returns:
            overlapping(bool): True if regions overlap, False else
    """
    overlapping = False

    if region_1["chrom"] == region_2["chrom"]:

        if region_1["end"] < region_2["start"] or \
           region_1["start"] > region_2["end"]:

            overlapping = False

        else:

            overlapping = True
    else:

        overlapping = False

    return overlapping

def overlapping_region(single_region, region_list):
    """
        compare a single region to a list of regions, and
        find if the region overlaps with any region in the list.
    """
    overlapping = False
    for region in region_list:
        if overlaps(single_region, region):
            overlapping = True
    return overlapping
