import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any
from faster_whisper import WhisperModel


from .caching import cached_file, cached_file_object

''' Performs transcription of audio to raw text '''

_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperModel("/mnt/data3/AI/software/VideoRAG/faster-distil-whisper-large-v3")
        _whisper_model.logger.setLevel(logging.WARNING)
        
    return _whisper_model

@cached_file_object('.raw_transcript')
def initial_transcription(video_path: str) -> str:
    """Perform initial transcription using Whisper"""
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
