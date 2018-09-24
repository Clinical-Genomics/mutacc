import subprocess
import json 

#Should the entire JSON object be returned, or perhaps just the IDs?
def find_causatives(case_id = None):
    
    """
    
    Parses json output from scout for all cases with causative variants
    
    Args:
        
        case_if (string): ID for the case. If default None, then return all causative cases 
    
    Returns:
        
        dict, or list of dicts representing JSON
        
    """
    
    if case_id:

        cases = subprocess.check_output(['scout', 'export', 'cases', '--case-id', case_id, '--json'])    
    else:

        cases = subprocess.check_output(['scout', 'export', 'cases', '--causatives', '--json'])    
    
    cases = cases.decode("utf-8")

    cases = json.loads(cases)
    
    return cases 

def find_variants(variant_id):
    
    variant = subprocess.check_output(['scout','export', 'variants', '-d', variant_id, '--json'])
    variant = variant.decode("utf-8")
    variant = json.loads(variant)
    
    return variant
        
if __name__ == '__main__':
    
    causatives = find_causatives()
        
    variant = find_variants(causatives[0]['causatives'][0])
    
    
    
    
    
    
    
    
    
