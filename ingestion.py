import os
import sys
import json
import torch
import logging
from tqdm import tqdm
from faster_whisper import WhisperModel
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pyannote.audio import Pipeline
import outlines  # For structured LLM responses

class VideoTranscriber:
    def __init__(self):
        # Initialize models
        self.whisper_model = WhisperModel("./faster-distil-whisper-large-v3")
        self.whisper_model.logger.setLevel(logging.WARNING)
        self.diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

    def initial_transcription(self, video_path: str) -> str:
        """Perform initial transcription using Whisper"""
        try:
            segments, info = self.whisper_model.transcribe(video_path)
            raw_transcript = " ".join(segment.text for segment in segments)
            return raw_transcript
        except Exception as e:
            print(f"Error in initial transcription: {e}")
            return ""

    def extract_nouns(self, master_document_path: str) -> list:
        """Extract proper nouns and technical terms from master document"""
        try:
            with open(master_document_path, 'r') as f:
                text = f.read()

            # Define structured output format
            structured_prompt = outlines.prompt(
                "Extract all proper nouns, technical terms, and important concepts from this text. "
                "Return as a JSON list.",
                output_format={"terms": list[str]}
            )
            
            # Using outlines with a local LLM (replace with your preferred model)
            response = outlines.generate(text, model="your-local-llm-model", prompt=structured_prompt)
            return response["terms"]
        except Exception as e:
            print(f"Error extracting nouns: {e}")
            return []

    def correct_transcript(self, raw_transcript: str, noun_list: list) -> str:
        """Correct transcript using LLM and noun list"""
        try:
            # Using outlines for structured correction
            correction_prompt = outlines.prompt(
                "Correct this transcript, paying special attention to the proper nouns and terms "
                "in the provided list. Ensure proper punctuation and formatting.",
                output_format={"corrected_text": str}
            )
            
            # Combine inputs
            input_data = {
                "transcript": raw_transcript,
                "nouns": noun_list
            }
            
            response = outlines.generate(
                input_data,
                model="your-local-llm-model",
                prompt=correction_prompt
            )
            return response["corrected_text"]
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
            
            # Map speakers to names using context (simplified example)
            mapping_prompt = outlines.prompt(
                "Based on this transcript and speaker segments, map speaker labels to actual names.",
                output_format={"speaker_mapping": dict[str, str]}
            )
            
            input_data = {
                "transcript": transcript,
                "segments": speaker_segments
            }
            
            response = outlines.generate(
                input_data,
                model="your-local-llm-model",
                prompt=mapping_prompt
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

    def transcribe_video(self, video_path: str, master_doc_path: str) -> str:
        """Main function to run the complete transcription process"""
        # Step 1: Initial transcription
        raw_transcript = self.initial_transcription(video_path)
        if not raw_transcript:
            return "Transcription failed"

        # Step 2: Noun extraction
        noun_list = self.extract_nouns(master_doc_path)
        
        # Step 3: Transcript correction
        corrected_transcript = self.correct_transcript(raw_transcript, noun_list)
        
        # Step 4: Speaker identification
        speaker_mapping = self.identity_speakers(video_path, corrected_transcript)
        
        # Step 5: Final formatting
        final_transcript = self.format_transcript(corrected_transcript, speaker_mapping)
        
        return final_transcript

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <video_path> <master_document_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    master_doc_path = sys.argv[2]
    
    if not os.path.exists(video_path) or not os.path.exists(master_doc_path):
        print("Error: File(s) not found")
        sys.exit(1)
    
    transcriber = VideoTranscriber()
    result = transcriber.transcribe_video(video_path, master_doc_path)
    
    # Save output
    with open("transcription.md", "w") as f:
        f.write(result)
    print("Transcription complete. Output saved to transcription.md")

if __name__ == "__main__":
    main()
