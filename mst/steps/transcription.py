import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any
from faster_whisper import WhisperModel


from .caching import cached_file, cached_file_object

"""
Performs transcription of audio to raw text using Whisper model.
"""

_whisper_model = None

def get_whisper_model():
    """
    Gets or initializes the Whisper model.

    Returns:
        WhisperModel: The initialized Whisper model instance.
    """
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperModel("distil-large-v3")
        _whisper_model.logger.setLevel(logging.WARNING)

    return _whisper_model

@cached_file_object('.raw_transcript')
def initial_transcription(video_path: str) -> List[Dict[str, Any]]:
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
    try:
        whisper_model = get_whisper_model()

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
