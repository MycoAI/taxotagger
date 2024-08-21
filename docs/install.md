
# Installation

## Pre-requisites

- Python ≥3.10
- [Conda](https://docs.conda.io/en/latest/miniconda.html) (optional but recommended)


## Install from PyPI

```bash title="Install taxotagger package"
# create an virtual environment
conda create -n venv-3.10 python=3.10
conda activate venv-3.10

# install the package (pre-release)
pip install --pre taxotagger  # (1)!
```

1. Taxotagger might be released as [pre-release](https://pypi.org/project/taxotagger/#history). To install the pre-release, you need the `--pre` option. 

## Install from source code:
```bash title="Install from this repo"
# create an virtual environment
conda create -n venv-3.10 python=3.10
conda activate venv-3.10

# install from the source code
pip install git+https://github.com/MycoAI/taxotagger
```