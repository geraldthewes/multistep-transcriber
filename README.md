## Introduction

A video/audio transcript service implementating the algorithm described on this thread:

https://www.reddit.com/r/LocalLLaMA/comments/1g2vhy3/creating_very_highquality_transcripts_with/

## The algorithm

Transcription is performed by a series of transformation steps. Details are available in the [Planning](documentation/Planning.md) document.


### Why This Approach is Superior
Complete Control: By owning the stack, we can customize every step of the process.

Flexibility: We can easily add features like highlighting mentioned books or papers in transcript.

Cost-Effective: After initial setup, running costs are minimal -> Basically GPU hosting or electricity cost.

Continuous Improvement: We can fine-tune models on our specific content for better accuracy over time.

### Limitations

This packages currently only handles wav files, so if you have a video, you must extract the audio track and save it in a wav file.

### Dependencies

This package depends on an external ollama server with some models, and will download some models from Hugging Face. The system is expected to have a GPU for better performance.
Install ollama follwoing documentation on the [olama web site](https://ollama.com/)

**Hugging Face Token Required**: You need a Hugging Face token with read access to download the models. Set the `HF_TOKEN` environment variable:
```bash
export HF_TOKEN=your_hugging_face_token_here
```

## Installation

### Install package

```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
pip install https://github.com/geraldthewes/topic-treeseg 
pip install .
```

### Serve documentation

```
 mkdocs serve -a 0.0.0.0:8000
```

## Usage

Please consult the documentation on how to use the package. For a simple overview read the [introduction](documentation/index.md)

## Unit Tests

Unit tests can be run as follows

```
python -m unittest test_transcriber.py
python -m unittest mst/steps/tests/test_helpers.py
```
