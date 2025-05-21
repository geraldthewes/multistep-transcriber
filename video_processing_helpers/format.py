import os
import json
import torch
import logging
import traceback
import re
from typing import List, Dict, Any

from .caching import cached_file, cached_file_object


@cached_file('.formatted')
def format_transcript(video_path: str, transcripts: str) -> str:
    """Format final transcript as Markdown"""
    try:
        formatted = "# Transcribed Video\n\n"
        # This is a simplified formatting - enhance as needed
        for entry in transcripts:
            speaker = entry['speaker_name']
            transcript = entry['transcript']
            formatted += f"{speaker}:{transcript}\n"
        return formatted
    except Exception as e:
        print(f"Error formatting transcript: {e}")
        return transcript

def _create_anchor_link(subheading):
    # Remove non-word characters except spaces and hyphens
    cleaned = re.sub(r'[^\w\s-]', '', subheading)
    # Collapse multiple spaces into a single space
    collapsed_spaces = re.sub(r'\s+', ' ', cleaned.strip())
    # Convert to lowercase and replace spaces with hyphens
    anchor_link = collapsed_spaces.lower().replace(" ", "-")
    return anchor_link

    
@cached_file('.md')
def format_markdown(video_path: str,
                    transcripts: List[Dict[str, Any]],
                    nouns_list: Dict[str, List[Dict[str, Any]]],
                    topic_headlines: list,
                    topic_summary: list) -> str:
    """Formats the final transcript as Markdown."""
    try:
        formatted = "# Transcribed Video\n\n"
        current_topic = None

        ''' TOC '''
        formatted += "# Table of Content\n"        
        for entry in transcripts:
            topic = entry.get('topic', None) 

            if topic != current_topic:
                start = entry.get('start')
                headline = topic_headlines[topic]
                headline_anchor = _create_anchor_link(headline)
                formatted += f"\n- [{headline}](#{headline_anchor})   ({start})\n\n"
                current_topic = topic
                summary = topic_summary[topic]                
                formatted += f"\t{summary}\n"
        
        formatted += "\n# Transcript\n"        
        current_speaker = None        
        ''' Transcript '''
        for entry in transcripts:
            speaker = entry.get('speaker_name', 'UNKNOWN') # Use .get for safety
            topic = entry.get('topic', None) 
            transcript_text = entry.get('transcript', '[TRANSCRIPT MISSING]')

            # Add speaker heading only when the topic changes
            if topic != current_topic:
                start = entry.get('start')
                headline = topic_headlines[topic]
                formatted += f"\n\n## {headline}\n"
                current_topic = topic
                formatted += f"### {speaker} ({start})\n"                
            
            # Add speaker heading only when the speaker changes
            if speaker != current_speaker:
                start = entry.get('start')                
                formatted += f"\n### {speaker} ({start})\n"
                current_speaker = speaker

            # Add the transcript text, indented slightly
            formatted += f"- {transcript_text}\n"

        formatted += f'\n#Appendix: List of Entities\n'
        for label in nouns_list:
            formatted += f'### {label}\n'
            for noun in nouns_list[label]:
                formatted += f"- {noun['text']}\n"
        
        return formatted
    except Exception as e:
        print(f"Error formatting transcript: {e}")
        # Attempt to return a basic representation even on error
        return json.dumps(transcripts, indent=2)
