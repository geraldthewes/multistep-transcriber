import os
import sys
import json
import torch
import logging
import argparse
import traceback
from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer
from pyannote.audio import Pipeline
from gliner import GLiNER
from setfit import SetFitModel

# Import helpers from the new package
from video_processing_helpers import helpers
# Note: Models and Caching decorators are used within the helpers module now.


class VideoTranscriber:
    def __init__(self):
        # Initialize all models here for efficiency
        print("Initializing models...")
        # Whisper
        # Consider making model paths/names configurable
        self.whisper_model_path = "/mnt/data3/AI/software/VideoRAG/faster-distil-whisper-large-v3"
        try:
            self.whisper_model = WhisperModel(self.whisper_model_path)
            self.whisper_model.logger.setLevel(logging.WARNING) # Set log level once
            print(f"Whisper model loaded from {self.whisper_model_path}")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.whisper_model = None

        # Diarization
        self.diarization_model_name = "pyannote/speaker-diarization-3.1"
        try:
            # Ensure HF_TOKEN is set in environment or handle authentication appropriately
            hf_token = os.environ.get("HF_TOKEN")
            if not hf_token:
                print("Warning: HF_TOKEN environment variable not set. Diarization model might fail to load.")
            self.diarization_pipeline = Pipeline.from_pretrained(
                self.diarization_model_name,
                use_auth_token=hf_token
            )
            # Move to GPU if available
            if torch.cuda.is_available():
                self.diarization_pipeline.to(torch.device("cuda"))
                print(f"Diarization pipeline '{self.diarization_model_name}' loaded to CUDA.")
            else:
                 print(f"Diarization pipeline '{self.diarization_model_name}' loaded to CPU.")
        except Exception as e:
            print(f"Error loading Diarization pipeline: {e}")
            self.diarization_pipeline = None

        # GLiNER (Entity Extraction)
        self.entity_model_name = "urchade/gliner_medium-v2.1"
        try:
            self.entity_model = GLiNER.from_pretrained(self.entity_model_name)
            print(f"GLiNER model '{self.entity_model_name}' loaded.")
        except Exception as e:
            print(f"Error loading GLiNER model: {e}")
            self.entity_model = None

        # Sentence Transformer (Noun Correction)
        self.noun_correction_model_name = 'paraphrase-MiniLM-L6-v2'
        try:
            self.noun_correction_model = SentenceTransformer(self.noun_correction_model_name)
            print(f"SentenceTransformer model '{self.noun_correction_model_name}' loaded.")
        except Exception as e:
            print(f"Error loading SentenceTransformer model: {e}")
            self.noun_correction_model = None

        # SetFit (Introduction Detection)
        self.people_intro_model_name = "gerald29/setfit-bge-small-v1.5-sst2-8-shot-introduction"
        try:
            self.people_intro_model = SetFitModel.from_pretrained(self.people_intro_model_name)
            print(f"SetFit model '{self.people_intro_model_name}' loaded.")
        except Exception as e:
            print(f"Error loading SetFit model: {e}")
            self.people_intro_model = None

        print("Model initialization complete.")


    # --- Removed helper methods, now in video_processing_helpers.helpers ---


    def transcribe_video(self, video_path: str) -> str:
        """Main function to run the complete transcription process using helper functions."""

        # Check if essential models loaded correctly
        if not self.whisper_model:
             print("Error: Whisper model not loaded. Cannot transcribe.")
             return "Transcription failed: Whisper model unavailable."
        # Add similar checks for other critical models if necessary

        print('Step 1: Initial transcription')
        # Pass the initialized model to the helper function
        raw_transcript = helpers.initial_transcription(video_path, self.whisper_model)
        if raw_transcript is None: return "Transcription failed at Step 1."

        print('Step 2: Noun extraction')
        if not self.entity_model:
            print("Warning: GLiNER model not loaded. Skipping noun extraction.")
            noun_list_str = ""
        else:
            noun_list_str = helpers.extract_nouns(video_path, raw_transcript, self.entity_model)
        # print(noun_list_str)

        print('Step 3: Transcript correction')
        if not self.noun_correction_model:
             print("Warning: SentenceTransformer model not loaded. Skipping transcript correction.")
             corrected_transcript = raw_transcript # Use raw if correction model failed
        elif not noun_list_str:
             print("Warning: No nouns extracted. Skipping transcript correction.")
             corrected_transcript = raw_transcript
        else:
            corrected_transcript = helpers.correct_transcript(video_path, raw_transcript, noun_list_str, self.noun_correction_model)
            if corrected_transcript is None:
                print("Warning: Transcript correction failed. Using raw transcript for subsequent steps.")
                corrected_transcript = raw_transcript
        # print(corrected_transcript)

        print('Step 4: Speaker identification')
        if not self.diarization_pipeline:
            print("Warning: Diarization pipeline not loaded. Skipping speaker identification.")
            diarization_result = [] # Empty list if diarization fails
        else:
            diarization_result = helpers.identify_speakers(video_path, self.diarization_pipeline)
        #print(diarization_result)

        print('Step 5: Merge transcript and diarization')
        merged_transcript = helpers.merge_transcript_diarization(video_path, corrected_transcript, diarization_result)
        if not merged_transcript: return "Transcription failed at Step 5." # Or handle differently

        print('Step 6: Compress merged transcript')
        compressed_transcript = helpers.compress_transcript(video_path, merged_transcript)
        if not compressed_transcript: return "Transcription failed at Step 6."

        print('Step 7: Filter transcript by speaker introductions')
        if not self.people_intro_model:
            print("Warning: SetFit model not loaded. Skipping introduction filtering.")
            speaker_introductions = []
        else:
            speaker_introductions = helpers.find_introductions_setfit(video_path, compressed_transcript, self.people_intro_model)

        print('Step 8: Extract persons from intro')
        # This step now needs the entity_model and the *introductions* list
        if not self.entity_model:
             print("Warning: GLiNER model not loaded. Cannot extract speaker names from introductions.")
             speaker_names_list = speaker_introductions # Pass through if model missing
        elif not speaker_introductions:
             print("Info: No introductions found to extract speaker names from.")
             speaker_names_list = []
        else:
            # Extract persons specifically from the introduction segments
            speaker_names_list = helpers.extract_persons(video_path + "_intros", # Use modified path for caching
                                                         speaker_introductions,
                                                         self.entity_model)
            # Note: Caching for extract_persons might need adjustment if video_path collision is an issue.
            # Using video_path + "_intros" attempts to create a unique cache key.

        # Create the speaker ID -> Name map
        speaker_id_to_name_map = helpers.speaker_to_name_mapping(speaker_names_list)
        print(f"Speaker Map: {speaker_id_to_name_map}")


        print('Step 9: Map speaker names to full transcript')
        # Apply the map to the *compressed* transcript
        transcript_final = helpers.map_speakers_to_final_transcript(video_path, compressed_transcript, speaker_id_to_name_map)
        if not transcript_final: return "Transcription failed at Step 9."


        print('Step 10: Final formatting')
        transcript_formatted = helpers.format_transcript(video_path, transcript_final)

        # Save the final formatted transcript (optional, can be done in main)
        base_name, _ = os.path.splitext(video_path)
        output_file = base_name + ".transcription.md"
        try:
            with open(output_file, "w", encoding='utf-8') as f:
                f.write(transcript_formatted)
            print(f"Final transcript saved to {output_file}")
        except Exception as e:
            print(f"Error saving final transcript: {e}")


        return transcript_formatted



def main():
    parser = argparse.ArgumentParser(description="Transcribe a video file.")

    # Add arguments
    parser.add_argument("video_path", type=str, help="Path to the video file")

    # Parse arguments
    args = parser.parse_args()
    
    video_path = args.video_path
    
    if not os.path.exists(video_path):
        print("Error: File(s) not found")
        sys.exit(1)

    # Initialize the transcriber (loads models)
    transcriber = VideoTranscriber()

    print(f'\nStarting transcription process for: {video_path}')
    result = transcriber.transcribe_video(video_path)

    # Output is now saved within transcribe_video, but you could print status here
    if "failed" in result.lower():
         print(f"\nTranscription process encountered errors.")
    else:
         print(f"\nTranscription process finished for {video_path}.")
         # The final file path is printed within transcribe_video


if __name__ == "__main__":
    main()


