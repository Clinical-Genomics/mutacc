# VCF
COMMA = ","
COLON = ":"
SEMICOLON = ";"
PIPE = "|"
TAB = "\t"
NEW_LINE = "\n"
EQUALS = "="
DOT = "."
SLASH = "/"


TYPES = {"str": str, "int": int, "float": float, None: lambda value: value}
VCF_HEADER = (
    '##INFO=<ID=END,Number=1,Type=Integer,Description="Stop position of the interval">',
    '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant">',
    '##INFO=<ID=TYPE,Number=A,Type=String,Description="The type of allele, either snp, mnp, ins, del, or complex.">',
    '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
    '##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth (reads with MQ=255 or with bad mates are filtered)">',
    '##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">',
    '##FORMAT=<ID=AD,Number=R,Type=Integer,Description="Allelic depths for the ref and alt alleles in the order listed">',
)

VCF_FILEFORMAT = "##fileformat=VCFv4.2"


PADDING = 1000
