# Custom Embedding Models

One of the key features of TaxoTagger is the ability to use custom embedding models. This allows users to use their own models or models from other sources to calculate the embeddings for the given FASTA file. 

TaxoTagger comes with a few [pre-trained models][taxotagger.defaults.PRETRAINED_MODELS], but users can add their own models to the tool. For this, users need to follow the steps below.


!!! Warning "Model format"
    Currently, TaxoTagger only supports PyTorch models. If you have a model in another framework, you could convert it to PyTorch before using it with TaxoTagger. 


## 1. Register your custom embedding model in the [`PRETRAINED_MODELS`][taxotagger.defaults.PRETRAINED_MODELS] dictionary

The name of the models are the keys of the dictionary, and the values are the download URLs. 

The model names should be unique and should not contain any spaces. The download URLs should be direct download links to the model files. Most importantly, **the name of the downloaded file should be the same as the model name, with the extension `.pt`**.

For example, your custom model is named `Example-Transformer`, and the model files should be named `Example-Transformer.pt`, then you can add the following entry to the `PRETRAINED_MODELS` dictionary:

```python
PRETRAINED_MODELS = {
    "MycoAI-CNN": "https://zenodo.org/records/10904344/files/MycoAI-CNN.pt",
    "MycoAI-BERT": "https://zenodo.org/records/10904344/files/MycoAI-BERT.pt",
    "Example-Transformer": "https://example.com/Example-Transformer.pt" # (1)!
}
```


## 2. Implement a new wrapper class for the embedding model

Add a new wrapper class for the embedding model to the [`taxotagger.models`][taxotagger.models] module ([source code file](https://github.com/MycoAI/taxotagger/blob/main/src/taxotagger/models.py)). The wrapper class should inherit from the [`EmbedModelBase`][taxotagger.abc.EmbedModelBase] abstract class and implement the `embed`method to calculate the embeddings for the given FASTA file.

Here is an example of a custom embedding model wrapper class:

```python
# For clarity, we omitted the imports and other parts of the code, e.g. docstring

def ExampleTransformerEmbedModel(EmbedModelBase): 

    name = "Example-Transformer" # (1)!

    def __init__(self, config: ProjectConfig) -> None: # (2)!
        self._config = config
        self.model = load_model(self.name, config)

    def embed(self, fasta_file: str) -> dict[str, list[dict[str, Any]]]: # (3)!
        # Parse input FASTA file
        sequences = read_fasta(fasta_file)
        # Calculate embeddings
        embeddings = self.model(sequences)
        # Return the embeddings
        return embeddings
```

1. It's important to set the `name` attribute to the name of the model.
2. It's  recommended to add a constructor to the class to load the model. 
3. The `embed` method should calculate the embeddings for the given FASTA file and return them as a dictionary. The logic for calculating the embeddings is specific to the model, and you should implement it accordingly.


## 3. Add the new wrapper class to the [`ModelFactory.get_model`][taxotagger.models.ModelFactory.get_model] method

After implementing the new wrapper class, you need to add it to the [`ModelFactory.get_model`][taxotagger.models.ModelFactory.get_model] method ([source code file](https://github.com/MycoAI/taxotagger/blob/main/src/taxotagger/models.py)). This method should return the wrapper class for the given model name.

Here is an example for adding the new wrapper class `ExampleTransformerEmbedModel`:

```python

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
        elif model_id == "Example-Transformer": # (1)!
            return ExampleTransformerEmbedModel(config) # (2)!
        # Add more embedding models here if needed
        else:
            raise ValueError(
                f"Invalid model id {model_id}. Valid models are {PRETRAINED_MODELS.keys()}"
            )
```

1. Add the new model name to the `ModelFactory.get_model` method.
2. Return the new wrapper class for the given model name.


## 4. Test the custom embedding model

Implement a test case for the custom embedding model to ensure that it works correctly. You can add the unit tests to the file [`test_models.py`](https://github.com/MycoAI/taxotagger/blob/main/tests/test_models.py).


## 5. Submit a pull request or build your own version of TaxoTagger
You can submit a pull request to the [TaxoTagger repository](https://github.com/MycoAI/taxotagger) to add your custom embedding model to the tool. Alternatively, you can build your own version of TaxoTagger with the custom embedding model and use it for your projects.