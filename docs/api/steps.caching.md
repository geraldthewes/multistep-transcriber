<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/caching.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `steps.caching`



## Table of Contents
- [`cached_file`](./steps.caching.md#function-cached_file)
- [`cached_file_object`](./steps.caching.md#function-cached_file_object)
- [`clear_cache_directory`](./steps.caching.md#function-clear_cache_directory)
- [`get_cache_directory`](./steps.caching.md#function-get_cache_directory)
- [`get_cache_file`](./steps.caching.md#function-get_cache_file)
- [`load_object_file`](./steps.caching.md#function-load_object_file)
- [`load_text_file`](./steps.caching.md#function-load_text_file)



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/caching.py#L5"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_cache_directory`

```python
get_cache_directory(video_path)
```





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/caching.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_cache_file`

```python
get_cache_file(video_path, file_ext)
```





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/caching.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `clear_cache_directory`

```python
clear_cache_directory(video_path: str)
```

Clears all files from the cache directory associated with the video_path.
The directory itself will remain.


**Args:**

- <b>`video_path`</b> (str): The path to the video file, used to determine the cache directory.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/caching.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `load_text_file`

```python
load_text_file(cache_file: str)
```





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/caching.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `cached_file`

```python
cached_file(file_ext)
```

A decorator that caches the output of a function to a file.


**Args:**

- <b>`file_ext`</b> (str): The file extension used for the cache file.


**Returns:**

- <b>`function`</b>: A decorator that applies the caching behavior.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/caching.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `load_object_file`

```python
load_object_file(cache_file: str)
```





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/caching.py#L97"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `cached_file_object`

```python
cached_file_object(file_ext)
```

A decorator that caches the output of a function returning a JSON-serializable object to a file.

**Args:**

- <b>`file_ext`</b> (str): The file extension used for the cache file.

**Returns:**

- <b>`function`</b>: A decorator that applies the caching behavior.



