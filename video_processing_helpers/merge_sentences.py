import spacy
from typing import List, Dict

from .caching import cached_file, cached_file_object

def _concatenate_transcripts(segments: List[Dict[str, any]]) -> str:
    """
    Concatenate all transcript texts.
    """
    return "".join(segment["transcript"] for segment in segments)

def _tokenize_into_sentences(full_text: str, nlp) -> List[str]:
    """
    Tokenize into sentences using a spaCy nlp model.
    """
    doc = nlp(full_text)
    return [sent.text.strip() for sent in doc.sents]

def _compute_cumulative_lengths(segments: List[Dict[str, any]]) -> List[int]:
    """
    Compute cumulative character lengths for mapping.
    """
    cumulative_lengths = []
    current_length = 0
    for segment in segments:
        cumulative_lengths.append(current_length)
        current_length += len(segment["transcript"])
    cumulative_lengths.append(current_length)  # Add final length for end boundary
    return cumulative_lengths

def _map_sentences_to_segments(
    sentences: List[str], 
    segments: List[Dict[str, any]], 
    cumulative_lengths: List[int]
) -> List[Dict[str, any]]:
    """
    Map sentences to segments and assign timestamps.
    """
    merged_segments = []
    current_pos = 0
    last_end_time = 0.0
    
    for sentence in sentences:
        #print(current_pos)
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
        #print(f'start segment={start_segment_idx} end_segment={end_segment_idx}')
        
        # Handle edge case where sentence spans multiple segments
        if start_segment_idx is not None and end_segment_idx is not None:
            start_time = segments[start_segment_idx]["start"]
            #print(f'start_time={start_time} last_end_time={last_end_time}')
            if start_time < last_end_time:
                # Ensure previous segment ends before current segment starts
                # Adjust start_time to be midpoint if overlap, or maintain if sequential
                #print('Adjust time')
                new_start_time = (segments[start_segment_idx]["start"] + last_end_time) / 2
                if merged_segments and new_start_time < merged_segments[-1]["end"]: # ensure it doesn't go before previous end
                     merged_segments[-1]["end"] = new_start_time
                start_time = new_start_time

            merged_segment = {
                "start": start_time,
                "end": segments[end_segment_idx]["end"],
                "transcript": sentence
            }
            merged_segments.append(merged_segment)
            #print(merged_segments)
            last_end_time = segments[end_segment_idx]["end"]            
        
        current_pos = sentence_end
    
    return merged_segments


@cached_file_object('.sentence_merge')
def merge_transcript_segments(video_path:str, segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """
    Merge transcript segments into full sentences using spaCy for sentence tokenization.
    
    Args:
        video_path: Path to the video file (used for caching).
        segments: List of dictionaries containing 'start', 'end', and 'transcript' keys.
        
    Returns:
        List of dictionaries with merged segments containing full sentences and corresponding timestamps.
    """
    if not segments:
        return []

    # Load spaCy model and add sentencizer
    nlp = spacy.load("en_core_web_sm")
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")
    
    # Step 1: Concatenate all transcript texts
    full_text = _concatenate_transcripts(segments)
    #print(full_text)
    
    # Step 2: Tokenize into sentences
    sentences = _tokenize_into_sentences(full_text, nlp)
    #print(sentences)
    
    # Step 3: Compute cumulative character lengths for mapping
    cumulative_lengths = _compute_cumulative_lengths(segments)
    #print(cumulative_lengths)
    
    # Step 4: Map sentences to segments and assign timestamps
    merged_segments = _map_sentences_to_segments(sentences, segments, cumulative_lengths)
    
    return merged_segments
