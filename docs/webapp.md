# TaxoTagger Webapp

TaxoTagger webapp is a [user-friendly interface][webapp-demo] for the TaxoTagger library. It allows users to interact with the TaxoTagger library through a web browser. Users can upload DNA sequences and search for the taxonomy of the sequences using the TaxoTagger library.

The webapp is available at https://github.com/MycoAI/taxotagger-webapp.

Below are the instructions to deploy and use the webapp.

## Deployment for exploration

### Installation

1. Clone the repository to your local machine
```bash
git clone https://github.com/MycoAI/taxotagger-webapp.git
```

2. Install the required packages
```bash
# Go to the taxotagger-webapp directory
cd taxotagger-webapp

# Create a new conda environment `taxotagger-webapp`
conda create -n taxotagger-webapp python=3.10

# Go to the conda environment
conda activate taxotagger-webapp

# Install the required packages
pip install -r requirements.txt
```

### Run the webapp

1. Set the environment variables `MYCOAI_HOME`

    === "Linux or MacOS"
        ```bash
        export MYCOAI_HOME=/your/path/to/taxotagger-webapp/data
        ```

    === "Windows"
        ```bash
        set MYCOAI_HOME=C:\your\path\to\taxotagger-webapp\data
        ```

    Set the environment variable `MYCOAI_HOME` to the path of the `data` directory of your local webapp repository.
    The [`data` directory](https://github.com/MycoAI/taxotagger-webapp/tree/main/data) contains the example vector databases for demo purposes.


2. Start the webapp

    ```bash
    streamlit run app.py # (1)!
    ```

    1. Make sure you are in the `taxotagger-webapp` directory and the right conda environment is activated.

    Then you can open the webapp in your browser by visiting the URL http://localhost:8501.


    !!! Note
        For the first time running, the webapp will download the embedding model files. This may take a few minutes depending on the internet connection speed.

## Production deployment

The vector databases provided in the [`data` directory](https://github.com/MycoAI/taxotagger-webapp/tree/main/data) are for demo purposes only. 
To use the webapp in production, you should prepare the vector databases using the production data. 
To build the vector database, you can follow the instructions in the [Build a vector database][build-a-vector-database] page.