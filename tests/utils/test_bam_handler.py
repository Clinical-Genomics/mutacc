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
    return cram, reference


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
