from __future__ import annotations
from typing import Any
import torch
from mycoai import data
from torch.utils.data import DataLoader
from .abc import EmbedModelBase
from .config import ProjectConfig
from .defaults import PRETRAINED_MODELS
from .defaults import TAXONOMY_LEVELS
from .utils import load_model
from .utils import parse_unite_fasta_header


class ModelFactory:
    """Factory class to get the embedding model for the given model identifier."""

    @staticmethod
    def get_model(model_id: str, config: ProjectConfig) -> EmbedModelBase:
        """Get the embedding model for the given model identifier.

        Args:
            model_id: The identifier of the model to load.
            config: The configurations for the project.

        Returns:
            The embedding model instance for the given model identifier.

        Examples:
            >>> config = ProjectConfig()
            >>> model = ModelFactory.get_model("MycoAI-CNN", config)
        """
        if model_id == "MycoAI-CNN":
            return MycoAICNNEmbedModel(config)
        elif model_id == "MycoAI-BERT":
            return MycoAIBERTEmbedModel(config)
        # Add more embedding models here if needed
        else:
            raise ValueError(
                f"Invalid model id {model_id}. Valid models are {PRETRAINED_MODELS.keys()}"
            )


###################################################################################################
# Define your embedding models below
# After defining the models, add them to the `ModelFactory.get_model` method
###################################################################################################


class MycoAICNNEmbedModel(EmbedModelBase):
    """Embedding model for the pretrained MycoAI-CNN."""

    name = "MycoAI-CNN"

    def __init__(self, config: ProjectConfig) -> None:
        self._config = config
        self.model = load_model(self.name, config)

    def embed(self, fasta_file: str) -> dict[str, list[dict[str, Any]]]:
        """Calculate the embeddings for the given FASTA file.

        Args:
            fasta_file: The path to the FASTA file to embed.

        Returns:
            A dictionary of embeddings for each taxonomy level.
                The dictionary keys are the taxonomy levels, and the values are lists of dictionaries
                containing the id, embeddings and metadata for each sequence.

                The shape of the list is `(n_samples)`, where `n_samples` is the number of sequences.

                The keys of the inside dictionaries are: `id`, `vector`, and the taxonomy levels
                (e.g. `phylum`, `class`, `order`, `family`, `genus`, `species`) and other metadata
                fields present in the FASTA header.

                The shape of the `vector` is `(n_features)`, where `n_features` is the number of
                features in the embedding. The number of features for each taxonomy level is:

                    - phylum: 18
                    - class: 70
                    - order: 231
                    - family: 791
                    - genus: 3695
                    - species: 14742

                The returned data looks like:
                ```python
                {
                "phylum": [{"id": "seq1", "vector": [0.1, 0.2, ...], "phylum": "Basidiomycota", ...}, ...],
                "class": [{"id": "seq1", "vector": [0.5, 0.6, ...], "class": "Agaricomycetes", ...}, ...],
                "order": [{"id": "seq1", "vector": [0.9, 0.8, ...], "order": "Corticiales", ...}, ...],
                "family": [{"id": "seq1", "vector": [0.3, 0.4, ...], "family": "Corticiaceae", ...}, ...],
                "genus": [{"id": "seq1", "vector": [0.7, 0.8, ...], "genus": "Waitea", ...}, ...],
                "species": [{"id": "seq1", "vector": [0.5, 0.6, ...], "species": "Circinata", ...}, ...]
                }
                ```

        Examples:
            >>> config = ProjectConfig()
            >>> model = MycoAICNNEmbedModel(config)
            >>> embeddings = model.embed("dna1.fasta")
        """
        headers, encoded_data = self.parse_and_encode_fasta(fasta_file)
        # headers shape (n_samples, n_headers), e.g.
        # [['id1', 'phylum1', 'class1', 'order1', 'family1', 'genus1', 'species1', 'SH_id1'], ...]

        embeddings = []
        dataloader = DataLoader(encoded_data, shuffle=False)
        with torch.no_grad():
            for x, _ in dataloader:  # (encoded data, labels)
                y_pred = self.model(x.to(self._config.device))
                embeddings.append(y_pred)
        # embeddings shape (n_samples, n_taxonomies, (1, n_features)), where n_taxonomies is 6, e.g.
        # [[phylumTensor1, classTensor1, orderTensor1, familyTensor1, genusTensor1, speciesTensor1], ...]
        # the shape of each tensor is (1, n_features), n_features are different for each taxonomy level

        data_collections = {}
        for i, taxo_level in enumerate(TAXONOMY_LEVELS):
            data_list = [
                {
                    "id": headers[j][0],
                    # squeeze to remove the batch dimension: (1, n_features) -> (n_features)
                    "vector": embeddings[j][i].squeeze().numpy(),
                    taxo_level: headers[j][i + 2],
                    "SH_id": headers[j][-1],
                }
                for j in range(len(embeddings))
            ]
            data_collections[taxo_level] = data_list
        return data_collections

    def parse_and_encode_fasta(self, fasta_file: str) -> tuple[list[list[str]], data.TensorData]:
        """Parse headers and encode the sequences in the given FASTA file.

        The sequences are encoded using the encoders defined in the pretrained model.

        Args:
            fasta_file: The path to the FASTA file.

        Returns:
            A tuple containing the headers and the encoded data for the sequences in the FASTA file.

                The shape of the headers is `(n_samples, n_headers)`, where `n_samples` is the
                number of sequences and `n_headers` is the 9 metadata fields parsed from the header.
        """
        input_data = data.Data(fasta_file, tax_parser=None, allow_duplicates=False)
        # Using custom parser to parse the FASTA headers
        headers = [parse_unite_fasta_header(header) for header in input_data.data["id"].values]
        encoded_data = input_data.encode_dataset(self.model.dna_encoder, self.model.tax_encoder)
        return headers, encoded_data


