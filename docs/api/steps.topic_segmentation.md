<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/topic_segmentation.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `steps.topic_segmentation`



## Table of Contents
- [`update_transcript_with_topics`](./steps.topic_segmentation.md#function-update_transcript_with_topics)


**Global Variables**
---------------
- **TOPIC_MODEL**
- **EXTENSION_TOPICS**
- **HEADLINE_PROMPT**
- **SUMMARY_PROMPT**

---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/topic_segmentation.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `update_transcript_with_topics`

```python
update_transcript_with_topics(transcript, topic_transitions)
```

Updates transcript entries with topic numbers based on topic transitions.


**Args:**

- <b>`transcript`</b> (list): List of transcript entry dictionaries
- <b>`topic_transitions`</b> (list): List of 0s and 1s indicating topic continuation (0) or new topic (1)


**Returns:**

- <b>`list`</b>: Updated transcript with topic field added to each entry



