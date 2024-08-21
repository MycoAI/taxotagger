# How to setup logging
TaxoTagger uses the standard library [logging](https://docs.python.org/3/library/logging.html#module-logging) 
module for managing log messages and the python library [rich](https://rich.readthedocs.io/en/latest/logging.html) 
to colorize the log messages. Depending on how you use TaxoTagger, you can set up logging in different ways.

## TaxoTagger as an application
If you're using TaxoTagger as an application, you are using the [`TaxoTagger` class][taxotagger.TaxoTagger], 
like the example described in the [Quickstart][quick-start]. In this case, you can set up logging with the [configuration][project-configuration]. 

## TaxoTagger as a library
If you're using TaxoTagger as a library, you're using some other functions or classes in your script. 
By default, TaxoTagger will not log any messages. However, you can set up logging in your script with 
the [`setup_logging` function][taxotagger.setup_logging]:

```python title="Set up logging in 'your_script.py'"
# Set up logging configuration first
from TaxoTagger import setup_logging

setup_logging(level="DEBUG", file="taxotagger.log", to_console=True) # (1)!

# Your business code here
# e.g. download a model from the internet to `~/temp_dir` folder
from TaxoTagger.utils import download_from_url

url = "https://zenodo.org/records/10904344/files/MycoAI-CNN.pt"
download_from_url(url, "~/temp_dir")
```

1. The [`setup_logging` function][taxotagger.setup_logging] sets up the logging settings:
    - The `level` sets the logging level, e.g. `NONSET`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.
    - The `file` sets the path to the log file. 
    - The `to_console` sets whether to log messages to your console.

Run the script above, you will see the log messages in the console and the log file `taxotagger.log` in the current working directory.