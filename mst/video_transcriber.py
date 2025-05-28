import os
import sys
import json
import torch
import logging
import argparse
from typing import List, Dict, Any

from  .steps import *
    
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

        print('Step 9: Extract persons from introductions')
        speaker_map = create_speaker_map(video_path, speaker_introductions, speaker_mapping)

        print('Step 10: Map speaker names')
        transcript_final = map_speakers(video_path, compressed_transcript, speaker_map)
        
        return transcript_final, nouns_list

    def topics(self, video_path: str, transcript: list, max_topics) -> list:
        """Break transcript into topics"""
        if not self.topic_config:
            print('No topic segmentation configuration. Skipping topic segmentation')
            return transcript
        processed_transcript = segment_topics(video_path, transcript, self.topic_config, max_topics)
        # Generate and cache topic headlines
        topic_headlines = prepare_and_generate_headlines(video_path, processed_transcript)
        topic_summary = prepare_and_generate_summary(video_path, processed_transcript)
        
        return processed_transcript, topic_headlines, topic_summary
    
    def format_transcript(self,
                          video_path: str,
                          transcript: list,
                          nouns_list:  Dict[str, List[Dict[str, Any]]],
                          topic_headlines: list,
                          topic_summary: list) -> None:
        """Format the transcript"""

        transcript_formatted = format_transcript(video_path, transcript)
        transcript_markdown = format_markdown(video_path, transcript, nouns_list, topic_headlines, topic_summary)        


    def retrieve_json(self, video_path: str): 
        ''' return transcription result as JSON '''
        path = get_cache_file(video_path, EXTENSION_TOPICS)        
        return load_text_file(path)

    def retrieve_markdown(self, video_path: str): 
        ''' return transcription result as markdown '''
        path = get_cache_file(video_path, EXTENSION_MARKDOWN)
        return load_object_file(path)
        
    def clear(self, video_path: str):
        '''Clear all cache files '''
        return clear_cache_directory(video_path)
