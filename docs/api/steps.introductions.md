<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/introductions.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `steps.introductions`



## Table of Contents
- [`map_entities_to_speakers`](./steps.introductions.md#function-map_entities_to_speakers)
- [`speaker_to_name`](./steps.introductions.md#function-speaker_to_name)


**Global Variables**
---------------
- **MARGIN_IN_SECONDS**

---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/introductions.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `speaker_to_name`

```python
speaker_to_name(introductions: str)
```





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/introductions.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `map_entities_to_speakers`

```python
map_entities_to_speakers(
    video_path: str,
    ner_data,
    diarization_data,
    margin=0.5
)
```

Maps entities (especially persons) from NER data to speakers from diarization data
based on overlapping time intervals, allowing for a specified margin.


**Args:**

- <b>`ner_data`</b> (list): A list of lists, where each inner list contains one entity dictionary.
                 Each entity dictionary should have 'start', 'end', 'text', 'label'.
- <b>`Example: [[{'start': 5, 'end': 17, 'text': 'Doug Lucente', 'label'`</b>: 'Person'}], ...]
- <b>`diarization_data`</b> (list): A list of speaker segment dictionaries.
                         Each dictionary should have 'start', 'end', 'speaker'.
- <b>`Example: [{'start': 4.0, 'end': 10.0, 'speaker'`</b>: 'SPEAKER_01'}, ...]
- <b>`margin`</b> (float): A time margin (in seconds) to allow for slight discrepancies
                in start/end times. When checking for a match, the speaker's
                segment is conceptually expanded by this margin.


**Returns:**

- <b>`list`</b>: A list of augmented entity dictionaries. Each dictionary corresponding
      to a processed target_label entity will have two new keys:
- <b>`'matched_speaker'`</b>: The speaker ID if a match is found, else None.
- <b>`'overlap_duration'`</b>: The duration of the actual overlap with the matched speaker.
                    If no match, this will be 0.



