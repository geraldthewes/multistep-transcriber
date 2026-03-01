<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/transcription.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `mst.steps.transcription`



## Table of Contents
- [`get_whisper_model`](./mst.steps.transcription.md#function-get_whisper_model)



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/transcription.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_whisper_model`

```python
get_whisper_model(model_name: str = 'distil-large-v3') → WhisperModel
```

Gets or initializes the Whisper model for the given model name.


**Args:**

- <b>`model_name`</b>: Name of the Whisper model to load.


**Returns:**

- <b>`WhisperModel`</b>: The initialized Whisper model instance.



