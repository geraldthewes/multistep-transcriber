import os
import sys
import json
import torch
import logging
import argparse

from  video_processing_helpers import *
    
class VideoTranscriber:
    def __init__(self):
        # Initialize models
        self.people_intro_model_name = "gerald29/setfit-bge-small-v1.5-sst2-8-shot-introduction"
        self.people_intro_model = None


    def transcribe_video(self, video_path: str) -> str:
        """Main function to run the complete transcription process"""

        
        print('Step 1: Initial transcription')
        raw_transcript = initial_transcription(video_path)

        print('Step 2: Merge Sentences')
        merged_segments = merge_transcript_segments(video_path, raw_transcript)

        print('Step 3: Noun extraction')
        noun_list = extract_nouns(video_path, merged_segments)
        # print(noun_list)
        
        print('Step 4: Transcript correction')
        corrected_transcript = correct_transcript(video_path, merged_segments, noun_list)
        # print(corrected_transcript)
        
        print('Step 5: Speaker identification')
        speaker_mapping = identify_speakers(video_path, corrected_transcript)
        #print(speaker_mapping)

        print('Step 6: Merge transcript and diarization')
        merged_transcript = merge_transcript_diarization(video_path, corrected_transcript,  speaker_mapping )

        print('Step 7: Compress merged transcript')
        compressed_transcript = compress_transcript(video_path, merged_transcript)

        print('Step 8: Filter transcript by speaker introductions')
        speaker_introductions = find_introductions(video_path, compressed_transcript)                

        print('Step 9: Extract persons from intro')
        speaker_names = extract_persons(video_path, speaker_introductions)
        speakers = speaker_to_name(speaker_names)

        print('Step 10: Map speaker fnames')
        transcript_final = map_speakers(video_path, compressed_transcript, speakers)
        
        print('Step 11: Final formatting')
        transcript_formatted = format_transcript(video_path, transcript_final)
        transcript_markdown = format_markdown(video_path, transcript_final)        
        
        return transcript_final

