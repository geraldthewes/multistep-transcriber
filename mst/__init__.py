"""
The `mst` package provides a comprehensive suite of tools for generating
high-quality video and audio transcripts. It implements an automated workflow
that leverages Large Language Models (LLMs) and specialized audio processing
libraries to achieve accurate and well-formatted results.

The core process involves several key steps:
1.  **Initial Transcription**: Generating a raw transcript from the media file.
2.  **Noun and Entity Extraction**: Identifying important terms and proper nouns
    to improve accuracy.
3.  **Transcript Correction**: Refining the raw transcript using the extracted
    entities and LLMs.
4.  **Speaker Diarization**: Identifying and labeling different speakers in
    the audio.
5.  **Topic Segmentation**: Dividing the transcript into logical topic segments
    and generating headlines/summaries.
6.  **Formatting**: Producing final outputs in various formats, such as
    Markdown, including speaker labels and timestamps.

This package aims to provide a flexible, cost-effective, and controllable
solution for transcription tasks, allowing for customization and continuous
improvement.
"""

__version__ = "0.1.0"  # Keep this in sync with the version in pyproject.toml

# Expose key components for easier import by users of the package
from .video_transcriber import VideoTranscriber

# You can also expose other core functions/classes from submodules if desired, for example:
# from .steps.transcription import initial_transcription
# from .steps.diarization import identify_speakers
# from .steps.topic_segmentation import segment_topics
# from .steps.format import format_markdown
