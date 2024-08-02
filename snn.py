from __future__ import annotations

import argparse
from os import PathLike
from pathlib import Path

import httpx
import torch
import torch.nn.functional as F
from mycoai.data import Data
from rich import print
from rich.progress import Progress
from torch import nn


class SiameseNetwork(nn.Module):
    """Siamese Network for DNA barcode identification."""

    pretrained_model_url = "https://zenodo.org/records/10904344/files/MycoAI-CNN.pt"

    def __init__(self, device):
        super(SiameseNetwork, self).__init__()

        # Load pretrained CNN model
        self.cnn = self._load_model_from_url(self.pretrained_model_url, device)

    def _load_model_from_url(self, url: str, device: torch.device) -> nn.Module:
        """Load the pretrained model from the given URL.

        Args:
            url: The URL of the pretrained model.
            device: The device to load the model to.
        """
        model_path = download_model(url, ".")
        return torch.load(model_path, map_location=torch.device(device))

    def predict(self, seq1: str, seq2: str) -> None:
        """Predict the similarity between two DNA sequences.

        The similarity is represented by the Euclidean distance between the two sequences.

        Args:
            seq1: path to FASTA file containing the first DNA sequence
            seq2: path to FASTA file containing the second DNA sequence
        """
        self.eval()

        # get actual labels: id, phylum, class, order, family, genus, species
        label1 = Data(seq1).data.iloc[0, :7].to_list()
        label2 = Data(seq2).data.iloc[0, :7].to_list()

        # encode input data
        seq1 = self.cnn._encode_input_data(seq1)
        seq2 = self.cnn._encode_input_data(seq2)
        pred1 = self.cnn._predict(seq1)
        pred2 = self.cnn._predict(seq2)

        # calculate the Euclidean distance
        distances = ["Distance"]
        for i in range(len(pred1)):
            dist = F.pairwise_distance(pred1[i], pred2[i])
            distances.append(dist.item())

        # print the results
        print("Predictions:")
        for i in range(len(label1)):
            print(
                f"{label1[i]:<30}",
                f"{label2[i]:<30}",
                distances[i],
                sep="\t",
            )


def download_model(
    url: str,
    root: str | PathLike,
    http_method: str = "GET",
    allow_http_redirect: bool = True,
) -> str:
    """Download pretrained model from the given URL.

    The output file name is determined by the URL and saved to the given root directory.

    Args:
        url: The URL of the file to download.
        root: The directory to save the file to.
        http_method: The HTTP method to use. Defaults to "GET".
        allow_http_redirect: Whether to allow HTTP redirects. Defaults to True.

    Returns:
        The path to the downloaded file.
    """
    fpath = Path(root) / Path(url).name

    # check if the file already exists
    if fpath.exists():
        return str(fpath)

    # download the file if it does not exist
    with open(fpath, "wb") as fh:
        with httpx.stream(
            http_method, url, follow_redirects=allow_http_redirect
        ) as response:
            response.raise_for_status()
            print(f"Downloading {url} to {root}")
            total = int(response.headers.get("Content-Length", 0))

            with Progress() as progress:
                task = progress.add_task(
                    f"[hot_pink]Downloading {fpath.name}", total=total
                )
                for chunk in response.iter_bytes():
                    fh.write(chunk)
                    progress.update(task, advance=len(chunk))

    return str(fpath)


def predict():
    """Convenience function to predict the similarity between two DNA sequences"""

    parser = argparse.ArgumentParser(
        description="Siamese network for DNA barcode identification"
    )
    parser.add_argument(
        "--no-cuda", action="store_true", default=False, help="disables CUDA"
    )
    parser.add_argument(
        "--no-mps",
        action="store_true",
        default=False,
        help="disables macOS GPU",
    )
    parser.add_argument(
        "--seed", type=int, default=1, metavar="S", help="random seed (default: 1)"
    )
    parser.add_argument(
        "--dna1",
        type=str,
        default="data/dna1.fasta",
        help="input DNA sequence 1 (default: data/dna1.fasta)",
    )

    parser.add_argument(
        "--dna2",
        type=str,
        default="data/dna2.fasta",
        help="input DNA sequence 2 (default: data/dna2.fasta)",
    )

    args = parser.parse_args()

    use_cuda = not args.no_cuda and torch.cuda.is_available()
    use_mps = not args.no_mps and torch.backends.mps.is_available()
    if use_cuda:
        device = torch.device("cuda")
    elif use_mps:
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    model = SiameseNetwork(device).to(device)
    model.predict(args.dna1, args.dna2)


if __name__ == "__main__":
    predict()
