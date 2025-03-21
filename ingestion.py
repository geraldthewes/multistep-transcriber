import os
import sys
import json
import torch
import logging
import argparse
from tqdm import tqdm
from faster_whisper import WhisperModel
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from sentence_transformers import SentenceTransformer, util
from pyannote.audio import Pipeline
from typing import List
from gliner import GLiNER
from setfit import SetFitModel
import re
import traceback

# import outlines  # For structured LLM responses

from ollama import chat, generate
from pydantic import BaseModel


class NounList(BaseModel):
    nouns: list[str]

class CorrectedText(BaseModel):
    corrected_text: str

class Speaker_Mapping(BaseModel):
    speaker_mapping: dict[str, str]


# Approximate conversion factor (1 word ≈ 4 tokens)
WORDS_TO_TOKENS_RATIO = 1.34

def cached_file(file_ext):
    """
    A decorator that caches the output of a function to a file.
    
    Args:
        file_ext (str): The file extension used for the cache file.
        
    Returns:
        function: A decorator that applies the caching behavior.
    """
    def decorator(func):
        def wrapper(self, video_path, *args, **kwargs):
            # Construct the cache file name
            base_name, _ = os.path.splitext(video_path)
            cache_dir = base_name + '.d'
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, 'cache' + file_ext)            
            
            # Try to load from cache if it exists
            if os.path.exists(cache_file):
                print(f"Loading cached data from {cache_file}")
                with open(cache_file, 'r', encoding='utf-8') as file:
                    return file.read()
            
            # Compute the result since cache doesn't exist
            result = func(self, video_path, *args, **kwargs)
            
            if not result:  # Check for failure
                print(f"Error in computing {func.__name__}")
                return f"{func.__name__} failed"
            
            # Save to cache
            with open(cache_file, 'w', encoding='utf-8') as file:
                file.write(result)
                
            return result
        
        return wrapper
    
    return decorator

