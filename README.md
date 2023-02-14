<!-- SPDX-License-Identifier: 0BSD -->

# findrepo2-experiment

These are experiments toward a program like
[`findrepo`](https://github.com/EliahKagan/newrepo-findrepo#using-findrepo),
but using
[text-embedding-ada-002](https://platform.openai.com/docs/guides/embeddings/embedding-models)
([OpenAI’s new general purpose text embedding
model](https://openai.com/blog/new-and-improved-embedding-model/)).

This is in contrast to the custom nonempty-substring frequency vectors
(non-semantic vocabulary-unaware sparse lossless embeddings in an indefinitely
high-dimensional vector space) that `findrepo` uses.

Note that the goal of this repository is not to build the alternative. Rather,
these experiments are to figure out of it makes sense to build it, and whether
(and it what ways) it might do a better job than `findrepo`.

## License

[0BSD](https://spdx.org/licenses/0BSD.html). See [**`LICENSE`**](LICENSE).

## Setup

Using `conda`:

```sh
git clone https://github.com/EliahKagan/findrepo2-experiment.git
cd findrepo2-experiment
conda env create
conda activate findrepo2-experiment
conda develop .
```

Or using `poetry`:

```sh
git clone https://github.com/EliahKagan/findrepo2-experiment.git
cd findrepo2-experiment
poetry install
```

## Usage

**The best place to start is [`notebooks/main.ipynb`](notebooks/main.ipynb).**

Make sure to activate the `findrepo2-experiment` environment, or verify that
your editor/IDE has done so. If using `conda`:

```sh
cd findrepo2-experiment  # When about to use the software.
conda activate findrepo2-experiment
```

Or if using `poetry`:

```sh
cd findrepo2-experiment  # When about to use the software.
poetry shell
```
