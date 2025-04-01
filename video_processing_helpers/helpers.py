import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any
from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer, util
from pyannote.audio import Pipeline
from gliner import GLiNER
from setfit import SetFitModel

from .caching import cached_file, cached_file_object

# Approximate conversion factor (1 word ≈ 1.34 tokens) - Moved from ingestion.py
WORDS_TO_TOKENS_RATIO = 1.34

# --- Helper Functions (Moved from VideoTranscriber) ---

@cached_file_object('.raw_transcript')
def initial_transcription(video_path: str, whisper_model: WhisperModel) -> List[Dict[str, Any]]:
    """Perform initial transcription using Whisper"""
    try:
        whisper_model.logger.setLevel(logging.WARNING) # Set level here or manage globally
        segments, info = whisper_model.transcribe(video_path)
        output_lines = []
        current_start = None
        curr_end = None
        current_text = None

        for segment in segments:
            if current_text is None or segment.text != current_text:
                if current_text is not None:
                    output_lines.append({
                        "start": current_start,
                        "end": curr_end,
                        "transcript": current_text
                    })
                current_start = segment.start
                current_end = segment.end
                current_text = segment.text
            else:
                current_end = segment.end

        if current_text is not None:
            output_lines.append({
                "start": current_start,
                "end": current_end,
                "transcript": current_text
            })
        return output_lines
    except Exception as e:
        print(f"Error in initial transcription: {e}")
        traceback.print_exc()
        return None

