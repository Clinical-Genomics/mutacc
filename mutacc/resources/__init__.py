import pkg_resources

case_filename = "resources/case.yaml"
father_fastq1_filename = "resources/father_R1.fastq.gz"
father_fastq2_filename = "resources/father_R2.fastq.gz"
father_bam_filename = "resources/father.bam"
mother_bam_filename = "resources/mother.bam"
child_bam_filename = "resources/child.bam"
vcf_filename = "resources/variant1.vcf.gz"

vcf_parser_file = "resources/vcf-info-def.yaml"

path_to_case_file = pkg_resources.resource_filename("mutacc", case_filename)
path_to_background_fastq1_file = pkg_resources.resource_filename(
    "mutacc", father_fastq1_filename
)
path_to_background_fastq2_file = pkg_resources.resource_filename(
    "mutacc", father_fastq2_filename
)
path_to_background_bam_file = pkg_resources.resource_filename(
    "mutacc", father_bam_filename
)

default_vcf_parser = pkg_resources.resource_filename("mutacc", vcf_parser_file)

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
            "bam_file": pkg_resources.resource_filename("mutacc", child_bam_filename),
        },
        {
            "sample_id": "father",
            "analysis_type": "wgs",
            "sex": "male",
            "phenotype": "unaffected",
            "mother": "0",
            "father": "0",
            "bam_file": pkg_resources.resource_filename("mutacc", father_bam_filename),
        },
        {
            "sample_id": "mother",
            "analysis_type": "wgs",
            "sex": "female",
            "phenotype": "unaffected",
            "mother": "0",
            "father": "0",
            "bam_file": pkg_resources.resource_filename("mutacc", mother_bam_filename),
        },
    ],
    "variants": pkg_resources.resource_filename("mutacc", vcf_filename),
}
