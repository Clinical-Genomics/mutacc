import shutil
import pytest
import pysam
from pathlib import Path
from mutacc.utils.bam_handler import BAMContext


def test_BAMContext(tmpdir, bam_path):

    with BAMContext(
        bam_file = bam_path,
        out_dir = Path(tmpdir.mkdir("bam_test"))
        ) as bam_handle:

        bam_handle.find_reads_from_region(
            chrom = "4",
            start = 1000000,
            end = 10002000
        )

        assert bam_handle.out_name.exists()

        temp_names = bam_handle.make_names_temp(Path(tmpdir.mkdir("names_dir")))

        assert Path(temp_names).exists()


    assert not Path(temp_names).exists()


def test_BAMContext_find_names(read_ids_fixed, bam_path):

    # GIVEN a list of reads names that are in the bam-file
    with BAMContext(
        bam_file = bam_path,
        ) as bam_handle:

    # WHEN extracting the reads names from region
        bam_handle.find_names_from_region(
            chrom = "4",
            start = 1000000,
            end = 10002000
        )

    #THEN the set of read names found should correspond to the the above read names
        assert set(read_ids_fixed) == bam_handle.found_reads


def test_BAMContext_find_reads_by_proximity(read_ids_fixed, bam_path):

    # GIVEN a list of reads names that are in the bam-file
    with BAMContext(
        bam_file = bam_path,
        ) as bam_handle:

    # WHEN extracting the reads names from region using the brute flag
        bam_handle.find_reads_from_region(
            chrom = "4",
            start = 1000000,
            end = 10002000,
            brute = True
        )

    #THEN the set of read names found should correspond to the the above read names
        assert bam_handle.found_reads.issubset(set(read_ids_fixed))


def test_BAMContext_find_reads_without_mates(read_ids_fixed, bam_path):

    # GIVEN a list of reads names that are in the bam-file
    with BAMContext(
        bam_file = bam_path,
        ) as bam_handle:

    # WHEN extracting the reads names from region
        bam_handle.find_reads_from_region(
            chrom = "4",
            start = 1000000,
            end = 10002000,
            find_mates=False
        )

    #THEN the set of read names found should correspond to the the above read names
        assert bam_handle.found_reads.issubset(set(read_ids_fixed))


@pytest.fixture(name="cram_with_reference")
def fixture_cram_with_reference(tmpdir):
    """Small indexed CRAM and the reference fasta needed to decode it"""

    contig_length = 5000
    sequence = "ACGT" * (contig_length // 4)
    work_dir = Path(tmpdir.mkdir("cram_test"))

    reference = work_dir.joinpath("ref.fa")
    reference.write_text(">chr1\n" + sequence + "\n")
    pysam.faidx(str(reference))

    header = {"HD": {"VN": "1.6", "SO": "coordinate"}, "SQ": [{"SN": "chr1", "LN": contig_length}]}
    cram = work_dir.joinpath("small.cram")
    with pysam.AlignmentFile(
        str(cram), "wc", header=header, reference_filename=str(reference)
    ) as out_cram:
        for number in range(10):
            start = 100 + number * 50
            for mate in (0, 1):
                read = pysam.AlignedSegment(out_cram.header)
                read.query_name = f"read{number}"
                read.query_sequence = sequence[start : start + 50]
                read.query_qualities = pysam.qualitystring_to_array("I" * 50)
                read.reference_id = 0
                read.reference_start = start
                read.cigarstring = "50M"
                read.mapping_quality = 60
                read.flag = 99 if mate == 0 else 147
                read.next_reference_id = 0
                read.next_reference_start = start
                read.template_length = 50 if mate == 0 else -50
                out_cram.write(read)
    pysam.index(str(cram))

    moved_reference = Path(tmpdir.mkdir("reference")).joinpath("ref.fa")
    for suffix in ("", ".fai"):
        shutil.move(str(reference) + suffix, str(moved_reference) + suffix)
    return cram, moved_reference


def test_BAMContext_cram_without_reference_fails(cram_with_reference):

    cram, _ = cram_with_reference

    # WHEN extracting reads without giving the reference
    # THEN the CRAM cannot be decoded
    with pytest.raises((OSError, ValueError)):
        with BAMContext(bam_file=cram) as bam_handle:
            bam_handle.find_names_from_region(chrom="chr1", start=100, end=300)


def test_BAMContext_cram_with_reference(tmpdir, cram_with_reference):

    # GIVEN a CRAM file and the reference fasta it was written with
    cram, reference = cram_with_reference
    out_dir = Path(tmpdir.mkdir("cram_out"))

    # WHEN extracting reads from a region, giving the reference
    with BAMContext(bam_file=cram, out_dir=out_dir, reference=str(reference)) as bam_handle:
        bam_handle.find_reads_from_region(chrom="chr1", start=100, end=300)
        out_name = bam_handle.out_name
        found = bam_handle.record_number
        paired = bam_handle.paired

    # THEN the reads are found and written to a BAM file
    assert found > 0
    assert paired
    assert out_name.name == "mutacc_small.bam"
    with pysam.AlignmentFile(str(out_name), "rb") as out_bam:
        assert sum(1 for _ in out_bam) == found * 2


def test_BAMContext_passes_reference_to_pysam(monkeypatch, bam_path):

    # GIVEN pysam.AlignmentFile is replaced by a recorder
    calls = []
    real_alignment_file = pysam.AlignmentFile

    def recording_alignment_file(*args, **kwargs):
        calls.append(kwargs)
        return real_alignment_file(*args, **kwargs)

    monkeypatch.setattr(pysam, "AlignmentFile", recording_alignment_file)

    # WHEN opening a BAM with and without a reference
    with BAMContext(bam_file=bam_path):
        pass
    with BAMContext(bam_file=bam_path, reference="tests/fixtures/case.yaml"):
        pass

    # THEN the reference is handed to pysam only when given
    assert calls[0]["reference_filename"] is None
    assert calls[1]["reference_filename"].endswith("case.yaml")


def test_BAMContext_contig_name_without_prefix(tmpdir, cram_with_reference):

    # GIVEN a CRAM where the contig is named 'chr1'
    cram, reference = cram_with_reference

    with BAMContext(bam_file=cram, reference=str(reference)) as bam_handle:
        # WHEN the contig is given as '1', 'chr1' and with other case
        names = []
        for chrom in ("chr1", "1", "Chr1"):
            bam_handle.found_reads = set()
            bam_handle.find_names_from_region(chrom=chrom, start=100, end=300)
            names.append(set(bam_handle.found_reads))

        # THEN the same reads are found
        assert names[0]
        assert names[0] == names[1] == names[2]

        # AND names are resolved as expected, also for the mitochondrial contig
        assert bam_handle._contig_name("1") == "chr1"
        assert bam_handle._contig_name("MT") == "MT"


def test_BAMContext_contig_name_with_prefix_missing(bam_path):

    # GIVEN a BAM where the contig is named '4'
    with BAMContext(bam_file=bam_path) as bam_handle:
        # WHEN the contig is given with a 'chr' prefix THEN the prefix is removed
        assert bam_handle._contig_name("chr4") == "4"
        assert bam_handle._contig_name("4") == "4"
        # AND an unknown contig is returned unchanged
        assert bam_handle._contig_name("nonexisting") == "nonexisting"
