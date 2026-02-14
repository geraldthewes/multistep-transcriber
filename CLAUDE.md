# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python package called `multistep-transcriber` that implements an automated, multi-step workflow for generating high-quality video/audio transcripts. The project uses a combination of LLMs and specialized AI models to process audio through several stages: initial transcription, sentence merging, entity extraction, transcript correction, speaker diarization, topic segmentation, and final formatting.

The workflow is inspired by [this Reddit post](https://www.reddit.com/r/LocalLLaMA/comments/1g2vhy3/creating_very_highquality_transcripts_with/) and is designed to produce superior transcripts compared to single-pass approaches.

## Key Dependencies

- **ollama**: Required external server for LLM operations
- **faster-whisper**: Speech-to-text transcription
- **pyannote.audio**: Speaker diarization
- **topic-treeseg**: Topic segmentation (custom dependency)
- **transformers**, **sentence_transformers**: NLP models
- **gliner**, **setfit**: Entity recognition and classification
- **spacy**: Sentence processing
- **torch**: Deep learning framework

## Common Commands

### Installation
```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# Install topic-treeseg dependency
pip install https://github.com/geraldthewes/topic-treeseg 

# Install the package
pip install .
```

### Testing

```bash
# Full test suite + wheel build (recommended)
make test
# or directly:
./test.sh

# Individual test suites
python -m unittest test_transcriber.py
python -m unittest mst/steps/tests/test_helpers.py
```

### Publishing

```bash
# Run tests, build wheel, and upload to private PyPI (http://pypi.cluster:9999/)
make publish

# If authentication is required:
export TWINE_USERNAME=your_username
export TWINE_PASSWORD=your_password
make publish
```

### Documentation

```bash
# Serve documentation locally
mkdocs serve -a 0.0.0.0:8000
```

### Build Targets

| Target | Description |
|---|---|
| `make test` | Run all unit tests and build the wheel |
| `make publish` | Run tests, build wheel, upload to private PyPI |
| `make clean` | Remove `dist/`, `build/`, `*.egg-info/` |
| `make docs` | Generate API docs and build MkDocs site |
| `make docs-serve` | Serve documentation locally on port 8000 |
| `make docs-api` | Generate API documentation with lazydocs |

## Development Environment

This project uses [DevPod](https://devpod.sh/) with a devcontainer for a consistent development environment.

### Getting Started

```bash
# Launch the devcontainer
devpod up multistep-transcriber

# Once inside the container:
make test      # Run tests and build wheel
make publish   # Test, build, and upload to private PyPI
```

### Environment Variables

The devcontainer automatically sets:

| Variable | Value |
|---|---|
| `PYTHONPATH` | Container workspace folder |
| `OLLAMA_HOST` | `http://ollama.cluster:11434` |
| `OPENAI_BASE_URL` | `http://vllm.cluster:8000/v1` |
| `OPENAI_MODEL` | Model served by vLLM |
| `OPENAI_API_KEY` | Set via `remoteEnv` |

Additional secrets (e.g., `TWINE_USERNAME`, `TWINE_PASSWORD`) can be placed in `.vault-secrets` at the project root. This file is sourced automatically on shell startup via `post-setup.sh`.

## Architecture

### Core Components

**Main Entry Point**: `mst.VideoTranscriber` - The primary class that orchestrates the entire transcription pipeline.

**Processing Steps** (in `mst/steps/`):
1. **transcription.py**: Initial audio-to-text conversion using Whisper-based models
2. **merge_sentences.py**: Reassembles transcript chunks into complete sentences using spaCy
3. **entities.py**: Extracts nouns and technical terms using GLiNER and structured LLM responses
4. **standardize.py**: Corrects transcripts using extracted entities and LLMs
5. **diarization.py**: Speaker identification using pyannote.audio
6. **introductions.py**: Maps speaker labels to actual names based on context
7. **topic_segmentation.py**: Breaks transcript into topic segments using TreeSeg
8. **format.py**: Produces final outputs (Markdown, JSON) with speaker labels and timestamps

**Utility Modules**:
- **helpers.py**: Core functions for merging diarization data, compressing transcripts, and mapping speakers
- **models.py**: Model loading and caching utilities
- **caching.py**: File-based caching system for intermediate results

### External Scripts

Located in the project root, these provide standalone functionality:
- **ingestion.py**: Batch processing pipeline
- **topic_segment.py**: Standalone topic segmentation
- **yt-download.py** / **yt-transcript.py**: YouTube content processing utilities
- **merge_transcript_segments.py**: Standalone sentence merging

### Data Flow

The `VideoTranscriber.transcribe_video()` method processes files through this pipeline:

1. Audio file → Initial transcription (JSON chunks with timestamps)
2. Chunks → Merged sentences (maintaining timestamps)
3. Content → Extracted entities (proper nouns, technical terms)
4. Raw transcript + entities → Corrected transcript
5. Audio → Speaker diarization data
6. Transcript + diarization → Speaker-labeled transcript
7. Labeled transcript → Compressed (consecutive same-speaker segments merged)
8. Raw transcript → Speaker introductions detection
9. Introductions → Speaker ID to name mapping
10. Final transcript with actual speaker names

Optional: Topic segmentation creates logical content divisions with headlines and summaries.

## Development Guidelines

Per `documentation/CONVENTIONS.md`:
- Functions should be small, do one thing, and have unit tests
- Use meaningful, intent-revealing names
- Follow functional programming principles (pure functions, immutability, composition, declarative code)
- Keep code simple and self-explanatory
- Handle errors robustly and consider security implications

## External Requirements

- **Ollama server**: Must be running with appropriate models for LLM operations
- **GPU**: Recommended for better performance with audio processing models
- **WAV files**: Currently only supports WAV audio format (video files need audio extraction)

## File Structure Notes

- Package code is in `mst/` directory
- Documentation uses MkDocs with Material theme
- Tests are minimal (only in `test_transcriber.py` and `mst/steps/tests/`)
- Jupyter notebooks (`.ipynb` files) are used for experimentation
- `introductions.json` contains speaker mapping data