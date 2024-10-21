"""This module contains the default values for this TaxoTagger library."""

DEFAULT_CACHE_DIR = "~/.cache/mycoai"
"""The default directory for storing downloads and cache files.

This is a constant and should not be modified.
"""

ENV_MYCOAI_HOME = "MYCOAI_HOME"
"""The environment variable name to set the working directory for the project.

If it is not set, the default directory `DEFAULT_CACHE_DIR` will be used.

On Linux or macOS, you can set the environment variable as follows:
```bash
export MYCOAI_HOME="~/mycoai"
```

Or in python, you can set it as follows:
```python
import os
os.environ["MYCOAI_HOME"] = "~/mycoai"
```
"""

PRETRAINED_MODELS = {
    "MycoAI-CNN": "https://zenodo.org/records/10904344/files/MycoAI-CNN.pt",
    "MycoAI-BERT": "https://zenodo.org/records/10904344/files/MycoAI-BERT.pt",
}
"""Pretrained models and their download URLs.

The keys are the model names, and the values are the download URLs. The names should be unique and 
should not contain any spaces. The download URLs should be direct download links to the model files,
and the name of the downloaded file should be the same as the model name.
"""

TAXONOMY_LEVELS = ["phylum", "class", "order", "family", "genus", "species"]
"""The list of taxonomy level names used in this package."""

MAX_BATCH_SIZE_BYTES = 64 * 1024 * 1024
"""The maximum batch size in bytes for the Milvus database.

Milvus has a limit of 64MB for input and output per RPC operation, including `insert`, `search`, and
`query` operations.

For more information, see the [Milvus documentation](https://milvus.io/docs/limitations.md).
"""
