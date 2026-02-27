import json
import logging
import traceback
from typing import List, Dict, Any, Optional
from faster_whisper import WhisperModel


from .caching import cached_file, cached_file_object
from ..config import TranscriptionConfig

"""
Performs transcription of audio to raw text using Whisper model.
"""

_whisper_models: Dict[str, WhisperModel] = {}


def get_whisper_model(model_name: str = "distil-large-v3") -> WhisperModel:
    """
    Gets or initializes the Whisper model for the given model name.

    Args:
        model_name: Name of the Whisper model to load.

    Returns:
        WhisperModel: The initialized Whisper model instance.
    """
    if model_name not in _whisper_models:
        model = WhisperModel(model_name)
        model.logger.setLevel(logging.WARNING)
        _whisper_models[model_name] = model
    return _whisper_models[model_name]


@cached_file_object('.raw_transcript')
def initial_transcription(
    video_path: str, config: Optional[TranscriptionConfig] = None
) -> List[Dict[str, Any]]:
    """
    Perform initial transcription using Whisper.

    This function transcribes audio/video files using the Whisper speech-to-text model.
    It handles overlapping segments by extending end times to prevent gaps.

    Args:
        video_path (str): Path to the video or audio file to transcribe.

    Returns:
        List[Dict[str, Any]]: A list of transcript segments, each with:
            - start (float): Start time in seconds
            - end (float): End time in seconds
            - transcript (str): Transcribed text

    Raises:
        Exception: If transcription fails for any reason.
    """
    if config is None:
        config = TranscriptionConfig()
    try:
        whisper_model = get_whisper_model(config.whisper_model)

        segments, info = whisper_model.transcribe(video_path)
        output_lines = []
        current_start = None
        curr_end = None
        current_text = None

        for segment in segments:
            if current_text is None or segment.text != current_text:
                # If it's the first segment or the text has changed, add the previous range to output_lines
                if current_text is not None:
                    # Emit previous transcript
                    output_lines.append({
                        "start": current_start,
                        "end": current_end,
                        "transcript": current_text.strip()
                        })

                # Start a new range
                current_start = segment.start
                current_end = segment.end
                current_text = segment.text
            else:
                # If the text is the same, extend the end time of the current range
                current_end = segment.end

        # Add the last range to output_lines
        if current_text is not None:
            output_lines.append({
                "start": current_start,
                "end": current_end,
                "transcript": current_text
            })
        return output_lines
    except Exception as e:
        print(f"Error in initial transcription: {e}")
        return None
