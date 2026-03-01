<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/standardize.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `mst.steps.standardize`



## Table of Contents
- [`get_noun_correction_model`](./mst.steps.standardize.md#function-get_noun_correction_model)
- [`standardize_nouns_ai`](./mst.steps.standardize.md#function-standardize_nouns_ai)



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/standardize.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_noun_correction_model`

```python
get_noun_correction_model(
    model_name: str = 'paraphrase-MiniLM-L6-v2'
) → SentenceTransformer
```

Gets or initializes the sentence transformer model for noun standardization.


**Args:**

- <b>`model_name`</b>: Name of the SentenceTransformer model to load.


**Returns:**

- <b>`SentenceTransformer`</b>: The initialized sentence transformer model.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/standardize.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `standardize_nouns_ai`

```python
standardize_nouns_ai(
    transcript: list,
    noun_list: list,
    config: Optional[StandardizeConfig] = None
)
```

Standardizes nouns using AI-based phonetic similarity via embeddings, preserving line feeds.


**Args:**

- <b>`transcript`</b> (list): List of transcript segments with start, end, and transcript fields.
- <b>`noun_list`</b> (list): List of standard noun spellings.
- <b>`config`</b>: StandardizeConfig instance. If None, uses defaults.


**Returns:**

- <b>`list`</b>: Standardized transcript segments with line feeds preserved.



