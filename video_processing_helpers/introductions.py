import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any
from setfit import SetFitModel

from .caching import cached_file_object
from .entities import extract_persons

@cached_file_object('.introductions')
def find_introductions(video_path: str, transcripts):
    ''' Identify segments that are speaker introductions using a trained setfit model '''
    try:
        intro_sentences = []
        imodel = SetFitModel.from_pretrained("gerald29/setfit-bge-small-v1.5-sst2-8-shot-introduction")         
        sentences = [item['transcript'] for item in transcripts]
        labels = imodel.predict(sentences)
        # Filter the transcripts where the corresponding label is 'introduction'
        filtered_transcripts = [transcript for transcript, label in zip(transcripts, labels) if label == 'introduction']
        return filtered_transcripts
    except Exception as e:
         print(f"Error extracting speaker introductions: {e}")
         return None


def speaker_to_name(introductions: str):
    # Initialize an empty dictionary for the result
    result = {}

    # Iterate over each entry in the list
    for item in introductions:
        speaker_key = item['matched_speaker']
        speaker_value = item['speaker_name']

        # If the speaker is UNKNOWN, set the value to UNKNOWN
        if speaker_key == "UNKNOWN":
            speaker_value = "UNKNOWN"

        # Add the mapping to the result dictionary
        result[speaker_key] = speaker_value
    return result

     
def map_entities_to_speakers(video_path: str, ner_data, diarization_data, margin=0.5):
    """
    Maps entities (especially persons) from NER data to speakers from diarization data
    based on overlapping time intervals, allowing for a specified margin.

    Args:
        ner_data (list): A list of lists, where each inner list contains one entity dictionary.
                         Each entity dictionary should have 'start', 'end', 'text', 'label'.
                         Example: [[{'start': 5, 'end': 17, 'text': 'Doug Lucente', 'label': 'Person'}], ...]
        diarization_data (list): A list of speaker segment dictionaries.
                                 Each dictionary should have 'start', 'end', 'speaker'.
                                 Example: [{'start': 4.0, 'end': 10.0, 'speaker': 'SPEAKER_01'}, ...]
        margin (float): A time margin (in seconds) to allow for slight discrepancies
                        in start/end times. When checking for a match, the speaker's
                        segment is conceptually expanded by this margin.

    Returns:
        list: A list of augmented entity dictionaries. Each dictionary corresponding
              to a processed target_label entity will have two new keys:
              'matched_speaker': The speaker ID if a match is found, else None.
              'overlap_duration': The duration of the actual overlap with the matched speaker.
                                  If no match, this will be 0.
    """
    results = []

    for entity in ner_data:
        # Create a copy to avoid modifying the original input
        processed_entity = entity.copy()

        entity_start = processed_entity['start']
        entity_end = processed_entity['end']

        best_match_speaker = None
        max_overlap_duration = 0.0

        for segment in diarization_data:
            speaker_start = segment['start']
            speaker_end = segment['end']
            speaker_id = segment['speaker']

            # Condition for potential match: entity overlaps with expanded speaker segment
            # Expanded speaker segment: [speaker_start - margin, speaker_end + margin]
            # Overlap condition:
            # max(entity_start, speaker_start - margin) < min(entity_end, speaker_end + margin)

            potential_match_start = speaker_start - margin
            potential_match_end = speaker_end + margin

            if max(entity_start, potential_match_start) < min(entity_end, potential_match_end):
                # This speaker segment is a candidate. Now calculate actual overlap.
                # Actual overlap is between [entity_start, entity_end] and [speaker_start, speaker_end]
                overlap_start = max(entity_start, speaker_start)
                overlap_end = min(entity_end, speaker_end)

                current_overlap_duration = round(max(0, overlap_end - overlap_start),2)

                if current_overlap_duration > max_overlap_duration:
                    max_overlap_duration = current_overlap_duration
                    best_match_speaker = speaker_id

        processed_entity['matched_speaker'] = best_match_speaker
        processed_entity['overlap_duration'] = max_overlap_duration

        results.append(processed_entity)
        
    return results


MARGIN_IN_SECONDS=1.0

@cached_file_object('.speaker_map')
def create_speaker_map(video_path: str, speaker_introductions, speaker_mapping):
        ''' Create mapping betyween person name and diarization. '''
        # first extract name from introductions
        speaker_names = extract_persons(speaker_introductions)
        # Now map name to diarization
        speakers_diarization = map_entities_to_speakers(video_path, speaker_names, speaker_mapping, MARGIN_IN_SECONDS)
        # Now create map of speaker to speaker_name
        speakers = speaker_to_name(speakers_diarization)
        return speakers
