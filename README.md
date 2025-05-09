## Introduction

An implementation of the following algorith described on this thread:

https://www.reddit.com/r/LocalLLaMA/comments/1g2vhy3/creating_very_highquality_transcripts_with/

### The Solution: A 100% Automated, Open-Source Workflow
... a fully automated workflow powered by LLMs and transcription models. 

Here's how it works:

#### Initial Transcription

Use latest whisper-turbo, an open-source model, for the first pass.

We run it locally. You get a raw transcript.

There are many cool open source libraries that you can just plug in and it should work (whisperx, etc.)

#### Noun Extraction

This step is important. Basically the problem is the raw transcript above will have mostly likely have the nouns and special (technical) terms wrong. You need to correct that. But before that you need to collect this special words? How...?

Use structured API responses from open-source LLMs (like Outlines) to extract a list of nouns from a master document. If you don't want to use open-source tools here, almost all commerical APIs offer structure API response too. You can use that too.

In our case, for our podcast, we maintain a master document per episode that is basically like a script (for different uses) that contains all proper nouns, special technial terms and such? How do we extract that.

We just simply dump that into a LLM (with a structured generation) and it give back an proper array list of special words that we need to keep an eye on.

Prompt: "Extract all proper nouns, technical terms, and important concepts from this text. Return as a JSON list." with Structure Generation. Something like that...

#### Transcript Correction

Feed the initial transcript and extracted noun list to your LLM.

Prompt: "Correct this transcript, paying special attention to the proper nouns and terms in the provided list. Ensure proper punctuation and formatting." (That is not the real prompt, but you get the idea...)

Input: Raw transcript + noun list

Output: Cleaned-up transcript

#### Speaker Identification

Use pyannote.audio (open source!) for speaker diarization.

Bonus: Prompt your LLM to map speaker labels to actual names based on context.

#### Final Formatting

Use a simple script to format the transcript into your desired output (e.g., Markdown, HTML -> With speaker labels and timing if you want). And just publish.

### Why This Approach is Superior
Complete Control: By owning the stack, we can customize every step of the process.

Flexibility: We can easily add features like highlighting mentioned books or papers in transcript.

Cost-Effective: After initial setup, running costs are minimal -> Basically GPU hosting or electricity cost.

Continuous Improvement: We can fine-tune models on our specific content for better accuracy over time.


## Installation

```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
pip install -r requirements.txt
```

## Usage

```
export HF_TOKEN=
export OLLAMA_HOST=
python ingestion.py /mnt/data3/AI/software/VideoRAG/Lexington/DPa2iRgzadM.wav
```

## You Tube

YouTube viodeos can be do be downalod as follows

```
yt-dlp -o "%(id)s.%(ext)s" -S "res:720" https://www.youtube.com/live/FpC_Lp_Kq_0  -P .
ffmpeg -i file.mkv -q:a 0 -map a audio_output.wav
```

### Sentence merging

```
python -m spacy download en_core_web_sm
python merge_transcript_segments.py   /mnt/data3/AI/data/Needham/2024-10-24.d/cache.raw_transcript /mnt/data3/AI/data/Needham/2024-10-24.d/cache.sentence_merge
```


### Topic segmentation

```
python  topic_segment.py --transcript-file   /mnt/data3/AI/data/Needham/2024-10-24.d/cache.final --output-file=/mnt/data3/AI/data/Needham/2024-10-24.d/cache.topics --segments=512
```
### Unit Tests

```
python -m unittest test_transcriber.py
```
