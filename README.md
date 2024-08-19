# TaxoTagger

 [![pypi badge](https://img.shields.io/pypi/v/taxotagger.svg?color=blue)](https://pypi.python.org/project/taxotagger/)

Fungi DNA taxonomy label identification using semantic searching.

Features:
- Building vector databases directly from DNA sequences (FASTA file) with ease
- Supporting various embedding models
- Semantic searching with high efficiency

## Installation

Install from PyPI:

```bash
# create an virtual environment
conda create -n venv-3.10 python=3.10
conda activate venv-3.10

# install the `taxotagger` package
pip install --pre taxotagger
```

Or install from source code:
```bash
# create an virtual environment
conda create -n venv-3.10 python=3.10
conda activate venv-3.10

# install from this repo
pip install git+https://github.com/MycoAI/taxotagger
```

## Usage

### Build a vector database from a FASTA file

```python
from taxotagger import ProjectConfig
from taxotagger import TaxoTagger

config = ProjectConfig()
tt = TaxoTagger(config)

# creating the database will take ~30s
tt.create_db('data/database.fasta')
```

By default, the model [MycoAI-CNN.pt](https://zenodo.org/records/10904344) will be used as the embedding model, and the database will be created and stored in the default folder (`~/.cache/mycoai`) if you do not set a new value to `config.mycoai_home`. The embedding model is automatically downloaded to  there.


### Conduct a semantic search with FASTA file
```python
from taxotagger import ProjectConfig
from taxotagger import TaxoTagger

config = ProjectConfig()
tt = TaxoTagger(config)

# semantic search and return the top 1 result for each query sequence
res = tt.search('data/query.fasta', limit = 1)
```

The search results `res` will be a dictionary with taxonomic level names as keys and matched results as values for each query sequence. For example, `res['phylum']` will look like:

```python
[
    [{"id": "KY106088", "distance": 1.0, "entity": {"phylum": "Ascomycota"}}],
    [{"id": "KY106087", "distance": 0.9999998807907104, "entity": {"phylum": "Ascomycota"}}]
]
```

The first inner list is the top results for the first query sequence, and the second inner list is the top results for the second query sequence.


# Question and feedback
Please submit [an issue](https://github.com/MycoAI/taxotagger/issues) if you have any question or feedback.