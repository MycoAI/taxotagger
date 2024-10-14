# Custom Embedding Models

You can use your own embedding model with TaxoTagger. This guide will show you how to integrate your model with TaxoTagger.

## Steps

1. Add the name of the embedding model and the link to download the model to the constant variable `PRETRAINED_MODELS` in the `taxotagger.defaults` module.
2. Add a new wrapper class for the embedding model by implementing the `EmbedModelBase` interface in the `taxotagger.abc` module. There you need to implement the `embed` method to calculate the embeddings for the given FASTA file.
3. Add the new wrapper class to the `ModelFactory.get_model` method in the `taxotagger.models` module.