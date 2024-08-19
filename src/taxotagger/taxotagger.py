import logging
import os
import warnings
from typing import Any
from pymilvus import DataType
from pymilvus import MilvusClient
from .config import ProjectConfig
from .defaults import TAXONOMY_LEVELS
from .models import ModelFactory


logger = logging.getLogger(__name__)


class TaxoTagger:
    """The taxonomy tagger class."""

    def __init__(self, config: ProjectConfig) -> None:
        self.config = config

    def embed(
        self,
        fasta_file: str,
        model_id: str = "MycoAI-CNN",
    ) -> dict[str, list[dict[str, Any]]]:
        """Embed the DNA sequences in the fasta file using the specified model.

        This is a wrapper function for the `embed` method of each embedding model.
        See the `models` module for more details on each model.

        Args:
            fasta_file (str): The path to the fasta file.
            model_id (str): The model ID to use for embedding the DNA sequences.

        Returns:
            dict[str, list[dict[str, Any]]]: A dictionary of embeddings for each taxonomy level.
                The dictionary keys are the taxonomy levels, and the values are lists of dictionaries
                containing the id, embeddings and metadata for each sequence.

                The shape of the list is (n_samples), where n_samples is the number of sequences.

                The keys of the inside dictionaries are: "id", "vector", taxonomy levels ("phylum",
                "class", "order", "family", "genus", and "species"), and other metadata fields.

                The shape of the "vector" is (n_features), where n_features is the number of features
                in the embedding.

                The returned data looks like:
                ```
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
            >>> tagger = TaxoTagger(config)
            >>> embeddings = tagger.embed("dna1.fasta")
        """
        model = ModelFactory.get_model(model_id, self.config)
        return model.embed(fasta_file)

    def search(
        self,
        fasta_file: str,
        output_taxonomies: list = [],
        output_metadata: list = [],
        model_id: str = "MycoAI-CNN",
        db_name: str = "",
        **kwargs,
    ) -> dict[str, list[list[dict]]]:
        """Conduct a vector similarity search for the DNA sequences in the fasta file.

        Args:
            fasta_file: The path to the fasta file.
            output_taxonomies: List of taxonomy levels to include in the output. Defaults to all taxonomy levels.
            output_metadata: List of metadata fields to include in the output. Defaults to an empty list.
            model_id: The model ID to use for embedding the DNA sequences. Defaults to "MycoAI-CNN".
            db_name: The name of the database to search. Defaults to the model ID.
            kwargs: Additional keyword arguments to pass to the `search` method of the Milvus client.
                For example:

                - `limit`: The maximum number of matched results to return. Defaults to 10.
                - `filter`: The filtering condition to filter matched results.
                - `timeout`: The timeout in seconds for the search operation. Defaults to 60.

                See the `search` method of the Milvus client for more details:
                https://milvus.io/api-reference/pymilvus/v2.4.x/MilvusClient/Vector/search.md.

        Returns:
            dict[str, list[list[dict]]]: A dictionary of search results for each taxonomy level
                defined in `output_taxonomies`. The dictionary keys are the taxonomy levels, and
                the values are a list of search results (`list[dict]`) for each sequence.

                The search result for one sequence is a list of dictionaries, where the length of
                the list is the `limit` you set in the search, by default it is 10, i.e. the top 10
                matched sequences.

        Examples:
            >>> config = ProjectConfig()
            >>> tagger = TaxoTagger(config)
            >>> results = tagger.search("dna1.fasta")
        """
        # Remove `collection_name`, `data` or `output_fields` from  kwargs if they are present
        kwargs = {
            k: v for k, v in kwargs.items() if k not in ["collection_name", "data", "output_fields"]
        }

        # Get the embeddings for the query
        query_embedding = self.embed(fasta_file, model_id)

        #  Get output fields
        output_taxonomies = self._validate_taxonomies(output_taxonomies)
        output_taxonomies = output_taxonomies if output_taxonomies else list(TAXONOMY_LEVELS)
        if not output_taxonomies:
            output_taxonomies = list(TAXONOMY_LEVELS)
        output_fields = output_taxonomies + output_metadata

        db_name = db_name if db_name else f"{model_id}.db"
        db_path = os.path.join(self.config.mycoai_home, db_name)
        # TODO: Check if the database exists and download it if it does not exist

        client = MilvusClient(db_path)
        results = {}
        for taxo_level in output_taxonomies:
            res = client.search(
                collection_name=taxo_level,
                data=[d["vector"] for d in query_embedding[taxo_level]],
                output_fields=output_fields,
                **kwargs,
            )
            results[taxo_level] = res
        client.close()

        return results

    def create_db(self, fasta_file: str, model_id: str = "MycoAI-CNN", db_name: str = "") -> None:
        """Create a vector database for the DNA sequences in the fasta file with Milvus.

        Args:
            fasta_file: The path to the fasta file.
            model_id: The model ID to use for embedding the DNA sequences. Defaults to "MycoAI-CNN".
            db_name: The name of the database to create. Defaults to the model ID.

        Examples:
            >>> config = ProjectConfig()
            >>> tagger = TaxoTagger(config)
            >>> tagger.create_db("dna.fasta")
        """
        # Get the embeddings including the headers
        embeddings = self.embed(fasta_file, model_id)

        # Create the schema and index for the database
        dims = {
            taxonomy_level: embeddings[taxonomy_level][0]["vector"].shape[0]
            for taxonomy_level in TAXONOMY_LEVELS
        }
        schema_index_dict = self._create_schema_index(dims)

        db_name = db_name if db_name else f"{model_id}.db"
        db_path = os.path.join(self.config.mycoai_home, db_name)

        client = MilvusClient(db_path)

        # Create collections for each taxonomy level
        for taxo_level in TAXONOMY_LEVELS:
            schema, index_params = schema_index_dict[taxo_level]

            if client.has_collection(collection_name=taxo_level):
                client.drop_collection(collection_name=taxo_level)

            client.create_collection(
                collection_name=taxo_level,
                schema=schema,
                index_params=index_params,
            )

        # Insert the data with batch insert
        for taxo_level in TAXONOMY_LEVELS:
            batch_size = 1000
            for i in range(0, len(embeddings[taxo_level]), batch_size):
                client.insert(
                    collection_name=taxo_level, data=embeddings[taxo_level][i : i + batch_size]
                )

        client.close()

    def _validate_taxonomies(self, taxonomies: list[str]) -> list[str]:
        """Validate the taxonomy levels and return the valid ones.

        Invalid taxonomy levels are ignored and a warning is raised.
        """
        invalid_levels = [taxonomy for taxonomy in taxonomies if taxonomy not in TAXONOMY_LEVELS]
        if invalid_levels:
            logger.warning(
                f"Invalid taxonomy levels provided: {invalid_levels}, which will be ignored. "
                f"Available levels are: {TAXONOMY_LEVELS}",
            )
            warnings.warn(
                f"Invalid taxonomy levels provided: {invalid_levels}, which will be ignored. "
                f"Available levels are: {TAXONOMY_LEVELS}",
            )

        valid_levels = [taxonomy for taxonomy in taxonomies if taxonomy in TAXONOMY_LEVELS]
        return valid_levels

    @staticmethod
    def _create_schema_index(dims) -> dict[str, tuple]:
        """Create the schema and index parameters for the Milvus database.

        Args:
            dims: The dimensions of the embeddings for each taxonomy level.

        Returns:
            dict[str, tuple]: A dictionary of (CollectionSchema, IndexParams) for each taxonomy
                level.
        """
        res = {}
        for taxo_level in TAXONOMY_LEVELS:
            # Create schema for the collection and add fields to the schema
            schema = MilvusClient.create_schema(
                auto_id=False,
                enable_dynamic_field=True,
                description=f"The collection of embeddings on the taxonomy level {taxo_level}",
            )
            schema.add_field(
                field_name="id",
                datatype=DataType.VARCHAR,
                max_length=20,
                is_primary=True,
                description="The unique identifier of the DNA sequence. The length limit is 20.",
            )
            schema.add_field(
                field_name="vector",
                datatype=DataType.FLOAT_VECTOR,
                dim=dims[taxo_level],
                description="The embedding vector of the DNA sequence",
            )
            schema.add_field(
                field_name=taxo_level,
                datatype=DataType.VARCHAR,
                max_length=100,
                description=f"The {taxo_level} of the DNA sequence. The length limit is 100.",
            )

            # Set up index parameters and add indexes
            # Note: local mode only support FLAT, HNSW, AUTOINDEX
            ## Use auto indexing for `id` and taxo_level field https://milvus.io/docs/index-scalar-fields.md#Auto-indexing
            index_params = MilvusClient.prepare_index_params()
            index_params.add_index(field_name="id")
            index_params.add_index(
                field_name="vector",
                index_type="FLAT",
                metric_type="COSINE",
            )
            index_params.add_index(field_name=taxo_level)

            res[taxo_level] = (schema, index_params)

        return res
