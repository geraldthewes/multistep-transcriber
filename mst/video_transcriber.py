import os
import sys
import json
import torch
import logging
import argparse
from typing import List, Dict, Any

from  .steps import *
    
class VideoTranscriber:
    """
    A class to handle the end-to-end video transcription process,
    including initial transcription, noun extraction, correction,
    speaker diarization, topic segmentation, and formatting.
    """
    def __init__(self, topic_config=None):
        """
        Initializes the VideoTranscriber.

        Args:
            topic_config (dict, optional): Configuration for topic segmentation.
                                           Defaults to None, in which case topic
                                           segmentation will be skipped.
        """
        # Initialize models
        self.topic_config = topic_config

    def transcribe_video(self, video_path: str, transcribe: bool = True) -> list:
        """
        Processes a video file through the complete transcription pipeline.

        The pipeline includes:
        1. Initial transcription using a speech-to-text model.
        2. Merging transcript segments into sentences.
        3. Extracting nouns and important terms.
        4. Correcting the transcript using the extracted nouns.
        5. Identifying speakers (diarization).
        6. Merging diarization information with the transcript.
        7. Compressing the transcript by combining consecutive segments from the same speaker.
        8. Finding speaker introductions in the raw transcript.
        9. Creating a map of speaker IDs to actual names based on introductions.
        10. Applying the speaker names to the final transcript.

        Args:
            video_path (str): The file path to the video or audio file.
            transcribe(bool): False to skip audio transcription, default True 

        Returns:
            tuple: A tuple containing:
                - transcript_final (list): The final processed transcript with speaker information.
                - nouns_list (list): A list of extracted nouns and entities.
        """

        
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

    def topics(self, video_path: str, transcript: list, max_topics: int) -> tuple:
        """
        Segments the transcript into topics and generates headlines and summaries for them.

        If `topic_config` was not provided during initialization, this step is skipped.

        Args:
            video_path (str): The file path to the video or audio file, used for caching.
            transcript (list): The transcript to be segmented (typically the output of `transcribe_video`).
            max_topics (int): The maximum number of topics to segment the transcript into.

        Returns:
            tuple: A tuple containing:
                - processed_transcript (list): The transcript with topic information.
                - topic_headlines (list): A list of generated headlines for each topic.
                - topic_summary (list): A list of generated summaries for each topic.
            If topic segmentation is skipped, returns the original transcript and two empty lists.
        """
        if not self.topic_config:
            print('No topic segmentation configuration. Skipping topic segmentation')
            return transcript, [], []
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
        """
        Formats the processed transcript into plain text and Markdown.

        The formatted outputs are cached to files.

        Args:
            video_path (str): The file path to the video or audio file, used for caching.
            transcript (list): The final transcript data.
            nouns_list (Dict[str, List[Dict[str, Any]]]): A dictionary of extracted nouns/entities.
            topic_headlines (list): A list of topic headlines.
            topic_summary (list): A list of topic summaries.
        """

        transcript_formatted = format_transcript(video_path, transcript)
        transcript_markdown = format_markdown(video_path, transcript, nouns_list, topic_headlines, topic_summary)        


    def retrieve_json(self, video_path: str) -> str | None:
        """
        Retrieves the cached transcript with topic segmentation as a JSON string.

        This typically loads the '.topics' cached file.

        Args:
            video_path (str): The file path to the video or audio file, used to locate the cache.

        Returns:
            str | None: The JSON string content of the cached topics file, or None if not found.
        """
        path = get_cache_file(video_path, EXTENSION_TOPICS)        
        return load_text_file(path)

    def retrieve_markdown(self, video_path: str) -> Any | None:
        """
        Retrieves the cached transcript formatted as Markdown.

        This typically loads the '.md' cached file.

        Args:
            video_path (str): The file path to the video or audio file, used to locate the cache.

        Returns:
            Any | None: The content of the cached Markdown file (often a string),
                        or None if not found. The return type depends on `load_object_file`.
        """
        path = get_cache_file(video_path, EXTENSION_MARKDOWN)
        return load_text_file(path)
        
    def clear(self, video_path: str):
        """
        Clears all cached files associated with the given video path.

        Args:
            video_path (str): The file path to the video or audio file whose cache should be cleared.
        """
        return clear_cache_directory(video_path)
