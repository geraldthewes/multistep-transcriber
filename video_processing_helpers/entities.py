import os
import json
import torch
import logging
import traceback
import math
from typing import List, Dict, Any
from gliner import GLiNER

from ollama import chat
from pydantic import BaseModel

from .caching import cached_file, cached_file_object
from .models import NounList


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



''' Merge entities, pick highest prob'''
def merge_duplicate_texts(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
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
            if text.lower() in ['he','she', 'i', 'me', 'her','him','they', 'we', 'us', 'one', 'you', 'somebody'
                                'today', 'tonight', 'this year', 'last month', 'last year', 'yesterday', 'tomorrow']:
                continue
            # If the text is already in the unique_entries, update the score if it's higher
            if text in unique_entries:
                unique_entries[text] = max(unique_entries[text], score)
            else:
                unique_entries[text] = score

        #print(unique_entries)
        # Convert the unique_entries dictionary back to a list of dictionaries
        result[label] = [{'text': text, 'score': score} for text, score in unique_entries.items()]

    return result


SIMILAR_NAMES_MODEL = "gemma3:27b"

''' Merge entities, pick highest prob'''
def merge_similar_texts(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]: 
    # Initialize an empty dictionary to hold the results
    result = {}

    prompt =  f'''You are a talented copy editor. I have this list below of person names from a transcript, some names might be the same person with different spelling. I need you to reduce the list, arranged alphabetically that select the most appropriate unique spelling for each person name in the original list. '''
    


    # Iterate through each label in the input data
    for label, entries in data.items():
        print(label)
        # Process each entry in the list of entries for the current label
        entities = "\n- ".join(entity["text"] for entity in entries)
        print(entities)

        response = chat(model=SIMILAR_NAMES_MODEL,
                        messages=[{'role':'user', 'content':prompt + entities}],
                        format=NounList.model_json_schema())

        print(response.message.content)
        reduced_entrities = NounList.model_validate_json(response.message.content)
        print(reduced_entrities)


# def extract_entities_simple(video_path: str, labels: list, transcript: str) -> list:
#     """Extract proper nouns and technical terms from master document"""
#     try:
#         entity_model = get_entity_model()
#         transcript_sentences = [item['transcript'] for item in transcript]            
#         # Perform entity prediction
#         entities = entity_model.batch_predict_entities(transcript_sentences, labels, threshold=0.5)
#         return entities
#     except Exception as e:
#         print(f"Error extracting nouns: {e}")
#         traceback.print_exc()            
#         return None

# batch the requests to avoid memory issues
batch_size =  500
threshold = 0.65

def extract_entities(video_path: str, labels: list, transcript: list, batch_size: int = 100) -> list or None:
    """
    Extract proper nouns and technical terms from the transcript in batches
    to avoid memory issues with large transcripts.

    Args:
        video_path (str): Path to the video file (potentially used for logging or context).
        labels (list): List of entity labels to predict (e.g., ['PERSON', 'ORG', 'TECH TERM']).
        transcript (list): A list of dictionaries, where each dict is expected to have
                           a 'transcript' key containing a sentence or segment of text.
        batch_size (int): The maximum number of sentences to process in each batch.
                          Defaults to 100.

    Returns:
        list: A list containing the extracted entities from all batches,
              or None if a critical error occurs during initialization or processing.
              Returns an empty list if the transcript is empty.
    """
    if not transcript:
        print("Warning: Empty transcript provided.")
        return [] # Return an empty list if there's nothing to process

    try:
        print("Initializing entity model...")
        entity_model = get_entity_model()
        print("Entity model initialized.")

        # Prepare the list of sentences first
        transcript_sentences = [item['transcript'] for item in transcript if item.get('transcript')] # Ensure 'transcript' key exists and is not empty/None
        total_sentences = len(transcript_sentences)

        if total_sentences == 0:
            print("Warning: No valid sentences found in the transcript.")
            return []

        print(f"Total sentences to process: {total_sentences}")
        print(f"Processing in batches of size {batch_size}...")

        all_entities = []
        num_batches = math.ceil(total_sentences / batch_size) # Calculate total number of batches

        # Process in batches
        for i in range(0, total_sentences, batch_size):
            start_index = i
            # Ensure end_index doesn't exceed the list bounds
            end_index = min(i + batch_size, total_sentences)
            # Get the current batch of sentences
            current_batch_sentences = transcript_sentences[start_index:end_index]

            current_batch_num = (i // batch_size) + 1
            print(f"  Processing batch {current_batch_num}/{num_batches} (sentences {start_index+1}-{end_index})...")

            if not current_batch_sentences:
                # This shouldn't happen with the loop logic, but as a safeguard
                print(f"  Skipping empty batch {current_batch_num}.")
                continue

            try:
                # Perform entity prediction on the current batch
                batch_entities = entity_model.batch_predict_entities(
                    current_batch_sentences, labels, threshold=threshold
                )

                # Aggregate results - IMPORTANT ASSUMPTION:
                # Assuming batch_predict_entities returns a list of entities found within that batch.
                # If it returns None on error or empty, handle appropriately.
                if batch_entities:
                    # You might need to adjust entity indices if they are relative to the batch
                    # This example assumes the returned entities don't need index adjustments
                    # or that such adjustments are handled within batch_predict_entities or not needed.
                    all_entities.extend(batch_entities)
                elif batch_entities is None:
                     print(f"Warning: Batch {current_batch_num} prediction returned None.")
                # else: batch_entities is likely [], which is fine (no entities found in batch)


            except Exception as batch_e:
                # Handle errors specific to processing a single batch
                print(f"Error processing batch {current_batch_num} (sentences {start_index+1}-{end_index}): {batch_e}")
                traceback.print_exc()
                # Decide strategy: continue with next batch, or abort all?
                # For now, let's continue, logging the error for the specific batch.
                # If you need to stop entirely on any batch error, uncomment the following line:
                # raise batch_e # Re-raise the exception to be caught by the outer try-except

        print(f"Finished processing all batches. Total entities found: {len(all_entities)}")
        return all_entities

    except Exception as e:
        # Catch errors during model loading or other setup outside the loop
        print(f"Critical error during entity extraction setup or loop initiation: {e}")
        traceback.print_exc()
        return None # Return None on critical failure
    
@cached_file_object('.nouns')
def extract_nouns(video_path: str, transcript: str) -> list:
    labels = ["Person", "Organizations", "Date", "Positions", "Locations"]
    print('Extract Entities')
    entities =  extract_entities(video_path, labels, transcript)
    print('Group Entities')
    entities_by_label = group_by_label(entities)
    print('Merge Entities')
    entities_merged = merge_duplicate_texts(entities_by_label)
    print('Reduce Entities')
    entities_cannonical = merge_similar_texts(entities_merged)    
    return entities_merged

@cached_file_object('.speaker_names')
def extract_persons(video_path: str, transcripts: str) -> list:
    labels = ["Person"]
    if not transcripts:
        return []
    entities = extract_entities(video_path, labels, transcripts)
    speaker_names=[]
    for introduction in entities:
        name = [item['text'] for item in introduction]
        if name:
            speaker_names.append(name[0])
    speakers = [transcript | {'speaker_name': name} for transcript, name in zip(transcripts, speaker_names)]
    return speakers
