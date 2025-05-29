## Introduction

A video/audio transcript service implementating the algorithm described on this thread:

https://www.reddit.com/r/LocalLLaMA/comments/1g2vhy3/creating_very_highquality_transcripts_with/

## The algorithm

Transcription is performed by a series of transformation steps. Details are available in the [Algorithm](Planning.md) document.


## Usage

## Setup

Setup you environment. Use the supplied script to use on the command line
```
export HF_TOKEN=<HF_TOKEN>
export OLLAMA_HOST=<OLLAMA_HOST>
```

## ingestion.py CLI tool

```
python ingestion.py /mnt/data3/AI/software/VideoRAG/Lexington/DPa2iRgzadM.wav
```

Results are stored in

```
/mnt/data3/AI/software/VideoRAG/Lexington/DPa2iRgzadM.d
```

Primarily cache.md

## You Tube

YouTube viodeos can be do be downloaded using the yt-dlp package as follows

```
pip install yt-dlp
yt-dlp -o "%(id)s.%(ext)s" -S "res:720" https://www.youtube.com/live/FpC_Lp_Kq_0  -P .
ffmpeg -i file.mkv -q:a 0 -map a audio_output.wav
```

## Package


### Setup treeseg configuration

More information is available on the (topic-treeseg repo)[https://github.com/geraldthewes/topic-treeseg.git]

```
from treeseg import Embeddings, ollama_embeddings

# Build config
# Configuration
embeddings_config = Embeddings(
    embeddings_func=ollama_embeddings, # openai_embeddings
    headers={}, # forOpenAI
    model="nomic-embed-text",  # or "text-embedding-ada-002" for openai         
    endpoint=os.getenv("OLLAMA_HOST", "")   # "https://api.openai.com/v1/embeddings"
)
config = {
    "MIN_SEGMENT_SIZE": 10,
    "LAMBDA_BALANCE": 0,
    "UTTERANCE_EXPANSION_WIDTH": 3,
    "EMBEDDINGS": embeddings_config,
    "TEXT_KEY": "transcript"
}
```

### Create VideoTranscriber instance

```
   transcriber = VideoTranscriber(config)
```

### Transcribe

```
    result, nouns_list = transcriber.transcribe_video(video_path)
    result, headlines, summary = transcriber.topics(video_path, result, max_topics) 
    transcriber.format_transcript(video_path, result, nouns_list, headlines, summary)
```

max_topics sets the maximum topics you want the topic segmenter to create. The longer the video, the more topic can be discussed.

## Reference API

Read the reference [API](api/mst.md)


## Appendix - Obsolete sections

The code below is old and will probably be removed.

### Sentence merging

```
python -m spacy download en_core_web_sm
python merge_transcript_segments.py   /mnt/data3/AI/data/Needham/2024-10-24.d/cache.raw_transcript /mnt/data3/AI/data/Needham/2024-10-24.d/cache.sentence_merge
```


### Topic segmentation

```
python  topic_segment.py --transcript-file   /mnt/data3/AI/data/Needham/2024-10-24.d/cache.final --output-file=/mnt/data3/AI/data/Needham/2024-10-24.d/cache.topics --segments=512
```

