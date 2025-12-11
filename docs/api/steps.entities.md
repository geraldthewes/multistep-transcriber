<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/entities.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `steps.entities`



## Table of Contents
- [`extract_entities`](./steps.entities.md#function-extract_entities)
- [`extract_persons`](./steps.entities.md#function-extract_persons)
- [`get_entity_model`](./steps.entities.md#function-get_entity_model)
- [`group_by_label`](./steps.entities.md#function-group_by_label)
- [`merge_duplicate_texts`](./steps.entities.md#function-merge_duplicate_texts)
- [`merge_similar_texts`](./steps.entities.md#function-merge_similar_texts)


**Global Variables**
---------------
- **SIMILAR_NAMES_MODEL**
- **batch_size**
- **threshold**

---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/entities.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_entity_model`

```python
get_entity_model()
```

Gets or initializes the GLiNER entity model.


**Returns:**

- <b>`GLiNER`</b>: The initialized GLiNER model instance.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/entities.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `group_by_label`

```python
group_by_label(
    data: List[List[Dict[str, Any]]]
) → Dict[str, List[Dict[str, Any]]]
```

Groups extracted entities by their labels.


**Args:**

- <b>`data`</b> (List[List[Dict[str, Any]]]): Raw entity extraction data.


**Returns:**

- <b>`Dict[str, List[Dict[str, Any]]]`</b>: Entities grouped by label.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/entities.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `merge_duplicate_texts`

```python
merge_duplicate_texts(
    data: Dict[str, List[Dict[str, Any]]]
) → Dict[str, List[Dict[str, Any]]]
```

Merges duplicate entity texts, keeping the one with the highest score.


**Args:**

- <b>`data`</b> (Dict[str, List[Dict[str, Any]]]): Entities grouped by label.


**Returns:**

- <b>`Dict[str, List[Dict[str, Any]]]`</b>: Merged entities with duplicates removed.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/entities.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `merge_similar_texts`

```python
merge_similar_texts(
    data: Dict[str, List[Dict[str, Any]]]
) → Dict[str, List[Dict[str, Any]]]
```

Merges similar entity texts using AI to select canonical spellings.


**Args:**

- <b>`data`</b> (Dict[str, List[Dict[str, Any]]]): Entities grouped by label.


**Returns:**

- <b>`Dict[str, List[Dict[str, Any]]]`</b>: Entities with similar texts merged.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/entities.py#L146"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `extract_entities`

```python
extract_entities(labels: list, transcript: list, batch_size: int = 100) → list
```

Extract proper nouns and technical terms from the transcript in batches
to avoid memory issues with large transcripts.


**Args:**

- <b>`labels`</b> (list): List of entity labels to predict (e.g., ['PERSON', 'ORG', 'TECH TERM']).
- <b>`transcript`</b> (list): A list of dictionaries, where each dict is expected to have
                   a 'transcript' key containing a sentence or segment of text.
- <b>`batch_size`</b> (int): The maximum number of sentences to process in each batch.
                  Defaults to 100.
                  

**Returns:**

- <b>`list`</b>: A list containing the extracted entities from all batches,
      or None if a critical error occurs during initialization or processing.
      Returns an empty list if the transcript is empty.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/entities.py#L265"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `extract_persons`

```python
extract_persons(introductions: str) → list
```

Extracts person names from introductions.


**Args:**

- <b>`introductions`</b> (str): Introduction segments to extract persons from.


**Returns:**

- <b>`list`</b>: List of persons found in the introductions.



