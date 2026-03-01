<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `config`
Centralized configuration for the multistep-transcriber package.

All model names, thresholds, and environment-driven settings are defined here.
Use TranscriberConfig.from_env() to construct a config that reads the same
environment variables as the previous per-module defaults.


## Table of Contents
- [`DiarizationConfig`](./config.md#class-diarizationconfig)
- [`EntityConfig`](./config.md#class-entityconfig)
- [`IntroductionsConfig`](./config.md#class-introductionsconfig)
- [`LLMConfig`](./config.md#class-llmconfig)
- [`MergeSentencesConfig`](./config.md#class-mergesentencesconfig)
- [`StandardizeConfig`](./config.md#class-standardizeconfig)
- [`TopicConfig`](./config.md#class-topicconfig)
- [`TranscriberConfig`](./config.md#class-transcriberconfig)
	- [`from_env`](./config.md#classmethod-from_env)
- [`TranscriptionConfig`](./config.md#class-transcriptionconfig)




---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `LLMConfig`
Configuration for the LLM client.



---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation.


**Returns:**

    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.


---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance.


**Returns:**

    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `TranscriptionConfig`
Configuration for the Whisper transcription step.



---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation.


**Returns:**

    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.


---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance.


**Returns:**

    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L29"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `MergeSentencesConfig`
Configuration for the sentence-merging step.



---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation.


**Returns:**

    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.


---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance.


**Returns:**

    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `EntityConfig`
Configuration for the entity-extraction step.



---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation.


**Returns:**

    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.


---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance.


**Returns:**

    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `StandardizeConfig`
Configuration for the transcript-standardization step.



---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation.


**Returns:**

    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.


---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance.


**Returns:**

    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `DiarizationConfig`
Configuration for the speaker-diarization step.



---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation.


**Returns:**

    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.


---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance.


**Returns:**

    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `IntroductionsConfig`
Configuration for the speaker-introduction detection and mapping steps.



---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation.


**Returns:**

    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.


---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance.


**Returns:**

    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `TopicConfig`
Configuration for the topic-segmentation step.



---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation.


**Returns:**

    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.


---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance.


**Returns:**

    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `TranscriberConfig`
Top-level configuration for the VideoTranscriber pipeline.



---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation.


**Returns:**

    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.


---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance.


**Returns:**

    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.




---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/config.py#L95"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>classmethod</kbd> `from_env`

```python
from_env() → TranscriberConfig
```

Build a TranscriberConfig by reading the environment variables that were
previously consumed at module level in the individual step files.

Environment variables read:
  - LLM_PROVIDER       (default: "openai")
  - OPENAI_BASE_URL    (default: "http://glm-flash.cluster:9999/v1")
  - OPENAI_API_KEY     (default: "not-needed")
  - HF_TOKEN           (default: None)
  - SIMILAR_NAMES_MODEL (default: "glm-4.7-flash")
  - TOPIC_MODEL        (default: "glm-4.7-flash")



