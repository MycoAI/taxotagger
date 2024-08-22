from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import Any


class EmbedModelBase(ABC):
    """Base class for embedding models."""

    name: str
    """The name of the pretrained model used for embedding."""

    @abstractmethod
    def embed(self, fasta_file: str) -> dict[str, list[dict[str, Any]]]:
        """Calculate the embeddings for the given FASTA file.

        Args:
            fasta_file: The path to the FASTA file to embed.

        Returns:
            A dictionary of embeddings for each taxonomy level.
                The dictionary keys are the [taxonomy levels][taxotagger.defaults.TAXONOMY_LEVELS],
                and the values are lists of dictionaries containing the id, embeddings and metadata
                for each sequence.

                The shape of the list is `(n_samples)`, where `n_samples` is the number of sequences.

                The keys `id` and `vector` must be present in the inside dictionaries to present the
                accession and the embedding vector of the sequence, respectively.

                For example:
                ```python
                {
                    "phylum": [
                        {"id": "seq1", "vector": [0.1, 0.2, ...], "phylum": "Ascomycota", ...},
                        {"id": "seq2", "vector": [0.3, 0.4, ...], "phylum": "Basidiomycota", ...},
                        ...
                    ],
                    "class": [
                        {"id": "seq1", "vector": [0.5, 0.6, ...], "class": "Dothideomycetes", ...},
                        {"id": "seq2", "vector": [0.7, 0.8, ...], "class": "Agaricomycetes", ...},
                        ...
                    ],
                    ...
                }
                ```
        """
        ...
