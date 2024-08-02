MyCoAI-based Siamese Network for predicting the taxonomy label of fungi DNA sequence.

## Installation
```bash
# create an virtual environment
conda create -n dnabarcode python=3.9
conda activate dnabarcode

# install the required packages
pip install -r requirements.txt
```

## Usage
```bash
python snn.py --help
```

## Example

```bash
# Predict the similarity between two DNA sequences
python snn.py --dna1 data/dna1.fasta --dna2 data/dna2.fasta
```
