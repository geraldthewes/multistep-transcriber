import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any
from gliner import GLiNER

from .caching import cached_file, cached_file_object

_entity_model = None

def get_entity_model():
    global _entity_model
    if _entity_model is None:
        _entity_model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
    return _entity_model

''' Extract what we need from results '''
def group_by_label(data: List[List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    # Initialize an empty dictionary to hold the results
    result = {}

    # Iterate through each item in the list
    for sentence in data:
        for entry in sentence:
            # Check if the entry is a dictionary (to skip empty lists)
            if isinstance(entry, dict):
                label = entry['label']

                # Create a new dictionary with only 'text' and 'score'
                text_score_dict = {'text': entry['text'], 'score': entry['score']}

                # Add to the result dictionary under the appropriate label
                if label not in result:
                    result[label] = []
                result[label].append(text_score_dict)

    return result

def flatten_texts(input_dict: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    ''' Just return the nouns '''
    texts = []
    for label in input_dict:
        for item in input_dict[label]:
            texts.append(item['text'])
    return texts

''' Merge entities, pick highest prob'''
def merge_similar_texts(data: Dict[str, List[Dict[str, Any]]]) -> str:
    # Initialize an empty dictionary to hold the results
    result = {}

    # Iterate through each label in the input data
    for label, entries in data.items():
        # Use a dictionary to store unique texts with their maximum scores
        unique_entries = {}

        # Process each entry in the list of entries for the current label
        for entry in entries:
            text = entry['text']
            score = entry['score']

            # remove generic entities
            if text.lower() in ['he','she', 'I', 'me', 'her','him','they', 'we', 'us', 'one']:
                continue
            # If the text is already in the unique_entries, update the score if it's higher
            if text in unique_entries:
                unique_entries[text] = max(unique_entries[text], score)
            else:
                unique_entries[text] = score

        #print(unique_entries)
        # Convert the unique_entries dictionary back to a list of dictionaries
        result[label] = [{'text': text, 'score': score} for text, score in unique_entries.items()]

    # Now flatten the result
    return ','.join(flatten_texts(result))

        
def extract_entities(video_path: str, labels: list, transcript: str) -> list:
    """Extract proper nouns and technical terms from master document"""
    try:
        entity_model = get_entity_model()
        transcript_sentences = [item['transcript'] for item in transcript]            
        # Perform entity prediction
        entities = entity_model.batch_predict_entities(transcript_sentences, labels, threshold=0.5)
        return entities
    except Exception as e:
        print(f"Error extracting nouns: {e}")
        traceback.print_exc()            
        return None

@cached_file('.nouns')
def extract_nouns(video_path: str, transcript: str) -> list:
    labels = ["Person", "Organizations", "Date", "Positions", "Locations"]
    entities =  extract_entities(video_path, labels, transcript)
    entities_by_label = group_by_label(entities)
    entities_merged = merge_similar_texts(entities_by_label)
    return entities_merged

@cached_file_object('.speaker_names')
def extract_persons(ideo_path: str, transcripts: str) -> list:
    labels = ["Person"]
    entities = extract_entities(video_path, labels, transcripts)
    speaker_names=[]
    for introduction in entities:
        name = [item['text'] for item in introduction]
        if name:
            speaker_names.append(name[0])
    speakers = [transcript | {'speaker_name': name} for transcript, name in zip(transcripts, speaker_names)]
    return speakers
