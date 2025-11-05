import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any
from pyannote.audio import Pipeline

from .caching import cached_file_object


_diarization_pipeline = None

def get_diarization_pipeline():
    global _diarization_pipeline
    diarization_model = "pyannote/speaker-diarization-3.1"
    if _diarization_pipeline is None:
        _diarization_pipeline = Pipeline.from_pretrained(diarization_model)
        # Check if CUDA is available, otherwise fall back to CPU
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        _diarization_pipeline.to(device)
        
    return _diarization_pipeline

@cached_file_object('.diarization')
def identify_speakers(video_path: str, transcript: str) -> dict:
    """Perform speaker diarization and mapping"""
    try:
        diarization_pipeline = get_diarization_pipeline()

        # Perform diarization
        diarization = diarization_pipeline(video_path)

        # Convert to simple format
        speaker_segments = []
        # The correct way to iterate over tracks in pyannote.audio v4+
        # Try different approaches to handle the API change
        try:
            # Method 1: Direct iteration (most common)
            for turn, speaker in diarization:
                speaker_segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
        except Exception:
            # Method 2: Try with the itertracks method (older approach)
            try:
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    speaker_segments.append({
                        "start": turn.start,
                        "end": turn.end,
                        "speaker": speaker
                    })
            except Exception:
                # Method 3: Try to get speaker_diarization attribute
                try:
                    speaker_diarization = diarization.speaker_diarization
                    for turn, speaker in speaker_diarization:
                        speaker_segments.append({
                            "start": turn.start,
                            "end": turn.end,
                            "speaker": speaker
                        })
                except Exception:
                    # If all methods fail, return empty list
                    raise Exception("Could not iterate over diarization tracks")

        # There are cases of segments withing segments, drop them,
        prev_end = speaker_segments[0]["end"]
        speaker_filter = []
        for segment in speaker_segments[1:]:
            if segment["start"] >= prev_end:
                speaker_filter.append(segment)
            prev_end = max(prev_end, segment["end"])

        return speaker_filter
    except Exception as e:
        print(f"Error in speaker identification: {e}")
        # Return empty dict to maintain consistent return type
        return {}
