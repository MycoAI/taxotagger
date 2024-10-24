# Quick Start

## Build a vector database 

```python title="Build a vector database from a FASTA file"
from taxotagger import ProjectConfig
from taxotagger import TaxoTagger

config = ProjectConfig()
tt = TaxoTagger(config)

tt.create_db('data/database.fasta') # (1)!
```

1. The data is available in the [repo](https://github.com/MycoAI/taxotagger/tree/main/data).

Run the code above, you will see the following messages:

```log
[2024-08-22 09:45:42] INFO     Embedding the DNA sequences in data/database.fasta using the model MycoAI-CNN                              taxotagger.py:69
Downloading https://zenodo.org/records/10904344/files/MycoAI-CNN.pt to ~/.cache/mycoai
Downloading MycoAI-CNN.pt ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
[2024-08-22 09:46:06] INFO     Loading model MycoAI-CNN from ~/.cache/mycoai/MycoAI-CNN.pt                                                utils.py:97
[2024-08-22 09:46:12] INFO     Creating vector database for the DNA sequences in data/database.fasta at ~/.cache/mycoai/MycoAI-CNN.db     taxotagger.py:199
[2024-08-22 09:47:21] INFO     Database created successfully at ~/.cache/mycoai/MycoAI-CNN.db                                             taxotagger.py:230
```


By default,  the `~/.cache/mycoai` folder is used to store the vector database and the embedding model. The [`MycoAI-CNN.pt`](https://zenodo.org/records/10904344) model is automatically downloaded to this folder if it is not there, and the vector database is created and named after the model.

You can use a different embedding model by specifying the model name:

```python title="Using a different embedding model"

tt.create_db('data/database.fasta', model_id='other_model_name') # (1)!
```

1. Just the name of the model without the `.pt` extension.

You may want to integrate TaxoTagger with your own embedding model. See the [Custom Embedding Models][custom-embedding-models] guide for more details.



## Semantic searching

After building the vector database, you can conduct a semantic search with a query FASTA file:

```python title="Conduct a semantic search with FASTA file"
from taxotagger import ProjectConfig
from taxotagger import TaxoTagger

config = ProjectConfig()
tt = TaxoTagger(config)

res = tt.search('data/query.fasta', limit=1) # (1)!
```

1. The `limit` parameter specifies the number of top results to return for each query sequence. If you want to return the top 3 results, you can set `limit=3`.

The [`data/query.fasta` file](https://github.com/MycoAI/taxotagger/tree/main/data) contains two query sequences:
```txt
--8<-- "data/query.fasta"
```

The search results `res` will be a dictionary with [taxonomic level names][taxotagger.defaults.TAXONOMY_LEVELS] as keys and matched results as values for each of the two query sequences. For example, `res['phylum']` will look like:

```python title="Search results for phylum"
[
    [{"id": "KY106088", "distance": 1.0, "entity": {"phylum": "Ascomycota"}}],
    [{"id": "KY106087", "distance": 0.9999998807907104, "entity": {"phylum": "Ascomycota"}}]
]
```

The first inner list is the top results for the first query sequence, and the second inner list is the top results for the second query sequence.

The `id` field is the sequence ID of the matched sequence. The `distance` field is the cosine similarity between the query sequence and the matched sequence with a value between 0 and 1, the closer to 1, the more similar. The `entity` field is the taxonomic information of the matched sequence. 

We can see that the top 1 results for both query sequences are exactly themselves. This is because the query sequences are also in the database. You can try with different query sequences to see the search results.


## Project configuration

The [`ProjectConfig` class][taxotagger.ProjectConfig] is used to configure the project settings. 

You can change the settings by creating an instance of the class and setting the attributes:

```python title="Change project settings after creating the instance"
from taxotagger import ProjectConfig

config = ProjectConfig()

# Change cache folder
config.mycoai_home = '~/temp_dir' 

# Use GPU for computation
config.device = 'cuda'

# Force re-download and reload embedding model
config.force_reload = True

# Set the log level to DEBUG
config.log_level = 'DEBUG'

# Log to a file
config.log_file = '~/taxotagger.log'

# Do not log to console
config.log_to_console = False
```

Or you can set the attributes directly when creating the instance:
```python title="Change project settings when creating the instance"
from taxotagger import ProjectConfig

config = ProjectConfig(
    mycoai_home='~/temp_dir',
    device='cuda',
    force_reload=True,
    log_level='DEBUG',
    log_file='~/taxotagger.log',
    log_to_console=False
)
```

After creating the instance, you can pass the `config` object to the [`TaxoTagger` class][taxotagger.TaxoTagger] to use the settings:

```python title="Pass the config object to the TaxoTagger class"
from taxotagger import TaxoTagger

tt = TaxoTagger(config)
```

!!! Tip
    The settings are read only when creating the `TaxoTagger` instance. 
    
    So if you change the settings after creating the instance, the changes will not take effect. You need to create a new `TaxoTagger` instance with the updated settings.


## Use custom embedding models

You can use your own embedding models with TaxoTagger, such as using pre-trained models like transformers or creating domain-specific embeddings to enhance search accuracy.
For that, please check the [Custom Embedding Models][custom-embedding-models] guide.

## Use webapp

You can use the [TaxoTagger webapp](https://github.com/MycoAI/taxotagger-webapp) to interact with the library seamlessly. 
The webapp provides a user-friendly interface to conduct semantic searches and visualize the search results.
On how to deploy and use the webapp, please check the [TaxoTagger Webapp][taxotagger-webapp] guide.