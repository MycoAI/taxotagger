from pathlib import Path
import pytest
from taxotagger.utils import download_from_url
from taxotagger.utils import parse_fasta
from taxotagger.utils import parse_unite_fasta_header


################################################################################
# Test download_from_url function
################################################################################

# URL to download example file (DOWNLOAD_TEST.md, size 32 bytes)
URL = "https://zenodo.org/records/13928229/files/DOWNLOAD_TEST.md"


def test_download_from_url(tmp_path):
    result = download_from_url(URL, tmp_path)
    assert result == str(tmp_path / "DOWNLOAD_TEST.md")
    assert Path(result).stat().st_size == 32


def test_download_from_url_overwrite_existing(tmp_path):
    # Create an empty existing file
    fpath = tmp_path / "DOWNLOAD_TEST.md"
    fpath.touch()

    result = download_from_url(URL, tmp_path, overwrite_existing=True)
    assert Path(result).stat().st_size == 32


def test_download_from_url_not_overwrite_existing(tmp_path):
    # Create an empty existing file
    fpath = tmp_path / "DOWNLOAD_TEST.md"
    fpath.touch()

    result = download_from_url(URL, tmp_path, overwrite_existing=False)
    assert Path(result).stat().st_size == 0


################################################################################
# Test parse_unite_fasta_header function
################################################################################


def test_parse_unite_fasta_header_complete():
    header = ">MH855962|k__Fungi;p__Basidiomycota;c__Agaricomycetes;o__Corticiales;f__Corticiaceae;g__Waitea;s__Waitea_circinata|SH1011630.09FU"
    expected = [
        "MH855962",
        "Fungi",
        "Basidiomycota",
        "Agaricomycetes",
        "Corticiales",
        "Corticiaceae",
        "Waitea",
        "Waitea_circinata",
        "SH1011630.09FU",
    ]
    result = parse_unite_fasta_header(header)
    assert result == expected


def test_parse_unite_fasta_header_no_taxonomy():
    header = ">MH855962"
    expected = ["MH855962", "", "", "", "", "", "", "", ""]
    result = parse_unite_fasta_header(header)
    assert result == expected


def test_parse_unite_fasta_header_no_sh_id():
    header = ">MH855962|k__Fungi;p__Basidiomycota;c__Agaricomycetes;o__Corticiales;f__Corticiaceae;g__Waitea;s__Waitea_circinata"
    expected = [
        "MH855962",
        "Fungi",
        "Basidiomycota",
        "Agaricomycetes",
        "Corticiales",
        "Corticiaceae",
        "Waitea",
        "Waitea_circinata",
        "",
    ]
    result = parse_unite_fasta_header(header)
    assert result == expected


def test_parse_unite_fasta_header_partial_taxonomy():
    header = ">MH855962|k__Fungi;p__Basidiomycota;c__Agaricomycetes"
    expected = ["MH855962", "Fungi", "Basidiomycota", "Agaricomycetes", "", "", "", "", ""]
    result = parse_unite_fasta_header(header)
    assert result == expected


def test_parse_unite_fasta_header_empty():
    header = ">"
    expected = ["", "", "", "", "", "", "", "", ""]
    result = parse_unite_fasta_header(header)
    assert result == expected


################################################################################
# Test parse_fasta function
################################################################################


def test_parse_fasta_from_file_handle(tmp_path):
    fasta_data = ">seq1\nAAATTT\n>seq2\nCCCGGG\n"
    fasta_file = tmp_path / "test.fasta"
    fasta_file.write_text(fasta_data)

    expected = {
        "seq1": "AAATTT",
        "seq2": "CCCGGG",
    }
    with open(fasta_file, "r") as fh:
        result = parse_fasta(fh)
    assert result == expected


def test_parse_fasta_from_file(tmp_path):
    fasta_data = """>seq1\nAAATTT\n>seq2\nCCCGGG\n"""
    fasta_file = tmp_path / "test.fasta"
    fasta_file.write_text(fasta_data)

    expected = {
        "seq1": "AAATTT",
        "seq2": "CCCGGG",
    }
    # test the Path object
    result = parse_fasta(fasta_file)
    assert result == expected

    # test the string path
    result = parse_fasta(str(fasta_file))
    assert result == expected


def test_parse_fasta_from_string_content():
    fasta_data = ">seq1\nAAATTT\n>seq2\nCCCGGG\n"
    expected = {
        "seq1": "AAATTT",
        "seq2": "CCCGGG",
    }
    result = parse_fasta(fasta_data)
    assert result == expected


def test_parse_fasta_duplicate_headers():
    fasta_data = ">seq1\nAAATTT\n>seq2\nCCCGGG\n>seq1\nTTTAAA\n"
    with pytest.raises(ValueError, match="Duplicate fasta header: seq1"):
        parse_fasta(fasta_data)
