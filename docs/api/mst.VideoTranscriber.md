<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/video_transcriber.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>class</kbd> `VideoTranscriber`
A class to handle the end-to-end video transcription process,
including initial transcription, noun extraction, correction,
speaker diarization, topic segmentation, and formatting.

This class orchestrates the complete transcription pipeline, managing
the flow of data between different processing steps.


<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/video_transcriber.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>constructor</kbd> `__init__`

```python
VideoTranscriber(topic_config=None)
```

Initializes the VideoTranscriber.


**Args:**

- <b>`topic_config`</b> (dict, optional): Configuration for topic segmentation.
                               Defaults to None, in which case topic
                               segmentation will be skipped.





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/video_transcriber.py#L183"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>method</kbd> `clear`

```python
clear(video_path: str)
```

Clears all cached files associated with the given video path.


**Args:**

- <b>`video_path`</b> (str): The file path to the video or audio file whose cache should be cleared.


---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/video_transcriber.py#L131"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>method</kbd> `format_transcript`

```python
format_transcript(
    video_path: str,
    transcript: list,
    nouns_list: Dict[str, List[Dict[str, Any]]],
    topic_headlines: list,
    topic_summary: list
) → None
```

Formats the processed transcript into plain text and Markdown.

The formatted outputs are cached to files.


**Args:**

- <b>`video_path`</b> (str): The file path to the video or audio file, used for caching.
- <b>`transcript`</b> (list): The final transcript data.
- <b>`nouns_list`</b> (Dict[str, List[Dict[str, Any]]]): A dictionary of extracted nouns/entities.
- <b>`topic_headlines`</b> (list): A list of topic headlines.
- <b>`topic_summary`</b> (list): A list of topic summaries.


---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/video_transcriber.py#L152"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>method</kbd> `retrieve_json`

```python
retrieve_json(video_path: str) → str | None
```

Retrieves the cached transcript with topic segmentation as a JSON string.

This typically loads the '.topics' cached file.


**Args:**

- <b>`video_path`</b> (str): The file path to the video or audio file, used to locate the cache.


**Returns:**

- <b>`str | None`</b>: The JSON string content of the cached topics file, or None if not found.


---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/video_transcriber.py#L167"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>method</kbd> `retrieve_markdown`

```python
retrieve_markdown(video_path: str) → Any | None
```

Retrieves the cached transcript formatted as Markdown.

This typically loads the '.md' cached file.


**Args:**

- <b>`video_path`</b> (str): The file path to the video or audio file, used to locate the cache.


**Returns:**

- <b>`Any | None`</b>: The content of the cached Markdown file (often a string),
            or None if not found. The return type depends on `load_object_file`.


---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/video_transcriber.py#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>method</kbd> `topics`

```python
topics(video_path: str, transcript: list, max_topics: int) → tuple
```

Segments the transcript into topics and generates headlines and summaries for them.

If `topic_config` was not provided during initialization, this step is skipped.


**Args:**

- <b>`video_path`</b> (str): The file path to the video or audio file, used for caching.
- <b>`transcript`</b> (list): The transcript to be segmented (typically the output of `transcribe_video`).
- <b>`max_topics`</b> (int): The maximum number of topics to segment the transcript into.


**Returns:**

- <b>`tuple`</b>: A tuple containing:
- <b>`- processed_transcript (list)`</b>: The transcript with topic information.
- <b>`- topic_headlines (list)`</b>: A list of generated headlines for each topic.
- <b>`- topic_summary (list)`</b>: A list of generated summaries for each topic.
If topic segmentation is skipped, returns the original transcript and two empty lists.


---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/video_transcriber.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>method</kbd> `transcribe_video`

```python
transcribe_video(video_path: str, transcribe: bool = True) → tuple
```

Processes a video file through the complete transcription pipeline.

The pipeline includes:
1. Initial transcription using a speech-to-text model.
2. Merging transcript segments into sentences.
3. Extracting nouns and important terms.
4. Correcting the transcript using the extracted nouns.
5. Identifying speakers (diarization).
6. Merging diarization information with the transcript.
7. Compressing the transcript by combining consecutive segments from the same speaker.
8. Finding speaker introductions in the raw transcript.
9. Creating a map of speaker IDs to actual names based on introductions.
10. Applying the speaker names to the final transcript.


**Args:**

- <b>`video_path`</b> (str): The file path to the video or audio file.
- <b>`transcribe`</b> (bool): False to skip audio transcription, default True


**Returns:**

- <b>`tuple`</b>: A tuple containing:
- <b>`- transcript_final (list)`</b>: The final processed transcript with speaker information.
- <b>`- nouns_list (list)`</b>: A list of extracted nouns and entities.


