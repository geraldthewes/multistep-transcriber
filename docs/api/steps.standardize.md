<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/standardize.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `steps.standardize`



## Table of Contents
- [`get_noun_correction_model`](./steps.standardize.md#function-get_noun_correction_model)
- [`standardize_nouns_ai`](./steps.standardize.md#function-standardize_nouns_ai)



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/standardize.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_noun_correction_model`

```python
get_noun_correction_model()
```

Gets or initializes the sentence transformer model for noun standardization.


**Returns:**

- <b>`SentenceTransformer`</b>: The initialized sentence transformer model.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/standardize.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `standardize_nouns_ai`

```python
standardize_nouns_ai(transcript: list, noun_list: list)
```

Standardizes nouns using AI-based phonetic similarity via embeddings, preserving line feeds.


**Args:**

- <b>`transcript`</b> (list): List of transcript segments with start, end, and transcript fields.
- <b>`noun_list`</b> (list): List of standard noun spellings.


**Returns:**

- <b>`list`</b>: Standardized transcript segments with line feeds preserved.