class MycoAIBERTEmbedModel(EmbedModelBase):
    """Embedding model for the pretrained MycoAI-BERT."""

    name = "MycoAI-BERT"

    def __init__(self, config: ProjectConfig) -> None:
        self._config = config
        self.model = load_model(self.name, config)

    def embed(self, fasta_file: str) -> dict[str, list[dict[str, Any]]]:
        """Calculate the embeddings for the given FASTA file.

        Args:
            fasta_file: The path to the FASTA file to embed.

        Returns:
            A dictionary of embeddings for each taxonomy level.
                The dictionary keys are the taxonomy levels, and the values are lists of dictionaries
                containing the id, embeddings and metadata for each sequence.

                The shape of the list is `(n_samples)`, where `n_samples` is the number of sequences.

                The keys of the inside dictionaries are: `id`, `vector`, and the taxonomy levels
                (e.g. `phylum`, `class`, `order`, `family`, `genus`, `species`) and other metadata
                fields present in the FASTA header.

                The shape of the `vector` is `(n_features)`, where `n_features` is the number of
                features in the embedding. The number of features for each taxonomy level is:

                    - phylum: 18
                    - class: 70
                    - order: 231
                    - family: 791
                    - genus: 3695
                    - species: 14742

                The returned data looks like:
                ```python
                {
                "phylum": [{"id": "seq1", "vector": [0.1, 0.2, ...], "phylum": "Basidiomycota", ...}, ...],
                "class": [{"id": "seq1", "vector": [0.5, 0.6, ...], "class": "Agaricomycetes", ...}, ...],
                "order": [{"id": "seq1", "vector": [0.9, 0.8, ...], "order": "Corticiales", ...}, ...],
                "family": [{"id": "seq1", "vector": [0.3, 0.4, ...], "family": "Corticiaceae", ...}, ...],
                "genus": [{"id": "seq1", "vector": [0.7, 0.8, ...], "genus": "Waitea", ...}, ...],
                "species": [{"id": "seq1", "vector": [0.5, 0.6, ...], "species": "Circinata", ...}, ...]
                }
                ```

        Examples:
            >>> config = ProjectConfig()
            >>> model = MycoAIBERTEmbedModel(config)
            >>> embeddings = model.embed("dna1.fasta")
        """
        headers, encoded_data = self.parse_and_encode_fasta(fasta_file)
        # headers shape (n_samples, n_headers), e.g.
        # [['id1', 'phylum1', 'class1', 'order1', 'family1', 'genus1', 'species1', 'SH_id1'], ...]

        embeddings = []
        dataloader = DataLoader(encoded_data, shuffle=False)
        with torch.no_grad():
            for x, _ in dataloader:  # (encoded data, labels)
                y_pred = self.model(x.to(self._config.device))
                embeddings.append(y_pred)
        # embeddings shape (n_samples, n_taxonomies, (1, n_features)), where n_taxonomies is 6, e.g.
        # [[phylumTensor1, classTensor1, orderTensor1, familyTensor1, genusTensor1, speciesTensor1], ...]
        # the shape of each tensor is (1, n_features), n_features are different for each taxonomy level

        data_collections = {}
        for i, taxo_level in enumerate(TAXONOMY_LEVELS):
            data_list = [
                {
                    "id": headers[j][0],
                    # squeeze to remove the batch dimension: (1, n_features) -> (n_features)
                    "vector": embeddings[j][i].squeeze().numpy(),
                    taxo_level: headers[j][i + 2],
                    "SH_id": headers[j][-1],
                }
                for j in range(len(embeddings))
            ]
            data_collections[taxo_level] = data_list
        return data_collections

    def parse_and_encode_fasta(self, fasta_file: str) -> tuple[list[list[str]], data.TensorData]:
        """Parse headers and encode the sequences in the given FASTA file.

        The sequences are encoded using the encoders defined in the pretrained model.

        Args:
            fasta_file: The path to the FASTA file.

        Returns:
            A tuple containing the headers and the encoded data for the sequences in the FASTA file.

                The shape of the headers is `(n_samples, n_headers)`, where `n_samples` is the
                number of sequences and `n_headers` is the 9 metadata fields parsed from the header.
        """
        input_data = data.Data(fasta_file, tax_parser=None, allow_duplicates=False)
        # Using custom parser to parse the FASTA headers
        headers = [parse_unite_fasta_header(header) for header in input_data.data["id"].values]
        encoded_data = input_data.encode_dataset(self.model.dna_encoder, self.model.tax_encoder)
        return headers, encoded_data
