import logging
from .config import ProjectConfig
from .taxotagger import TaxoTagger


logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Cunliang Geng"
__email__ = "c.geng@esciencecenter.nl"
__version__ = "0.0.1-alpha.1"

__all__ = ["ProjectConfig", "TaxoTagger"]
