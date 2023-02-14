# findrepo2-experiment

These are experiments toward a program like
[`findrepo`](https://github.com/EliahKagan/newrepo-findrepo#using-findrepo),
but using
[text-embedding-ada-002](https://platform.openai.com/docs/guides/embeddings/embedding-models)
([OpenAI's new general purpose text embedding
model](https://openai.com/blog/new-and-improved-embedding-model/)).

This is in contrast to the custom nonempty-substring frequency vectors
(non-semantic vocabulary-unaware sparse lossless embeddings in an indefinitely
high-dimensional vector space) that `findrepo` uses.

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

The best place to start is [`notebooks/main.ipynb`](notebooks/main.ipynb).
