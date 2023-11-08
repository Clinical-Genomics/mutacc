from importlib_resources import files

BASE_PATH = "mutacc.resources"

case_filename = "case.yaml"
father_fastq1_filename = "father_R1.fastq.gz"
father_fastq2_filename = "father_R2.fastq.gz"
father_bam_filename = "father.bam"
mother_bam_filename = "mother.bam"
child_bam_filename = "child.bam"
vcf_filename = "variant1.vcf.gz"
vcf_parser_file = "vcf-info-def.yaml"


path_to_case_file = str(files(BASE_PATH).joinpath(case_filename))
path_to_background_fastq1_file = str(files(BASE_PATH).joinpath(father_fastq1_filename))
path_to_background_fastq2_file =str(files(BASE_PATH).joinpath(father_fastq2_filename))
path_to_background_bam_file = str(files(BASE_PATH).joinpath(father_bam_filename))
default_vcf_parser = str(files(BASE_PATH).joinpath(vcf_parser_file))

DEMO_CASE = {
    "case": {"case_id": "demo_trio"},
    "samples": [
        {
            "sample_id": "child",
            "analysis_type": "wgs",
            "sex": "male",
            "phenotype": "affected",
            "mother": "mother",
            "father": "father",
            "bam_file": str(files(BASE_PATH).joinpath(child_bam_filename)),
        },
        {
            "sample_id": "father",
            "analysis_type": "wgs",
            "sex": "male",
            "phenotype": "unaffected",
            "mother": "0",
            "father": "0",
            "bam_file": str(files(BASE_PATH).joinpath(father_bam_filename)),
        },
        {
            "sample_id": "mother",
            "analysis_type": "wgs",
            "sex": "female",
            "phenotype": "unaffected",
            "mother": "0",
            "father": "0",
            "bam_file": str(files(BASE_PATH).joinpath(mother_bam_filename)),
        },
    ],
    "variants": str(files(BASE_PATH).joinpath(vcf_filename)),
}
