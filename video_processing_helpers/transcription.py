import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any
from faster_whisper import WhisperModel


from .caching import cached_file, cached_file_object

# Approximate conversion factor (1 word ≈ 1.34 tokens) - Moved from ingestion.py
WORDS_TO_TOKENS_RATIO = 1.34

whisper_model = None

@cached_file_object('.raw_transcript')
def initial_transcription(video_path: str) -> str:
    """Perform initial transcription using Whisper"""
    try:
        # lazy Loading
        if not whisper_model:
            whisper_model = WhisperModel("/mnt/data3/AI/software/VideoRAG/faster-distil-whisper-large-v3")
            whisper_model.logger.setLevel(logging.WARNING)

        segments, info = self.whisper_model.transcribe(video_path)
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
                        "transcript": current_text
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
