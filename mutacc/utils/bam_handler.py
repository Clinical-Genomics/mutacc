"""
    Module with to handle bam files
"""

import logging
import tempfile
import os

import pysam

from mutacc.parse.path_parse import parse_path
from mutacc.utils.constants import PADDING

LOG = logging.getLogger(__name__)


class BAMContext:
    """
        Context manager to deal with bam files
    """

    def __init__(self, bam_file, out_dir=None, paired=True):
        """
            Args:
                bam_file (str): path to bam file
                out_dir (Path): Directory where new bam-file is created
                pared (bool): If bam containes paired reads
        """
        self.bam_file = parse_path(bam_file)
        self.file_name = self.bam_file.name
        self.bam = pysam.AlignmentFile(self.bam_file, "rb")
        self.reads = {}
        self.ends = 2 if paired else 1
        self.found_reads = set()
        self.out_dir = out_dir
        if self.out_dir:
            self.out_dir = parse_path(out_dir, file_type="dir")
            self.out_name = out_dir.joinpath("mutacc_" + self.file_name)
            self.out_bam = pysam.AlignmentFile(self.out_name, "wb", template=self.bam)

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.bam.close()

        if self.out_dir:
            self.out_bam.close()

        try:
            os.remove(self.names_temp)
        except AttributeError:
            pass

    def find_read_names_from_region(self, chrom, start, end):
        """Adds the read names in region to the set found_reads

            Args:
                chrom (str): name of contig
                start (int): start of region
                end (int): end of region
        """

        read_names = [read.query_name for read in self.bam.fetch(chrom, start, end)]
        self.found_reads = self.found_reads.union(set(read_names))

    def find_reads_from_region(self, chrom, start, end, brute=False, find_mates=True):

        """
            Writes the found reads in region to a new bam-file, if a out-dir is
            given to the constructor, else adds the read names to set self.found_reads

            Args:
                chrom (str): name of contig
                start (int): start of region
                end (int): end of region
                brute (bool): if True, finds the read mates just by looking in
                    the proximity of specified region. If False, searches for the
                    mate in the bam file.
                find_mates (bool): If True, tries to find the mates of unmatched reads

        """
        for read in self.bam.fetch(chrom, start, end):
            read_name = read.query_name
            if read_name in self.found_reads:
                continue
            pair_list = self.reads.get(read_name)
            if pair_list is not None:
                paired_read = pair_list[0]
                if str(paired_read) == str(read):
                    continue
                pair_list.append(read)
            else:
                self.reads[read_name] = [read]
            if len(self.reads[read_name]) == self.ends:
                self._flush_reads(read_name)

        if find_mates:
            if not brute:
                self._find_mates_explicitly()
            else:
                left_end = (chrom, start - 1000, start)
                right_end = (chrom, end, end + 1000)
                for region in (left_end, right_end):
                    self._find_mates_close(*region)
        self._reset_reads()

    def _flush_reads(self, read_name: str):
        """Flushes the read pair to new bam-file
            Args:
                read_name (str): read name of read-pairs
        """
        if self.out_dir:
            for end in self.reads[read_name]:
                self.out_bam.write(end)
        self.found_reads.add(read_name)
        self.reads.pop(read_name)

    def _find_mates_explicitly(self):
        """
            Find mates by looking in bam_file
        """
        unmatched_reads = list(self.unmatched_reads)
        for unmatched_read in unmatched_reads:
            mate = self._find_mate(self.reads[unmatched_read][0])
            if mate:
                self.reads[unmatched_read].append(mate)
                if self.out_dir:
                    for end in self.reads[unmatched_read]:
                        self.out_bam.write(end)
                self.found_reads.add(unmatched_read)
            self.reads.pop(unmatched_read)

    def _find_mate(self, read):

        """
            Find mate for read
        """
        try:
            mate = self.bam.mate(read)
        except ValueError:
            mate = None
        return mate

    def _find_mates_close(self, chrom, start, end):
        """
            Tries to find mates in specified region
        """
        for read in self.bam.fetch(chrom, start, end):
            read_name = read.query_name
            if read_name in self.found_reads:
                continue
            pair_list = self.reads.get(read_name)
            if pair_list is not None:
                paired_read = pair_list[0]
                if str(paired_read) == str(read):
                    continue
                pair_list.append(read)
                self._flush_reads(read_name)

    def _reset_reads(self):
        """
            Removes reads with no mates found
        """
        self.reads.clear()

    @property
    def out_file(self):
        """
            returns output file
        """
        return str(self.out_name)

    @property
    def unmatched_reads(self):
        """Returns reads without found mates"""
        _unmatched_reads = self.reads.keys()
        return _unmatched_reads

    @property
    def record_number(self):
        """
            Number of records
        """
        return len(self.found_reads)

    def make_names_temp(self, out_dir):
        """
            Make temporary file holding each read name on separate line
        """
        with tempfile.NamedTemporaryFile("wt", dir=out_dir, delete=False) as temp_file:
            temp_file.write("####READ NAMES####\n")
            for name in self.found_reads:
                temp_file.write(name + "\n")
            self.names_temp = temp_file.name
        return self.names_temp


def check_bam(bam_file):

    """Checks if reads in bam are paired
    Args:
        bam_file (path): path to bam file

    Returns:
        paired (bool): True if reads are paired
    """
    paired = False
    with pysam.AlignmentFile(bam_file) as bam:
        count = 0
        for read in bam:
            count += 1
            if read.is_paired:
                paired = True
                break
            if count == 1000:
                break

    return paired


def get_length(bam_file):
    """Calculate the average read length from first 1000 reads in bam
    Args:
        bam_file (path): path to bam file
    Returns:
        average_length (int): average read length
    """
    acc_length = 0

    with pysam.AlignmentFile(bam_file) as bam:
        count = 0
        for read in bam:
            count += 1
            acc_length += read.query_length
            if count == 1000:
                break

    average_length = acc_length / 1000

    return average_length


def get_real_padding(length, padding=None):
    """Given the read lengths in a BAM, calculate the real padding needed taking
    into consideration the read length. This should hopefully approximate
    the PADDING constant.
    Args:
        length (int): read length
    Returns:
        real_padding (int): sample specific padding to approximate PADDING

    """
    padding = padding or PADDING
    real_padding = padding - length / 2
    if real_padding < 1:
        real_padding = 1

    return real_padding


def get_overlaping_reads(file_name, chrom, start, end):
    """Extracts all read names from a bam file, overlapping the specified region.

        Args:
            file_name (string): name of bam file
            chrom (string): name of chromosome
            start (int): start of region
            end (int): end of region

        Returns:
            reads (set): set of read names.
    """
    file_name = parse_path(file_name)
    bam_file = pysam.AlignmentFile(file_name, "rb")
    reads = bam_file.fetch(reference=chrom, start=start, end=end)
    ids = [read.query_name for read in reads]
    bam_file.close()
    return set(ids)
