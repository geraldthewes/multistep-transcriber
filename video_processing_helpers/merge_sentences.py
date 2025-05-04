import spacy
from typing import List, Dict

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
    last_end_time = 0.0
    
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
            start_time = segments[start_segment_idx]["start"] 
            if  start_time < last_end_time:
                # Ensure previous segment ends before current sgements starts
                start_time = (start_time  + last_end_time)/2
                # Fix end time of previous segment
                merged_segments[-1]["end"] = start_time
            merged_segment = {
                "start": start_time,
                "end": segments[end_segment_idx]["end"],
                "transcript": sentence
            }
            merged_segments.append(merged_segment)
            last_end_time = segments[end_segment_idx]["end"]            
        
        current_pos = sentence_end
    
    return merged_segments
