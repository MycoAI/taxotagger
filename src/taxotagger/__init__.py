import logging
from .config import ProjectConfig
from .logger import setup_logging
from .taxotagger import TaxoTagger


logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Cunliang Geng"
__email__ = "c.geng@esciencecenter.nl"
__version__ = "0.0.1-alpha.7"

__all__ = ["ProjectConfig", "setup_logging", "TaxoTagger"]
