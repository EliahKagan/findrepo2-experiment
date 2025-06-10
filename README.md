<!-- SPDX-License-Identifier: 0BSD -->

# findrepo2-experiment

<!--
  Repo description:
  Semantic text embedding experiments for a utility like findrepo
-->

These are experiments toward a program like
[`findrepo`](https://github.com/EliahKagan/newrepo-findrepo#using-findrepo),
but using an embedding model like
[text-embedding-ada-002](https://platform.openai.com/docs/guides/embeddings/embedding-models)
(which was [OpenAI’s new general purpose text embedding
model](https://openai.com/blog/new-and-improved-embedding-model/) at the time
these experiments were begun).

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

Or if using `poetry` (with `poetry-plugin-shell` installed):

```sh
cd findrepo2-experiment  # When about to use the software.
poetry shell
```

## Preliminary results

Based on the matches shown in [`notebooks/main.ipynb`](notebooks/main.ipynb),
this *seems* to…

- …not work as well as `findrepo` in the common case when the user’s guess has
  some parts of the name correct. I call this the common case because I usually
  mostly remember what I called repositories.
- …work better than `findrepo` when the user’s guess is semantically related to
  the actual name but shared none, or *very* little, of it. This is as
  expected, since the algorithm `findrepo` uses doesn’t know anything about
  meaning, except insofar as that meaning correlates with shared substrings.

So the tests here should not be directly translated into an improved version of
`findrepo`, *at this time*.

## Next steps

Some of the output in [`notebooks/tokens.ipynb`](notebooks/tokens.ipynb)
suggests that the way the repository names are tokenized may contribute to poor
quality.

It’s unclear if this really matters. Ordinarily I think it it wouldn’t, because
context would fill in the meaning. But when embedding repository names, no
context goes into the embedding computation. So I suspect that when
tokenization splits the name at semantically irrelevant boundaries, *in the
cases that this prevents splitting at semantically relevant ones*, it may
decrease the quality of results from the model.

### Patterns of *possibly* undesirable splitting

Two patterns of interest appear:

#### 1. Hyphens stealing first letters from words

For example, `datarace` is tokenized as `data` `-r` `ace`.

This is the pattern that seems most compelling. Repositories shouldn’t be named
with spaces, but if the name *had* been `data race`, then it would’ve been
tokenized as `data` <code>&nbsp;race</code>.

#### 2. Non-initial camel-case words starting with very short tokens

For example, `FmtSandbox` is tokenized as `Fmt` `S` `andbox`.

This is less common. It happens because there are many words that form single
tokens when preceded by a space, but not by themselves.

### What to do about it

Even beyond those particular issues, it’s intuitive to think that having spaces
between the words would improve the quality of matches.

I emphasize again that I don’t actually know whether the way the pieces of
names are combined ever causes worse matches or, even if it does, whether it
has a tendency to do so. Any purported solution should be compared to the
current approach before being considered an improvement.

With that said, the idea to get more semantic tokenization, which might help
even separately from that, is **to transform the repository names** into
phrases whose words are separated by spaces before computing their embeddings.
This could be done instead of, or alongside, computing embeddings of the
unmodified names:

- Hyphens and underscores would be replaced by spaces. So `data-race` would
  become `data race`.
- Spaces would be inserted between words of camel-case names, so `VidDraw`
  would become `Vid Draw`. This is a bit more complicated than the first
  transformation, it’s necessary to avoid inserting spaces between successive
  letters of capitalized acronyms: `SFINAE` remains `SFINAE`.
- *Possibly*, case folding could be done on non-acronyms, either to sentence
  case (`VidDraw` becoming `Vid draw`) or all lower-case (`VidDraw` becoming
  `vid draw`).
