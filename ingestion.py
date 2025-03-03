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
# import outlines  # For structured LLM responses

from ollama import chat
from pydantic import BaseModel


class NounList(BaseModel):
    nouns: list[str]

class CorrectedText(BaseModel):
    corrected_text: str

class Speaker_Mapping(BaseModel):
    speaker_mapping: dict[str, str]

    
class VideoTranscriber:
    def __init__(self):
        # Initialize models
        self.whisper_model = WhisperModel("/mnt/data3/AI/software/VideoRAG/faster-distil-whisper-large-v3")
        self.whisper_model.logger.setLevel(logging.WARNING)
        self.diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                                             use_auth_token=os.environ["HF_TOKEN"])
        self.noun_extraction_model = "granite3.2:latest"  # Store the model name as a class attribute
        self.corrected_transcript_model = "granite3.2:latest" # need 128K token content length or more
        
    def initial_transcription(self, video_path: str) -> str:
        """Perform initial transcription using Whisper"""
        try:
            segments, info = self.whisper_model.transcribe(video_path)
            raw_transcript = " ".join(segment.text for segment in segments)
            return raw_transcript
        except Exception as e:
            print(f"Error in initial transcription: {e}")
            return ""

    def extract_nouns(self, transcript: str) -> list:
        """Extract proper nouns and technical terms from master document"""
        try:
            # Define structured output format
            structured_prompt =  f'Extract all proper nouns, people names, locations, technical terms, and important concepts from this text. Return as a JSON list. {transcript}'
            
            # Using outlines with a local LLM (replace with your preferred model)
            response = chat(model=self.noun_extraction_model,
                            messages=[{'role':'user', 'content':structured_prompt}])
                            #format=NounList.model_json_schema())
            return response['message']['content']
        except Exception as e:
            print(f"Error extracting nouns: {e}")
            return []

    def correct_transcript(self, raw_transcript: str, noun_list: list) -> str:
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

- Use markdown for your output.""",
            
            # Combine inputs
            input_data = {
                "transcript": raw_transcript,
                "nouns": noun_list
            }

            response = chat(model=self.correct_transcript,
                            messages=input_data,
                            format=CorrectedText.model_json_schema())
            return response['message']['content']
        except Exception as e:
            print(f"Error correcting transcript: {e}")
            return raw_transcript

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
            print(speaker_segments)    
                
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
        if not raw_transcript:
            return "Transcription failed"
        print(raw_transcript)

        print('Step 2: Noun extraction')
        noun_list = self.extract_nouns(raw_transcript)
        print(noun_list)
        

        print('Step 3: Transcript correction')
        corrected_transcript = self.correct_transcript(raw_transcript, noun_list)
        print(corrected_transcript)
        
        print('Step 4: Speaker identification')
        speaker_mapping = self.identify_speakers(video_path, corrected_transcript)
        print(speaker_mapping)
        
        print('Step 5: Final formatting')
        final_transcript = self.format_transcript(corrected_transcript, speaker_mapping)
        print(final_transcript)
        
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
