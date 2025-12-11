import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any

from .caching import cached_file, cached_file_object

"""
Helper functions for transcript processing and manipulation.
"""

@cached_file_object('.merged')
def merge_transcript_diarization(video_path: str, transcript: list, diarization: list):
    """
    Merges transcript and diarization information into a unified format.

    This function combines transcript segments with speaker diarization information
    to create a unified transcript with speaker labels.

    Args:
        video_path (str): Path to the video file (used for caching).
        transcript (list): List of transcript segments.
        diarization (list): List of speaker diarization segments.

    Returns:
        list: Merged transcript with speaker information.
    """
    # Create a new list to store merged results
    merged = []

    # Sort both arrays by start time just to be safe
    transcript = sorted(transcript, key=lambda x: x["start"])
    diarization = sorted(diarization, key=lambda x: x["start"])

    # Keep track of current position in both arrays
    t_idx = 0  # transcript index
    d_idx = 0  # diarization index

    # Handle case where one or both arrays are empty
    if not transcript or not diarization:
        return transcript if transcript else []

    current_time = min(transcript[0]["start"], diarization[0]["start"])
    max_time = max(
        transcript[-1]["end"] if transcript else 0,
        diarization[-1]["end"] if diarization else 0
    )

    while current_time < max_time and (t_idx < len(transcript) or d_idx < len(diarization)):
        # Get current transcript and diarization segments if available
        curr_trans = transcript[t_idx] if t_idx < len(transcript) else None
        curr_diar = diarization[d_idx] if d_idx < len(diarization) else None

        # Determine the next end time
        next_end = float('inf')
        if curr_trans:
            next_end = min(next_end, curr_trans["end"])
        if curr_diar:
            next_end = min(next_end, curr_diar["end"])

        # If no transcript in this segment, create a silent segment
        if not curr_trans or (curr_diar and curr_diar["end"] < curr_trans["start"]):
            if curr_diar:
                merged.append({
                    "start": current_time,
                    "end": min(next_end, curr_diar["end"]),
                    "transcript": "[SILENCE]",
                    "speaker": curr_diar["speaker"],
                    "duration": min(next_end, curr_diar["end"]) - current_time
                })
            else:
                merged.append({
                    "start": current_time,
                    "end": next_end,
                    "transcript": "[SILENCE]",
                    "speaker": "UNKNOWN",
                    "duration": next_end - current_time
                })
        # If we have a transcript segment
        else:
            speaker = "UNKNOWN"
            # Find overlapping diarization segment
            if curr_diar and curr_diar["start"] <= curr_trans["end"] and curr_diar["end"] >= curr_trans["start"]:
                speaker = curr_diar["speaker"]

            merged.append({
                "start": current_time,
                "end": next_end,
                "transcript": curr_trans["transcript"],
                "speaker": speaker,
                "duration": next_end - current_time,
            })

        # Update indices and current_time
        current_time = next_end

        if curr_trans and next_end >= curr_trans["end"]:
            t_idx += 1
        if curr_diar and next_end >= curr_diar["end"]:
            d_idx += 1

    return merged

@cached_file_object('.compressed')
def compress_transcript(video_path: str, entries: list):
    """
    Compresses repeated sentences in the transcript.

    This function combines consecutive segments with the same speaker and text
    to reduce redundancy in the transcript.

    Args:
        video_path (str): Path to the video file (used for caching).
        entries (list): List of transcript entries.

    Returns:
        list: Compressed transcript with redundant segments removed.
    """
    ''' Compress repreated senstences '''
    if not entries:
        return []

    compressed = []
    current = dict(entries[0])  # Create a copy of the first entry
    duration_max = current['duration']

    for entry in entries[1:]:
        # Check if current entry matches the previous one in transcript and speaker
        if (entry['transcript'] == current['transcript'] and
            entry['start'] == current['end']):  # Check if times are consecutive
            # Update the end time to the current entry's end time
            current['end'] = entry['end']
            current['duration'] = current['duration'] + entry['duration']
            if entry['duration'] > duration_max:
                # Select one corresponding to largest duration
                current['speaker'] = entry['speaker']
                duration_max = entry['duration']
        else:
            # Add the completed entry to our result and start a new one
            current['duration'] = round(current['duration'],2)
            compressed.append(current)
            current = dict(entry)  # Create a copy of the new entry
            duration_max = current['duration']
    # Don't forget to add the last entry
    current['duration'] = round(current['duration'],2)
    compressed.append(current)

    return compressed

@cached_file_object('.final')
def map_speakers(video_path: str, transcripts: list, speaker_to_name: dict):
    """
    Maps speaker IDs to actual names in the transcript.

    Args:
        video_path (str): Path to the video file (used for caching).
        transcripts (list): List of transcript entries.
        speaker_to_name (dict): Mapping of speaker IDs to names.

    Returns:
        list: Transcript with speaker names mapped.
    """
    return  [transcript | {'speaker_name': speaker_to_name.get(transcript['speaker'],transcript['speaker'])} for transcript in transcripts]

def flatten_texts(input_dict: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    """
    Flattens a dictionary of texts into a simple list.

    Args:
        input_dict (Dict[str, List[Dict[str, Any]]]): Dictionary with text entries.

    Returns:
        List[str]: Flat list of text values.
    """
    ''' Just return the nouns '''
    texts = []
    for label in input_dict:
        for item in input_dict[label]:
            texts.append(item['text'])
    return texts

    
