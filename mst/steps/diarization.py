import torch
import traceback
from typing import Dict, Any, Optional
from pyannote.audio import Pipeline

from .caching import cached_file_object
from ..config import DiarizationConfig

"""
Module for speaker diarization using pyannote.audio.
"""

_diarization_pipelines: Dict[str, Pipeline] = {}


def get_diarization_pipeline(config: Optional[DiarizationConfig] = None) -> Pipeline:
    """
    Gets or initializes the pyannote diarization pipeline for the given model.

    Args:
        config: DiarizationConfig instance. If None, uses defaults.

    Returns:
        Pipeline: The initialized pyannote diarization pipeline.
    """
    if config is None:
        config = DiarizationConfig()
    model_name = config.diarization_model
    if model_name not in _diarization_pipelines:
        pipeline = Pipeline.from_pretrained(
            model_name,
            token=config.hf_token,
        )
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        pipeline.to(device)
        _diarization_pipelines[model_name] = pipeline
    return _diarization_pipelines[model_name]

@cached_file_object('.diarization')
def identify_speakers(
    video_path: str,
    transcript: str,
    config: Optional[DiarizationConfig] = None,
) -> dict:
    """
    Performs speaker diarization and creates a mapping of speaker segments.

    This function identifies different speakers in the audio and creates a mapping
    of speaker segments with their start and end times.

    Args:
        video_path (str): Path to the video or audio file.
        transcript (str): The transcript to use for diarization.

    Returns:
        dict: Dictionary containing speaker segment information.
    """
    try:
        diarization_pipeline = get_diarization_pipeline(config)

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
