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
