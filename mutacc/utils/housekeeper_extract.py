
def findPath(inHouseID):
	
    """

    Finds paths to relevant files in HouseKeeper

    Args:

        inHouseID (str): ID to sample in HouseKeeper
        
    Returns:
    
        paths (list): list of paths to relevant files.
	
					
    """

    paths = {'ID': inHouseID,
             'paths': ['/path/to/bam/',
                     '/path/to/fastq']}
             
    return paths