def cached_file_object(file_ext):
    """
    A decorator that caches the output of a function to a file.
    Args:
        file_ext (str): The file extension used for the cache file.
    Returns:
        function: A decorator that applies the caching behavior.
    """
    def decorator(func):
        def wrapper(self, video_path, *args, **kwargs):
            # Construct the cache file name
            base_name, _ = os.path.splitext(video_path)
            cache_dir = base_name + '.d'
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, 'cache' + file_ext)                                           
            
            # Try to load from cache if it exists
            if os.path.exists(cache_file):
                print(f"Loading cached data from {cache_file}")
                with open(cache_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            
            # Compute the result since cache doesn't exist
            result = func(self, video_path, *args, **kwargs)
            if not result:  # Check for failure
                print(f"Error in computing {func.__name__}")
                return f"{func.__name__} failed"
            
            # Save to cache
            with open(cache_file, 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=4)
            
            return result
        return wrapper
    return decorator
    
class VideoTranscriber:
    def __init__(self):
        # Initialize models
        self.whisper_model = None
        self.diarization_pipeline = None
        self.diarization_model = "pyannote/speaker-diarization-3.1"
        # Initialize GLiNER with the base model
        self.entity_model = None
        self.noun_correction_model = None
        #self.corrected_transcript_model = "granite3.2:latest" # need 128K token content length or more
        #self.people_filter_model = "deepseek-v2:latest"
        self.people_intro_model_name = "gerald29/setfit-bge-small-v1.5-sst2-8-shot-introduction"
        self.people_intro_model = None

    @cached_file_object('.raw_transcript')
    def initial_transcription(self, video_path: str) -> str:
        """Perform initial transcription using Whisper"""
        try:
            if not self.whisper_model:
                self.whisper_model = WhisperModel("/mnt/data3/AI/software/VideoRAG/faster-distil-whisper-large-v3")
                self.whisper_model.logger.setLevel(logging.WARNING)

            segments, info = self.whisper_model.transcribe(video_path)
            output_lines = []
            current_start = None
            curr_end = None
            current_text = None

            for segment in segments:
                if current_text is None or segment.text != current_text:
                    # If it's the first segment or the text has changed, add the previous range to output_lines
                    if current_text is not None:
                        # Emit previous transcript
                        output_lines.append({
                            "start": current_start,
                            "end": current_end,
                            "transcript": current_text
                            })

                    # Start a new range
                    current_start = segment.start
                    current_end = segment.end                    
                    current_text = segment.text
                else:
                    # If the text is the same, extend the end time of the current range
                    current_end = segment.end                                    

            # Add the last range to output_lines
            if current_text is not None:
                output_lines.append({
                    "start": current_start,
                    "end": current_end,
                    "transcript": current_text
                })
            return output_lines
        except Exception as e:
            print(f"Error in initial transcription: {e}")
            return None

    ''' Extract what we need from results '''
    def group_by_label(self, data):
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

    def flatten_texts(self, input_dict):
        ''' Just return the nouns '''
        texts = []
        for label in input_dict:
            for item in input_dict[label]:
                texts.append(item['text'])
        return texts

    ''' Merge entities, pick highest prob'''
    def merge_similar_texts(self, data):
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
        return ','.join(self.flatten_texts(result))

    @cached_file('.nouns')
    def extract_nouns(self, video_path: str, transcript: str) -> list:
        labels = ["Person", "Organizations", "Date", "Positions", "Locations"]
        entities =  self.extract_entities(video_path, labels, transcript)
        entities_by_label = self.group_by_label(entities)
        entities_merged = self.merge_similar_texts(entities_by_label)
        return entities_merged

    @cached_file_object('.speaker_names')
    def extract_persons(self, video_path: str, transcripts: str) -> list:
        labels = ["Person"]
        entities = self.extract_entities(video_path, labels, transcripts)
        speaker_names=[]
        for introduction in entities:
            name = [item['text'] for item in introduction]
            if name:
                speaker_names.append(name[0])
        speakers = [transcript | {'speaker_name': name} for transcript, name in zip(transcripts, speaker_names)]
        return speakers
        
    def extract_entities(self, video_path: str, labels: list, transcript: str) -> list:
        """Extract proper nouns and technical terms from master document"""
        try:
            if not self.entity_model:
                self.entity_model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
            transcript_sentences = [item['transcript'] for item in transcript]            
            # Perform entity prediction
            entities = self.entity_model.batch_predict_entities(transcript_sentences, labels, threshold=0.5)
            return entities
        except Exception as e:
            print(f"Error extracting nouns: {e}")
            traceback.print_exc()            
            return None



    def standardize_nouns_ai(self, transcript: list, noun_list: list):
        """
        Standardizes nouns using AI-based phonetic similarity via embeddings, preserving line feeds.

        Args:
            transcript (str): Text with phonetic variations and original line breaks
            noun_list (list): Standard noun spellings

        Returns:
            str: Standardized transcript with line breaks preserved
        """
        # Load the model
        if not self.noun_correction_model:
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
    def correct_transcript(self, video_path: str, raw_transcript: list, nouns: str) -> str:
        """Correct transcript using LLM and noun list"""
        try:
            nouns_list = nouns.split(',')
            return self.standardize_nouns_ai(raw_transcript, nouns_list)
        except Exception as e:
            print(f"Error correcting transcript: {e}")
            traceback.print_exc()            
            return None

    @cached_file_object('.diarization')
    def identify_speakers(self, video_path: str, transcript: str) -> dict:
        """Perform speaker diarization and mapping"""
        try:
            if not self.diarization_pipeline:
                self.diarization_pipeline = Pipeline.from_pretrained(
                    self.diarization_model,
                    use_auth_token=os.environ["HF_TOKEN"])
                self.diarization_pipeline.to(torch.device("cuda"))
            
            # Perform diarization
            diarization = self.diarization_pipeline(video_path)
            
            # Convert to simple format
            speaker_segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speaker_segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })

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
            return {}
        
    @cached_file_object('.merged')
    def merge_transcript_diarization(self, video_path: str, transcript: list, diarization: list):
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
    def compress_transcript(self, video_path: str, entries: list):
        if not entries:
            return []

        compressed = []
        current = dict(entries[0])  # Create a copy of the first entry
        duration = current["duration"]
        speaker = current["speaker"]

        for entry in entries[1:]:
            # Check if current entry matches the previous one in transcript and speaker
            if (entry['transcript'] == current['transcript'] and 
                entry['start'] == current['end']):  # Check if times are consecutive
                # Update the end time to the current entry's end time
                current['end'] = entry['end']
                if entry["duration"] > duration:
                    # Select one ker corresponding to largest duration
                    speaker = entry['speaker']
            else:
                # Add the completed entry to our result and start a new one
                compressed.append(current)
                current = dict(entry)  # Create a copy of the new entry
                duration = current['duration']
                speaker  =  current['speaker']
        # Don't forget to add the last entry
        compressed.append(current)

        return compressed
    
        
    def map_speakers(self):
        try:
            # Map speakers to names using context (simplified example)
            mapping_prompt = "Based on this transcript and speaker segments, map speaker labels to actual names."
            input_data = {
                "transcript": transcript,
                "segments": speaker_segments
            }
            
            response = chat(
                messages=input_data,
                model="your-local-llm-model",
                format=Speaker_Mapping.model_json_schema()
            )
            return response["speaker_mapping"]
        except Exception as e:
            print(f"Error in speaker mapping: {e}")
            return {}

    @cached_file_object('.introductions')
    def find_introductions_setfit(self, video_path: str, transcripts):
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

    def speaker_to_name(self, introductions: str):
        # Initialize an empty dictionary for the result
        result = {}
        
        # Iterate over each entry in the list
        for item in introductions:
            speaker_key = item['speaker']
            speaker_value = item['speaker_name']

            # If the speaker is UNKNOWN, set the value to UNKNOWN
            if speaker_key == "UNKNOWN":
                speaker_value = "UNKNOWN"

            # Add the mapping to the result dictionary
            result[speaker_key] = speaker_value
        return result

    @cached_file_object('.final')    
    def map_speakers(self, video_path: str, transcripts: list, speaker_to_name: dict):
        return  [transcript | {'speaker_name': speaker_to_name.get(transcript['speaker'],transcript['speaker'])} for transcript in transcripts]
    
    def format_transcript(self, transcript: str, speaker_mapping: dict) -> str:
        """Format final transcript as Markdown"""
        try:
            formatted = "# Transcribed Video\n\n"
            # This is a simplified formatting - enhance as needed
            for line in transcript.split('.'):
                if line.strip():
                    speaker = list(speaker_mapping.values())[0]  # Simplified
                    formatted += f"**{speaker}:** {line.strip()}.\n\n"
            return formatted
        except Exception as e:
            print(f"Error formatting transcript: {e}")
            return transcript

    def transcribe_video(self, video_path: str) -> str:
        """Main function to run the complete transcription process"""

        
        print('Step 1: Initial transcription')
        raw_transcript = self.initial_transcription(video_path)

        print('Step 2: Noun extraction')
        noun_list = self.extract_nouns(video_path, raw_transcript)
        # print(noun_list)
        
        print('Step 3: Transcript correction')
        corrected_transcript = self.correct_transcript(video_path, raw_transcript, noun_list)
        # print(corrected_transcript)
        
        print('Step 4: Speaker identification')
        speaker_mapping = self.identify_speakers(video_path, corrected_transcript)
        #print(speaker_mapping)

        print('Step 5: Merge transcript and diarization')
        merged_transcript = self.merge_transcript_diarization(video_path, corrected_transcript,  speaker_mapping )

        print('Step 6: Compress merged transcript')
        compressed_transcript = self.compress_transcript(video_path, merged_transcript)

        print('Step 7: Filter transcript by speaker introductions')
        speaker_introductions = self.find_introductions_setfit(video_path, compressed_transcript)                

        print('Step 8: Extract persons from intro')
        speaker_names = self.extract_persons(video_path, speaker_introductions)
        speakers = self.speaker_to_name(speaker_names)

        print('Step 9: Map speaker names')
        transcript_final = self.map_speakers(video_path, compressed_transcript, speakers)
        
        
        #print('Step 6: Final formatting')
        #final_transcript = self.format_transcript(corrected_transcript, speaker_mapping)
        #print(final_transcript)
        
        # return final_transcript



def main():
    parser = argparse.ArgumentParser(description="Transcribe a video using a master document.")
    
    # Add arguments
    parser.add_argument("video_path", type=str, help="Path to the video file")
    
    # Parse arguments
    args = parser.parse_args()
    
    video_path = args.video_path
    
    if not os.path.exists(video_path):
        print("Error: File(s) not found")
        sys.exit(1)

    print('Setup')
    transcriber = VideoTranscriber()
    print(f'Transcribe {video_path}')
    result = transcriber.transcribe_video(video_path)
    
    # Save output
    #with open("transcription.md", "w") as f:
    #    f.write(result)
    #print("Transcription complete. Output saved to transcription.md")

    
if __name__ == "__main__":
    main()


