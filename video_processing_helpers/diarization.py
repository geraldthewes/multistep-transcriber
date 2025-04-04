import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any
from pyannote.audio import Pipeline

from .caching import cached_file, cached_file_object

diarization_model = "pyannote/speaker-diarization-3.1"
diarization_pipeline = None

@cached_file_object('.diarization')
def identify_speakers(video_path: str, transcript: str) -> dict:
    """Perform speaker diarization and mapping"""
    try:
        if not diarization_pipeline:
            diarization_pipeline = Pipeline.from_pretrained(
                diarization_model,
                use_auth_token=os.environ["HF_TOKEN"])
            diarization_pipeline.to(torch.device("cuda"))

        # Perform diarization
        diarization = diarization_pipeline(video_path)

        # Convert to simple format
        speaker_segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })

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
        return {}
