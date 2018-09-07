import subprocess

def findPath(internal_id):
	
    """

    Finds paths to relevant files in HouseKeeper

    Args:

        inHouseID (str): ID to sample in HouseKeeper
        
    Returns:
    
        paths (list): list of paths to relevant files.
	
					
    """

    files = {'ID': internal_id,
             'paths': ['/path/to/bam/',
                     '/path/to/fastq']}
             
    return files


