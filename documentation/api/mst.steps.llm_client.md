<!-- markdownlint-disable -->

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `mst.steps.llm_client`



## Table of Contents
- [`LLMClient`](./mst.steps.llm_client.md#class-llmclient)
	- [`chat`](./mst.steps.llm_client.md#method-chat)
	- [`parse`](./mst.steps.llm_client.md#method-parse)
- [`OllamaClient`](./mst.steps.llm_client.md#class-ollamaclient)
	- [`chat`](./mst.steps.llm_client.md#method-chat)
	- [`parse`](./mst.steps.llm_client.md#method-parse)
- [`OpenAIClient`](./mst.steps.llm_client.md#class-openaiclient)
	- [`__init__`](./mst.steps.llm_client.md#constructor-__init__)
	- [`chat`](./mst.steps.llm_client.md#method-chat)
	- [`parse`](./mst.steps.llm_client.md#method-parse)
- [`get_llm_client`](./mst.steps.llm_client.md#function-get_llm_client)



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_llm_client`

```python
get_llm_client(config: Optional[LLMConfig] = None) → LLMClient
```

Factory function to get the appropriate LLM client based on config.


**Args:**

- <b>`config`</b>: LLMConfig instance. If None, uses default LLMConfig values.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `LLMClient`






---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `chat`

```python
chat(model: str, messages: list[dict], **kwargs) → str
```

Send a chat request and return the response content.


---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `parse`

```python
parse(model: str, messages: list[dict], response_model: Type[~T], **kwargs) → ~T
```

Send a chat request and return a validated Pydantic model instance.



---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `OllamaClient`






---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `chat`

```python
chat(model: str, messages: list[dict], **kwargs) → str
```




---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L29"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `parse`

```python
parse(model: str, messages: list[dict], response_model: Type[~T], **kwargs) → ~T
```





---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `OpenAIClient`



<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>constructor</kbd> `__init__`

```python
OpenAIClient(base_url: str, api_key: str)
```







---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `chat`

```python
chat(model: str, messages: list[dict], **kwargs) → str
```




---

<a href="https://github.com/geraldthewes/multistep-transcriber/blob/main/mst/steps/llm_client.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `parse`

```python
parse(model: str, messages: list[dict], response_model: Type[~T], **kwargs) → ~T
```





