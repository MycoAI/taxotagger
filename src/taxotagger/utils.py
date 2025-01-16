from __future__ import annotations
import logging
import os
from io import StringIO
from os import PathLike
from pathlib import Path
from typing import Any
from typing import TextIO
import httpx
import torch
from Bio import SeqIO
from rich.progress import Progress
from .config import ProjectConfig
from .defaults import PRETRAINED_MODELS


logger = logging.getLogger(__name__)


def download_from_url(
    url: str,
    root: str | PathLike,
    overwrite_existing: bool = False,
    http_method: str = "GET",
    allow_http_redirect: bool = True,
) -> str:
    """Download data from the given URL.

    The output file name is determined by the URL and saved to the given `root` directory.

    Args:
        url: The URL of the file to download.
        root: The directory to save the file to.
        overwrite_existing: Whether to overwrite the existing file. Defaults to False.
        http_method: The HTTP method to use. Defaults to "GET".
        allow_http_redirect: Whether to allow HTTP redirects. Defaults to True.

    Returns:
        The path to the downloaded file.

    Examples:
        Download the MycoAI-CNN model to the current directory
        >>> url = "https://zenodo.org/records/10904344/files/MycoAI-CNN.pt"
        >>> download_model(url, ".")
    """
    fpath = Path(root) / Path(url).name

    if fpath.exists() and not overwrite_existing:
        return str(fpath)

    with open(fpath, "wb") as fh:
        with httpx.stream(http_method, url, follow_redirects=allow_http_redirect) as response:
            response.raise_for_status()
            print(f"Downloading {url} to {root}")
            total = int(response.headers.get("Content-Length", 0))

            with Progress() as progress:
                task = progress.add_task(f"[hot_pink]Downloading {fpath.name}", total=total)
                for chunk in response.iter_bytes():
                    fh.write(chunk)
                    progress.update(task, advance=len(chunk))

    return str(fpath)


def load_model(
    model_id: str,
    config: ProjectConfig,
) -> Any:
    """Load the pretrained model with pytorch for the given model identifier.

    Available models are defined in the default
    [`PRETRAINED_MODELS`][taxotagger.defaults.PRETRAINED_MODELS].
    If the model `{model_id}.pt` is not found in the cache, it will be downloaded from the
    predefined URL.

    Args:
        model_id: The identifier of the model to load.
        config: The configurations for the project.

    Returns:
        The pretrained model loaded with `torch.load`.

    Examples:
        >>> config = Config()
        >>> model = load_model("MycoAI-CNN", config)
    """
    # validate the model id
    if model_id not in PRETRAINED_MODELS:
        raise ValueError(
            f"Invalid model id {model_id}. Available models are {PRETRAINED_MODELS.keys()}"
        )

    # use cache or download the model
    model_dir = config.mycoai_home
    os.makedirs(model_dir, exist_ok=True)
    model_path = Path(model_dir) / f"{model_id}.pt"
    if not model_path.exists() or config.force_reload:
        download_from_url(PRETRAINED_MODELS[model_id], model_dir, config.force_reload)

    logger.info(f"Loading model [magenta]{model_id}[/magenta] from {model_path}")
    model = torch.load(model_path, map_location=config.device)
    return model


def parse_unite_fasta_header(header: str) -> list[str]:
    """Parse metadata from a UNITE FASTA file header.

    The header of a FASTA file must follow the formats:

    - the UNITE format:
        ```
        >Accession|k__Kingdom;p__Phylum;c__Class;o__Order;f__Family;g__Genus;s__Species|SHIdentifier
        ```
    - only the accession:
        ```
        >Accession
        ```

    Note that the `SHIdentifier` (Species Hypothesis identifier) is optional.

    Args:
        header: A string representing the header of a FASTA file from the UNITE database.

    Returns:
        A list of parsed metadata in the following order:
            `[Accession, Kingdom, Phylum, Class, Order, Family, Genus, Species, SH_ID]`.
            Empty strings are returned for missing metadata.

    Examples:
        Parse the header of a UNITE FASTA file
        >>> header = ">MH855962|k__Fungi;p__Basidiomycota;c__Agaricomycetes;o__Corticiales;f__Corticiaceae;g__Waitea;s__Waitea_circinata|SH1011630.09FU"
        >>> parse_unite_fasta_header(header)
        ['MH855962', 'Fungi', 'Basidiomycota', 'Agaricomycetes', 'Corticiales', 'Corticiaceae', 'Waitea', 'Waitea_circinata', 'SH1011630.09FU']

        Parse the header of a FASTA file with only the accession
        >>> process_unite_fasta_header(">MH855962")
        ['MH855962', '', '', '', '', '', '', '', '']
    """
    result = [""] * 9

    # Split the header into sections based on '|'
    header = header.lstrip(">")
    sections = header.split("|")

    # The accession is the first part
    result[0] = sections[0]

    # If there is a taxonomy section, process it
    if len(sections) > 1:
        taxonomy_parts = sections[1].split(";")
        taxonomy_map = {
            "k__": 1,  # Kingdom
            "p__": 2,  # Phylum
            "c__": 3,  # Class
            "o__": 4,  # Order
            "f__": 5,  # Family
            "g__": 6,  # Genus
            "s__": 7,  # Species
        }
        for part in taxonomy_parts:
            prefix, value = part[:3], part[3:]
            if prefix in taxonomy_map:
                result[taxonomy_map[prefix]] = value

    # If there is an SH ID section, add it
    if len(sections) > 2:
        result[8] = sections[2]

    return result


def parse_fasta(data: str | PathLike | TextIO) -> dict:
    """Parse  FASTA data and return a dictionary of sequences.

    Args:
        data: Can be one of the following:

            - A file-like object (with .read() or .readline() methods)
            - A file path (string or PathLike) to a FASTA file
            - A string containing FASTA content

    Returns:
        A dictionary with the FASTA headers as keys and the sequences as values.

    Raises:
        ValueError: If there are duplicate FASTA headers.
    """
    header_seq_dict = {}

    fh = _fasta_to_handle(data)
    for record in SeqIO.parse(fh, "fasta"):
        if record.description not in header_seq_dict:
            header_seq_dict[record.description] = str(record.seq)
        else:
            raise ValueError(f"Duplicate FASTA header found: `{record.description}`")
    return header_seq_dict


def _fasta_to_handle(data: str | PathLike | TextIO) -> TextIO:
    """Convert the input FASTA data to a file handle.

    Args:
        data: Can be one of the following:

            - A file-like object (with .read() or .readline() methods)
            - A file path (string or PathLike) to a FASTA file
            - A string containing FASTA content

    Returns:
        A file handle for the input data.

    Raises:
        TypeError: If the input data is not a valid type.
    """
    # Check if input_data is a file-like object
    if hasattr(data, "read") or hasattr(data, "readline"):
        file_handle = data
    elif isinstance(data, PathLike):
        file_handle = open(data, "r")
    elif isinstance(data, str):
        # Check if it's a file path
        if os.path.isfile(data):
            file_handle = open(data, "r")
        else:
            # Assume it's a string with FASTA content
            file_handle = StringIO(data)
    else:
        raise TypeError("Invalid input data type.")

    return file_handle
