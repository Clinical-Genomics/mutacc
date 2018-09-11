import subprocess

def find_files(internal_id, tags = ()):
	
    """

    Finds paths to relevant files in HouseKeeper

    Args:

        internal_id (str): internal ID of sample in HouseKeeper
        tags (tuple/list): list of all file tags of interest
        
        
    Returns:
    
        files (dict): dict with files, with tag name as keys. 
	
					
    """
    
    #hk_out = subprocess.check_output(['housekeeper','get', '-V', internal_id])
    
    hk_out = subprocess.check_output(["cat", 'mutacc/hapmap_vitalmouse_housekeeper.txt'])
    
    hk_out = hk_out.decode("utf-8")
                     
    files = {tag: [] for tag in tags}
             
    for row in hk_out.split('\n'):
        
        fields = row.split('|')
        
        if fields[2].strip() in tags:
            
            files[fields[2].strip()].append(fields[1].strip())
            
    return files
        
        

if __name__ == "__main__":
    
    files = find_files("", tags = ("vcf-snv-clinical", "pedigree"))
    
