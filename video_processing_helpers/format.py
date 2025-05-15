import os
import json
import torch
import logging
import traceback
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

@cached_file('.md')
def format_markdown(video_path: str, transcripts: List[Dict[str, Any]], nouns_list: Dict[str, List[Dict[str, Any]]]) -> str:
    """Formats the final transcript as Markdown."""
    try:
        formatted = "# Transcribed Video\n\n"
        current_speaker = None
        current_topic = None
        for entry in transcripts:
            speaker = entry.get('speaker_name', 'UNKNOWN') # Use .get for safety
            topic = entry.get('topic', None) 
            transcript_text = entry.get('transcript', '[TRANSCRIPT MISSING]')

            # Add speaker heading only when the topic changes
            if topic != current_topic:
                formatted += f"\n\n## Topic {topic}:\n"
                current_topic = topic
                start = entry.get('start')
                formatted += f"Time:{start}\n"
                formatted += f"### {speaker}:\n"                
            
            # Add speaker heading only when the speaker changes
            if speaker != current_speaker:
                formatted += f"\n### {speaker}:\n"
                current_speaker = speaker

            # Add the transcript text, indented slightly
            formatted += f"- {transcript_text}\n"

        formatted += f'\n## Entities mentionned in this meeting transcript'
        for label in nouns_list:
            formatted += f'### {label}\n'
            for noun in nouns_list[label]:
                formatted += f"- {noun['text']}\n"
        
        return formatted
    except Exception as e:
        print(f"Error formatting transcript: {e}")
        # Attempt to return a basic representation even on error
        return json.dumps(transcripts, indent=2)
