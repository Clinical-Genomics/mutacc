import random
import string

def random_string():

    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

#Return random trio with random variant object to populate the mock database
def random_trio():

    case = {}
    case_id = random_string()
    case['case_id'] = case_id

    #make samples
    sample_ids = []
    for i in range(3):
        sample_ids.append(random_string())

    samples = []
    count = 0
    for sample_id in sample_ids:
        count += 1
        sample = {}
        sample['sample_id'] = sample_id
        sample['mother'] = sample_ids[1] if count == 1 else '0'
        sample['father'] = sample_ids[2] if count == 1 else '0'
        sample['phenotype'] = random.choice(['affected', 'unaffected'])
        if count == 1:
            sex = random.choice(['male', 'female'])
        elif count == 2:
            sex = 'female'
        else:
            sex = 'male'
        sample['sex'] = sex
        sample['analysis_type'] = random.choice(['wes', 'wgs'])
        sample['bam_file'] = 'path'
        sample['variant_bam_file'] = 'path/to/variant_bam'
        sample['variant_fastq_files'] = ['path/to/fastq1', 'path/to/fastq2']
        samples.append(sample)

    case['samples'] = samples

    #make variant
    variant = {}
    variant['display_name'] = random_string()
    variant['variant_type'] = random.choice(['del','snp','dup','bnd'])
    variant['alt'] = [random.choice(['A','C','G','T'])]
    variant['ref'] = random.choice(['A','C','G','T'])
    variant['chrom'] =  random.choice(['1','2','X','Y'])
    pos = random.choice(range(1000000))
    end =  pos + random.choice(range(100))
    variant['start'] = pos
    variant['end'] = end
    padding = random.choice(range(100))
    variant['padding'] = padding
    variant['reads_region'] = {'start': pos - padding, 'end': end + padding}
    variant['case'] = case_id
    variant['samples'] = {
        sample_id: {'GT': random.choice(['1/1','0/1','0/0'])} for id in sample_ids
    }

    variant['vcf_entry'] = '\t'.join([
            str(variant['chrom']),
            str(variant['start']),
            '.',
            str(variant['ref']),
            str(variant['alt']),
            '.',
            'PASS',
        ])



    return case, variant
