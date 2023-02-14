# findrepo2-experiment

Experiments toward a program like findrepo but using text-embedding-ada-002
(OpenAI's new general purpose text embedding model), instead of the custom
nonempty-substring frequency vectors (non-semantic vocabulary-unaware sparse
lossless embeddings in an indefinitely high-dimensional vector space).

## Setup

Using `conda`:

```sh
git clone https://github.com/EliahKagan/findrepo2-experiment.git
cd findrepo2-experiment
conda env create
conda activate findrepo2-experiment
conda develop .
```

## Usage

The best place to start is `notebooks/main.ipynb`.
