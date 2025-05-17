import os
import sys
import json
import torch
import logging
import argparse
from typing import List, Dict, Any

from  video_processing_helpers import *
    
class VideoTranscriber:
    def __init__(self, topic_config=None):
        # Initialize models
        self.topic_config = topic_config

    def transcribe_video(self, video_path: str) -> list:
        """Main function to run the complete transcription process"""

        
        print('Step 1: Initial transcription')
        raw_transcript = initial_transcription(video_path)

        print('Step 2: Merge Sentences')
        merged_segments = merge_transcript_segments(video_path, raw_transcript)

        print('Step 3: Entity extraction')
        nouns_list = extract_nouns(video_path, merged_segments)
        
        print('Step 4: Transcript correction')
        corrected_transcript = correct_transcript(video_path, merged_segments, nouns_list)
        # print(corrected_transcript)
        
        print('Step 5: Diarization / Speaker identification')
        speaker_mapping = identify_speakers(video_path, corrected_transcript)
        #print(speaker_mapping)

        print('Step 6: Merge transcript and diarization')
        merged_transcript = merge_transcript_diarization(video_path, corrected_transcript,  speaker_mapping )

        print('Step 7: Compress merged transcript')
        compressed_transcript = compress_transcript(video_path, merged_transcript)

        print('Step 8: Filter transcript by speaker introductions')
        # Use raw transcript as sentence merge can cause timing mismatch        
        speaker_introductions = find_introductions(video_path, raw_transcript)                

        # Move logic to a function so this remains one call
        print('Step 9: Extract persons from introductions')
        # Create mapping betyween person name and diarization.
        # first extract name from introductions
        speaker_names = extract_persons(speaker_introductions)
        # Now map name to diarization
        speakers_diarization = map_entities_to_speakers(video_path, speaker_names, speaker_mapping)
        # Now create map of speaker to speaker_name
        speakers = speaker_to_name(speakers_diarization)

        print('Step 10: Map speaker names')
        transcript_final = map_speakers(video_path, compressed_transcript, speakers)
        
        return transcript_final, nouns_list

    def topics(self, video_path: str, transcript: list, max_topics) -> list:
        """Break transcript into topics"""
        if not self.topic_config:
            print('No topic segmentation configuration. Skipping topic segmentation')
            return transcript
        processed_transcript = segment_topics(video_path, transcript, self.topic_config, max_topics)
        return processed_transcript
    
    def format_transcript(self, video_path: str, transcript: list, nouns_list:  Dict[str, List[Dict[str, Any]]]) -> None:
        """Format the transcript"""

        transcript_formatted = format_transcript(video_path, transcript)
        transcript_markdown = format_markdown(video_path, transcript, nouns_list)        
        
