# TaxoTagger

 [![pypi badge](https://img.shields.io/pypi/v/taxotagger.svg?color=blue)](https://pypi.python.org/project/taxotagger/)
 [![Static Badge](https://img.shields.io/badge/🧬_Docs_🧬-826644)](https://mycoai.github.io/taxotagger)[](https://mycoai.github.io/taxotagger)

TaxoTagger is an open-source Python library for DNA taxonomy identification, which involves categorizing DNA sequences into their respective taxonomic groups. It is powered by deep learning and semantic search to provide efficient and accurate results.

Key Features:

- 🚀 **Build vector databases** from DNA sequences with ease
- ⚡ Conduct **efficient semantic searches** for precise results
- 🛠 Extend support for **custom embedding models** effortlessly
- 🌐 Interact seamlessly through a **[user-friendly web app](https://github.com/MycoAI/taxotagger-webapp)**

## Installation

TaxoTagger requires Python 3.10 or later.

```bash
# create an virtual environment
conda create -n venv-3.10 python=3.10
conda activate venv-3.10

# install the `taxotagger` package
pip install --pre taxotagger
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

By default,  the `~/.cache/mycoai` folder is used to store the vector database and the embedding model. The [`MycoAI-CNN.pt`](https://zenodo.org/records/10904344) model is automatically downloaded to this folder if it is not there, and the vector database is created and named after the model.


### Conduct a semantic search with FASTA file
```python
from taxotagger import ProjectConfig
from taxotagger import TaxoTagger

config = ProjectConfig()
tt = TaxoTagger(config)

# semantic search and return the top 1 result for each query sequence
res = tt.search('data/query.fasta', limit = 1)
```

The [`data/query.fasta` file](data/query.fasta) contains two query sequences: `KY106088` and `KY106087`. 

The search results `res` will be a dictionary with taxonomic level names as keys and matched results as values for each of the two query sequences. For example, `res['phylum']` will look like:

```python
[
    [{"id": "KY106088", "distance": 1.0, "entity": {"phylum": "Ascomycota"}}],
    [{"id": "KY106087", "distance": 0.9999998807907104, "entity": {"phylum": "Ascomycota"}}]
]
```

The first inner list is the top results for the first query sequence, and the second inner list is the top results for the second query sequence.

The `id` field is the sequence ID of the matched sequence. The `distance` field is the cosine similarity between the query sequence and the matched sequence with a value between 0 and 1, the closer to 1, the more similar. The `entity` field is the taxonomic information of the matched sequence. 

We can see that the top 1 results for both query sequences are exactly themselves. This is because the query sequences are also in the database. You can try with different query sequences to see the search results.


## Docs
Please visit the [official documentation](https://mycoai.github.io/taxotagger) for more details.

## Question and feedback
Please submit [an issue](https://github.com/MycoAI/taxotagger/issues) if you have any question or feedback.

## Citation
If you use TaxoTagger in your work, please cite it by clicking the `Cite this repository` on right top of this page.
