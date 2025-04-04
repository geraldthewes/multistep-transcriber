import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any
from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer, util

from .caching import cached_file, cached_file_object

noun_correction_model = None

def standardize_nouns_ai(transcript: list, noun_list: list):
    """
    Standardizes nouns using AI-based phonetic similarity via embeddings, preserving line feeds.

    Args:
        transcript (str): Text with phonetic variations and original line breaks
        noun_list (list): Standard noun spellings

    Returns:
        str: Standardized transcript with line breaks preserved
    """
    # Load the model
    if not noun_correction_model:
        noun_correction_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Compute embeddings for standard nouns
    noun_embeddings = noun_correction_model.encode(noun_list, convert_to_tensor=True)

    # Split transcript into lines, preserving line breaks
    output = []

    for row in transcript:
        line = row['transcript']
        if not line.strip():  # Preserve empty lines
            output.append({
                "start": row["start"],
                "end": row["end"],
                "transcript": line})
            continue

        # Split each line into words
        words = line.split()
        standardized_words = []

        for word in words:
            word_lower = word.lower()
            if word_lower in noun_list:  # Exact match
                standardized_words.append(word)
                continue

            # Compute embedding for current word
            word_embedding = noun_correction_model.encode(word_lower, convert_to_tensor=True)

            # Calculate cosine similarity with all standard nouns
            similarities = util.cos_sim(word_embedding, noun_embeddings)[0]
            max_similarity, best_match_idx = similarities.max(), similarities.argmax()

            # If similarity is high enough, replace with standard form
            if max_similarity > 0.85:  # Threshold can be tuned
                standard_form = noun_list[best_match_idx]
                if word[0].isupper():
                    standard_form = standard_form.capitalize()
                standardized_words.append(standard_form)
            else:
                standardized_words.append(word)

        # Reconstruct the line with original spacing between words
        output.append({
                "start": row["start"],
                "end": row["end"],
                "transcript": ' '.join(standardized_words)})

    return output
    
@cached_file_object('.corrected_transcript')        
def correct_transcript(video_path: str, raw_transcript: list, nouns: str) -> str:
    """Correct transcript using LLM and noun list"""
    try:
        nouns_list = nouns.split(',')
        return self.standardize_nouns_ai(raw_transcript, nouns_list)
    except Exception as e:
        print(f"Error correcting transcript: {e}")
        traceback.print_exc()            
        return None