def group_by_label(data: List[List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """ Extract what we need from GLiNER results """
    result = {}
    for sentence in data:
        for entry in sentence:
            if isinstance(entry, dict):
                label = entry['label']
                text_score_dict = {'text': entry['text'], 'score': entry['score']}
                if label not in result:
                    result[label] = []
                result[label].append(text_score_dict)
    return result

def flatten_texts(input_dict: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    """ Just return the text from grouped entities """
    texts = []
    for label in input_dict:
        for item in input_dict[label]:
            texts.append(item['text'])
    return texts

def merge_similar_texts(data: Dict[str, List[Dict[str, Any]]]) -> str:
    """ Merge entities, pick highest probability, remove pronouns, return comma-separated string """
    result = {}
    pronouns = {'he', 'she', 'i', 'me', 'her', 'him', 'they', 'we', 'us', 'one'}

    for label, entries in data.items():
        unique_entries = {}
        for entry in entries:
            text = entry['text']
            score = entry['score']
            if text.lower() in pronouns:
                continue
            if text in unique_entries:
                unique_entries[text] = max(unique_entries[text], score)
            else:
                unique_entries[text] = score
        result[label] = [{'text': text, 'score': score} for text, score in unique_entries.items()]

    return ','.join(flatten_texts(result))

@cached_file('.nouns')
def extract_nouns(video_path: str, transcript: List[Dict[str, Any]], entity_model: GLiNER) -> str:
    """Extracts nouns (Person, Org, Date, Position, Location) using GLiNER."""
    labels = ["Person", "Organizations", "Date", "Positions", "Locations"]
    entities = extract_entities(video_path, labels, transcript, entity_model) # Pass entity_model
    if entities is None:
        return "" # Return empty string on error
    entities_by_label = group_by_label(entities)
    entities_merged = merge_similar_texts(entities_by_label)
    return entities_merged

@cached_file_object('.speaker_names')
def extract_persons(video_path: str, transcripts: List[Dict[str, Any]], entity_model: GLiNER) -> List[Dict[str, Any]]:
    """Extracts Person entities using GLiNER and adds 'speaker_name' key."""
    labels = ["Person"]
    entities = extract_entities(video_path, labels, transcripts, entity_model) # Pass entity_model
    if entities is None:
        return transcripts # Return original transcripts on error

    speaker_names = []
    for introduction in entities:
        # Find the 'Person' entity text if it exists in the list of dicts
        name = next((item['text'] for item in introduction if item['label'] == 'Person'), None)
        speaker_names.append(name if name else "UNKNOWN") # Use UNKNOWN if no name found

    # Ensure speaker_names has the same length as transcripts
    if len(speaker_names) != len(transcripts):
         print(f"Warning: Mismatch between transcript segments ({len(transcripts)}) and extracted names ({len(speaker_names)}). Filling missing names with UNKNOWN.")
         # Pad speaker_names if shorter
         speaker_names.extend(["UNKNOWN"] * (len(transcripts) - len(speaker_names)))
         # Truncate speaker_names if longer (less likely with batch_predict)
         speaker_names = speaker_names[:len(transcripts)]


    speakers = [transcript | {'speaker_name': name} for transcript, name in zip(transcripts, speaker_names)]
    return speakers

# Note: extract_entities is called by extract_nouns and extract_persons,
# so it doesn't need caching itself, but needs the entity_model.
def extract_entities(video_path: str, labels: list, transcript: List[Dict[str, Any]], entity_model: GLiNER) -> List[List[Dict[str, Any]]]:
    """Extract entities using GLiNER model."""
    try:
        transcript_sentences = [item['transcript'] for item in transcript]
        entities = entity_model.batch_predict_entities(transcript_sentences, labels, threshold=0.5)
        return entities
    except Exception as e:
        print(f"Error extracting entities: {e}")
        traceback.print_exc()
        return None

def standardize_nouns_ai(transcript: List[Dict[str, Any]], noun_list: List[str], noun_correction_model: SentenceTransformer) -> List[Dict[str, Any]]:
    """
    Standardizes nouns using AI-based phonetic similarity via embeddings.
    """
    if not noun_list: # Handle empty noun list
        return transcript

    # Compute embeddings for standard nouns
    noun_embeddings = noun_correction_model.encode(noun_list, convert_to_tensor=True)
    output = []

    for row in transcript:
        line = row['transcript']
        if not line or not line.strip(): # Preserve empty/whitespace lines
            output.append(row)
            continue

        words = line.split()
        standardized_words = []

        for word in words:
            word_lower = word.lower()
            # Simple check first for performance
            if word_lower in noun_list:
                # Find the standard form (preserving original case if possible)
                standard_form = next((n for n in noun_list if n.lower() == word_lower), word)
                standardized_words.append(standard_form)
                continue

            # Compute embedding for current word
            try:
                word_embedding = noun_correction_model.encode(word_lower, convert_to_tensor=True)
                # Calculate cosine similarity with all standard nouns
                similarities = util.cos_sim(word_embedding, noun_embeddings)[0]
                max_similarity, best_match_idx = similarities.max(), similarities.argmax()

                # If similarity is high enough, replace with standard form
                if max_similarity > 0.85:  # Threshold can be tuned
                    standard_form = noun_list[best_match_idx]
                    # Try to preserve original capitalization
                    if word.istitle():
                        standard_form = standard_form.title()
                    elif word.isupper():
                         # Check if it's likely an acronym (more than 1 char and all upper)
                         if len(word) > 1 and all(c.isupper() for c in word):
                             standard_form = standard_form.upper() # Keep acronym uppercase
                         else:
                             standard_form = standard_form.capitalize() # Capitalize first letter
                    # else keep standard_form as is (likely lowercase)
                    standardized_words.append(standard_form)
                else:
                    standardized_words.append(word)
            except Exception as e:
                 # Handle potential errors during encoding/similarity calculation for a word
                 print(f"Error processing word '{word}': {e}")
                 standardized_words.append(word) # Keep original word on error


        # Reconstruct the line
        output.append({
            "start": row["start"],
            "end": row["end"],
            "transcript": ' '.join(standardized_words)
        })

    return output

@cached_file_object('.corrected_transcript')
def correct_transcript(video_path: str, raw_transcript: List[Dict[str, Any]], nouns: str, noun_correction_model: SentenceTransformer) -> List[Dict[str, Any]]:
    """Correct transcript using SentenceTransformer and noun list"""
    try:
        nouns_list = [noun.strip() for noun in nouns.split(',') if noun.strip()]
        return standardize_nouns_ai(raw_transcript, nouns_list, noun_correction_model)
    except Exception as e:
        print(f"Error correcting transcript: {e}")
        traceback.print_exc()
        return None

@cached_file_object('.diarization')
def identify_speakers(video_path: str, diarization_pipeline: Pipeline) -> List[Dict[str, Any]]:
    """Perform speaker diarization"""
    try:
        # Perform diarization
        diarization = diarization_pipeline(video_path)

        # Convert to simple format and filter overlaps
        speaker_segments = []
        prev_end = 0.0
        for turn, _, speaker in diarization.itertracks(yield_label=True):
             # Basic overlap filter: only add if the start is after the previous segment's end
             if turn.start >= prev_end:
                 speaker_segments.append({
                     "start": turn.start,
                     "end": turn.end,
                     "speaker": speaker
                 })
                 prev_end = turn.end
             # Optional: Handle small overlaps by adjusting start/end times or logging warnings
             # elif turn.end > prev_end: # Partial overlap
             #     print(f"Warning: Overlapping speaker segment detected for {speaker} at {turn.start:.2f}s. Adjusting start time.")
             #     speaker_segments.append({
             #         "start": prev_end, # Adjust start to avoid overlap
             #         "end": turn.end,
             #         "speaker": speaker
             #     })
             #     prev_end = turn.end


        # More robust filtering (optional, might remove valid short segments)
        # speaker_filter = []
        # if speaker_segments:
        #     speaker_filter.append(speaker_segments[0])
        #     prev_end_robust = speaker_segments[0]["end"]
        #     for segment in speaker_segments[1:]:
        #         if segment["start"] >= prev_end_robust:
        #             speaker_filter.append(segment)
        #             prev_end_robust = max(prev_end_robust, segment["end"])
        # return speaker_filter

        return speaker_segments

    except Exception as e:
        print(f"Error in speaker identification: {e}")
        traceback.print_exc()
        return [] # Return empty list on error

@cached_file_object('.merged')
def merge_transcript_diarization(video_path: str, transcript: List[Dict[str, Any]], diarization: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merges transcript segments with speaker diarization information."""
    merged = []
    t_idx, d_idx = 0, 0

    if not transcript:
        return [] # Return empty if no transcript

    # If diarization failed or is empty, assign UNKNOWN speaker to all transcript segments
    if not diarization:
        for segment in transcript:
             merged.append({
                 "start": segment["start"],
                 "end": segment["end"],
                 "transcript": segment["transcript"],
                 "speaker": "UNKNOWN",
                 "duration": segment["end"] - segment["start"]
             })
        return merged


    # Proceed with merging if both transcript and diarization have data
    while t_idx < len(transcript):
        t_segment = transcript[t_idx]
        t_start, t_end = t_segment["start"], t_segment["end"]
        t_mid = t_start + (t_end - t_start) / 2 # Midpoint for speaker assignment

        assigned_speaker = "UNKNOWN"

        # Find the best matching speaker segment (simple midpoint check)
        best_match_speaker = "UNKNOWN"
        found_match = False
        # Iterate through diarization segments to find overlap
        temp_d_idx = d_idx # Use a temporary index to search from the current position
        while temp_d_idx < len(diarization):
            d_segment = diarization[temp_d_idx]
            d_start, d_end = d_segment["start"], d_segment["end"]

            # Check if transcript midpoint falls within diarization segment
            if d_start <= t_mid < d_end:
                best_match_speaker = d_segment["speaker"]
                found_match = True
                # Advance the main diarization index past this segment if it ends before the transcript segment
                if d_end <= t_end:
                    d_idx = temp_d_idx + 1
                break # Found the speaker for this transcript segment

            # If diarization segment ends before transcript midpoint, advance diarization index
            elif d_end <= t_mid:
                 # Only advance main index if we are sure this segment is before the relevant one
                 if temp_d_idx == d_idx:
                     d_idx +=1
                 temp_d_idx += 1 # Keep searching forward with temp index

            # If diarization segment starts after transcript midpoint, stop searching for this transcript segment
            elif d_start >= t_mid:
                break


        merged.append({
            "start": t_start,
            "end": t_end,
            "transcript": t_segment["transcript"],
            "speaker": best_match_speaker,
            "duration": t_end - t_start,
        })
        t_idx += 1

    return merged


@cached_file_object('.compressed')
def compress_transcript(video_path: str, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compresses consecutive transcript entries with the same speaker and text."""
    if not entries:
        return []

    compressed = []
    # Initialize with the first entry, ensuring it's a copy
    current = dict(entries[0])

    for entry in entries[1:]:
        # Check for same speaker and text, and if segments are consecutive (within a small tolerance)
        # Using a small tolerance (e.g., 0.1 seconds) for consecutive check
        if (entry['speaker'] == current['speaker'] and
            entry['transcript'] == current['transcript'] and
            abs(entry['start'] - current['end']) < 0.1):
            # Merge: Update the end time
            current['end'] = max(current['end'], entry['end']) # Take the later end time
            current['duration'] = current['end'] - current['start'] # Recalculate duration
        else:
            # Different speaker/text or not consecutive: Add the completed 'current' segment
            compressed.append(current)
            # Start a new segment, ensuring it's a copy
            current = dict(entry)

    # Add the last processed segment
    compressed.append(current)

    return compressed


@cached_file_object('.introductions')
def find_introductions_setfit(video_path: str, transcripts: List[Dict[str, Any]], people_intro_model: SetFitModel) -> List[Dict[str, Any]]:
    """Identifies speaker introductions using a SetFit model."""
    try:
        if not transcripts:
            return []
        sentences = [item['transcript'] for item in transcripts]
        # Handle potential prediction errors
        try:
            labels = people_intro_model.predict(sentences)
        except Exception as pred_e:
            print(f"Error during SetFit prediction: {pred_e}")
            return [] # Return empty list on prediction failure

        # Ensure labels and transcripts align
        if len(labels) != len(transcripts):
             print(f"Warning: Mismatch between transcript segments ({len(transcripts)}) and SetFit labels ({len(labels)}). Cannot reliably filter introductions.")
             return []


        # Filter based on the label 'introduction' (adjust if your model uses a different label)
        filtered_transcripts = [transcript for transcript, label in zip(transcripts, labels) if label == 'introduction']
        return filtered_transcripts
    except Exception as e:
         print(f"Error extracting speaker introductions: {e}")
         traceback.print_exc()
         return [] # Return empty list on general failure


def speaker_to_name_mapping(introductions: List[Dict[str, Any]]) -> Dict[str, str]:
    """Creates a mapping from speaker ID (e.g., SPEAKER_01) to extracted name."""
    result = {}
    processed_speakers = set() # Keep track of speaker IDs already mapped

    for item in introductions:
        speaker_id = item.get('speaker')
        speaker_name = item.get('speaker_name', 'UNKNOWN') # Default to UNKNOWN if key missing

        # Only map if we have a valid speaker ID and haven't mapped it yet
        if speaker_id and speaker_id != "UNKNOWN" and speaker_id not in processed_speakers:
             # Prefer non-UNKNOWN names if available for the same speaker ID
             if speaker_name != "UNKNOWN":
                 result[speaker_id] = speaker_name
                 processed_speakers.add(speaker_id)
             # If current name is UNKNOWN, but we don't have a mapping yet, add it tentatively
             elif speaker_id not in result:
                 result[speaker_id] = "UNKNOWN"
                 # Don't add to processed_speakers yet, allow overwrite by a real name later

    # Ensure all speaker IDs present in the input (even if not in introductions)
    # have at least an UNKNOWN mapping if no name was found.
    # This part might be redundant if the input `introductions` covers all segments,
    # but useful if `introductions` is just a subset.
    # Consider if you need this based on how `introductions` is generated.
    # all_speaker_ids = {item.get('speaker') for item in introductions if item.get('speaker')}
    # for speaker_id in all_speaker_ids:
    #     if speaker_id and speaker_id not in result:
    #          result[speaker_id] = "UNKNOWN"


    return result

@cached_file_object('.final')
def map_speakers_to_final_transcript(video_path: str, transcripts: List[Dict[str, Any]], speaker_name_map: Dict[str, str]) -> List[Dict[str, Any]]:
    """Applies the speaker ID to name mapping to the full transcript."""
    final_transcript = []
    for transcript in transcripts:
        speaker_id = transcript.get('speaker', 'UNKNOWN')
        # Get the mapped name, default to the original speaker ID if not found,
        # and finally default to 'UNKNOWN' if speaker_id itself was missing/None.
        resolved_name = speaker_name_map.get(speaker_id, speaker_id if speaker_id else "UNKNOWN")

        # Create a new dictionary to avoid modifying the original
        final_entry = dict(transcript)
        final_entry['speaker_name'] = resolved_name
        final_transcript.append(final_entry)

    return final_transcript


@cached_file('.formatted')
def format_transcript(video_path: str, transcripts: List[Dict[str, Any]]) -> str:
    """Formats the final transcript as Markdown."""
    try:
        formatted = "# Transcribed Video\n\n"
        current_speaker = None
        for entry in transcripts:
            speaker = entry.get('speaker_name', 'UNKNOWN') # Use .get for safety
            transcript_text = entry.get('transcript', '[TRANSCRIPT MISSING]')

            # Add speaker heading only when the speaker changes
            if speaker != current_speaker:
                formatted += f"**{speaker}:**\n"
                current_speaker = speaker

            # Add the transcript text, indented slightly
            formatted += f"- {transcript_text}\n"
        return formatted
    except Exception as e:
        print(f"Error formatting transcript: {e}")
        # Attempt to return a basic representation even on error
        return json.dumps(transcripts, indent=2)
