'''
Break transcript into segments
'''

import os, sys
import json
import argparse


from treeseg import TreeSeg, Embeddings, ollama_embeddings

# Configuration
embeddings_config = Embeddings(
            embeddings_func = ollama_embeddings, # openai_embeddings
            headers = {}, # forOpenAI
            model =  "nomic-embed-text",  # or "text-embedding-ada-002" for openai         
            endpoint = os.getenv("OLLAMA_HOST","")   # "https://api.openai.com/v1/embeddings"
)

config =   {
        "MIN_SEGMENT_SIZE": 5,
        "LAMBDA_BALANCE": 0,
        "UTTERANCE_EXPANSION_WIDTH": 2,
        "EMBEDDINGS": embeddings_config,
        "TEXT_KEY": "transcript"
    }


# Parse command-line arguments
parser = argparse.ArgumentParser(description='Break transcript into segments')
parser.add_argument('--transcript-file', type=str, required=True, 
                   help='Path to JSON file containing the transcript')
args = parser.parse_args()

# Load transcript from JSON file
try:
    with open(args.transcript_file, 'r') as f:
        transcript = json.load(f)
except FileNotFoundError:
    print(f"Error: Transcript file '{args.transcript_file}' not found")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Invalid JSON format in '{args.transcript_file}'")
    sys.exit(1)



segmenter = TreeSeg(configs=config, entries=transcript)

segments = segmenter.segment_meeting(20)

print(segments)


def update_transcript_with_topics(transcript, topic_transitions):
    """
    Updates transcript entries with topic numbers based on topic transitions.
    
    Args:
        transcript: List of transcript entry dictionaries
        topic_transitions: List of 0s and 1s indicating topic continuation (0) or new topic (1)
    
    Returns:
        Updated transcript with topic field added to each entry
    """
    if len(transcript) != len(topic_transitions):
        raise ValueError("Length of transcript and topic_transitions must match")
    
    current_topic = 0
    for i, (entry, transition) in enumerate(zip(transcript, topic_transitions)):
        if transition == 1:
            current_topic += 1
        entry['topic'] = current_topic
    
    return transcript


transcript_w_topics = update_transcript_with_topics(transcript, segments)

print(transcript_w_topics)


with open("out.json", 'w') as f:
    json.dump(transcript_w_topics, f, indent=4)
