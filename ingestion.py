import os
import sys
import json
import torch
import logging
import argparse
from tqdm import tqdm
from faster_whisper import WhisperModel
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pyannote.audio import Pipeline
from typing import List
from gliner import GLiNER
import re
import traceback

# import outlines  # For structured LLM responses

from ollama import chat
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
        self.whisper_model = WhisperModel("/mnt/data3/AI/software/VideoRAG/faster-distil-whisper-large-v3")
        self.whisper_model.logger.setLevel(logging.WARNING)
        self.diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token=os.environ["HF_TOKEN"])
        self.diarization_pipeline.to(torch.device("cuda"))
        # Initialize GLiNER with the base model
        self.entity_model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
        self.corrected_transcript_model = "granite3.2:latest" # need 128K token content length or more

    @cached_file_object('.raw_transcript')
    def initial_transcription(self, video_path: str) -> str:
        """Perform initial transcription using Whisper"""
        try:
            segments, info = self.whisper_model.transcribe(video_path)
            output_lines = []
            current_start = None
            curr_end = None
            current_text = None

            for segment in segments:
                if current_text is None or segment.text != current_text:
                    # If it's the first segment or the text has changed, add the previous range to output_lines
                    if current_text is not None:
                        formatted_line = f"[{current_start:.2f}s -> {segment.end:.2f}s]  {current_text}"
                        output_lines.append({
                            "start": current_start,
                            "end": segment.end,
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
                    "end": segment.end,
                    "transcript": current_text
                })
            return output_lines
        except Exception as e:
            print(f"Error in initial transcription: {e}")
            return None

    ''' Extract what we ned from results '''
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
        """Extract proper nouns and technical terms from master document"""
        try:
            transcript_sentences = [item['transcript'] for item in transcript]            
            labels = ["Person", "Organizations", "Date", "Positions", "Locations"]
            # Perform entity prediction
            entities = self.entity_model.batch_predict_entities(transcript_sentences, labels, threshold=0.5)
            entities_by_label = self.group_by_label(entities)
            entities_merged = self.merge_similar_texts(entities_by_label)
            return entities_merged
        except Exception as e:
            print(f"Error extracting nouns: {e}")
            traceback.print_exc()            
            return None

    @cached_file('.corrected_transcript')        
    def correct_transcript(self, video_path: str, raw_transcript: str, nouns: str) -> str:
        """Correct transcript using LLM and noun list"""
        try:
            # Using outlines for structured correction
            correction_prompt = """You are a skilled editor and in charge of editorial content and you will be given a transcript from an interview, video essay, podcast or speech and a set of nouns. Your job is to keep as much as possible from the original transcript and only make fixes for replacing nouns with the correct variant, for clarity or abbreviation, grammar, punctuation and format according to this general set of rules:

- Beware that this transcript is auto generated from speech so it can contain wrong or misspelled words, make your best effort to fix those words, never change the overall structure of the transcript, just focus con correcting specific words, fixing punctuation and formatting.

- Before doing your task be sure to read enough of the transcript so you can infer the overall context and make better judgements for the needed fixes.

- The same noun may be transcripted using different variations, your job is to pick the most correct one and use it consistently. 

- The most important rule is to keep the original transcript mostly unaltered word for word and especially in tone. You are only allowed to make small editorial changes for punctuation, grammar, formatting and clarity.

- You are allowed to modify the text only if in said context the subject correct themselves, so your job is to clean up the phrase for clarity and eliminate repetition.

- If by any chance you have to replace a word, please ~~strike trough~~ the original word and add a memo emoji 📝 next to your predicted correction.

- Use markdown for your output.

Use the following Nouns: {nouns}

Below is the transcript to correct:

{raw_transcript}
            
"""
            


            response = chat(model=self.correct_transcript,
                            messages=correction_prompt)
            return response['message']['content']
        except Exception as e:
            print(f"Error correcting transcript: {e}")
            traceback.print_exc()            
            return None

    @cached_file_object('.diarization')
    def identify_speakers(self, video_path: str, transcript: str) -> dict:
        """Perform speaker diarization and mapping"""
        try:
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
            print(f"Error in speaker identification: {e}")
            return {}

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
        print(noun_list)
        
        print('Step 3: Transcript correction')
        corrected_transcript = self.correct_transcript(video_path, raw_transcript, noun_list)
        print(corrected_transcript)
        
        print('Step 4: Speaker identification')
        speaker_mapping = self.identify_speakers(video_path, corrected_transcript)
        #print(speaker_mapping)
        
        print('Step 5: Final formatting')
        final_transcript = self.format_transcript(corrected_transcript, speaker_mapping)
        #print(final_transcript)
        
        return final_transcript



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
    
    transcriber = VideoTranscriber()
    result = transcriber.transcribe_video(video_path)
    
    # Save output
    with open("transcription.md", "w") as f:
        f.write(result)
    print("Transcription complete. Output saved to transcription.md")

    
if __name__ == "__main__":
    main()
