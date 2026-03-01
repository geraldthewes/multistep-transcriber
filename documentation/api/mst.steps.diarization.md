<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/diarization.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `mst.steps.diarization`



## Table of Contents
- [`get_diarization_pipeline`](./mst.steps.diarization.md#function-get_diarization_pipeline)



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/diarization.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_diarization_pipeline`

```python
get_diarization_pipeline(config: Optional[DiarizationConfig] = None) → Pipeline
```

Gets or initializes the pyannote diarization pipeline for the given model.


**Args:**

- <b>`config`</b>: DiarizationConfig instance. If None, uses defaults.


**Returns:**

- <b>`Pipeline`</b>: The initialized pyannote diarization pipeline.



