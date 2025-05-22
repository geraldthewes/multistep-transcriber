from .video_transcriber import VideoTranscriber
"""
MultiStep Transcriber package.
A multi-step, automated workflow for generating high-quality video/audio transcripts
using LLMs and other AI models.
"""

__version__ = "0.1.0"  # Keep this in sync with the version in pyproject.toml

# Expose key components for easier import by users of the package
from .video_transcriber import VideoTranscriber

# You can also expose other core functions/classes from submodules if desired, for example:
# from .steps.transcription import initial_transcription
# from .steps.diarization import identify_speakers
# from .steps.topic_segmentation import segment_topics
# from .steps.format import format_markdown
