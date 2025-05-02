import spacy
from typing import List, Dict
import argparse
import json

def merge_transcript_segments(segments: List[Dict[str, float]]) -> List[Dict[str, float]]:
    """
    Merge transcript segments into full sentences using spaCy for sentence tokenization.
    
    Args:
        segments: List of dictionaries containing 'start', 'end', and 'transcript' keys.
        
    Returns:
        List of dictionaries with merged segments containing full sentences and corresponding timestamps.
    """
    # Load spaCy model and add sentencizer
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("sentencizer")
    
    # Step 1: Concatenate all transcript texts
    full_text = "".join(segment["transcript"] for segment in segments)
    
    # Step 2: Tokenize into sentences
    doc = nlp(full_text)
    sentences = [sent.text.strip() for sent in doc.sents]
    
    # Step 3: Compute cumulative character lengths for mapping
    cumulative_lengths = []
    current_length = 0
    for segment in segments:
        cumulative_lengths.append(current_length)
        current_length += len(segment["transcript"])
    cumulative_lengths.append(current_length)  # Add final length for end boundary
    
    # Step 4: Map sentences to segments and assign timestamps
    merged_segments = []
    current_pos = 0
    
    for sentence in sentences:
        sentence_start = current_pos
        sentence_end = sentence_start + len(sentence)
        
        # Find start and end segments
        start_segment_idx = None
        end_segment_idx = None
        
        for i in range(len(cumulative_lengths) - 1):
            if cumulative_lengths[i] <= sentence_start < cumulative_lengths[i + 1]:
                start_segment_idx = i
            if cumulative_lengths[i] < sentence_end <= cumulative_lengths[i + 1]:
                end_segment_idx = i
        
        # Handle edge case where sentence spans multiple segments
        if start_segment_idx is not None and end_segment_idx is not None:
            merged_segment = {
                "start": segments[start_segment_idx]["start"],
                "end": segments[end_segment_idx]["end"],
                "transcript": sentence
            }
            merged_segments.append(merged_segment)
        
        current_pos = sentence_end
    
    return merged_segments

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge transcript segments into full sentences.")
    parser.add_argument("input_file", type=str, help="Path to the input JSON file containing segments.")
    parser.add_argument("output_file", type=str, help="Path to the output JSON file for merged segments.")
    
    args = parser.parse_args()
    
    # Read segments from input file
    with open(args.input_file, 'r') as f:
        segments = json.load(f)
    
    # Merge transcript segments
    merged_segments = merge_transcript_segments(segments)
    
    # Write merged segments to output file
    with open(args.output_file, 'w') as f:
        json.dump(merged_segments, f, indent=4)
