# Introdiuction

This project implements a video transcriping workflow in a python using a mix of LLM and specialized AI models

# Overall workflow

The workflow was inspired from this post on reddit: https://www.reddit.com/r/LocalLLaMA/comments/1g2vhy3/creating_very_highquality_transcripts_with/

It currently consists of


1. Initial Transcription

  - Use a state of the art  open-source model transcription model such as whisper or equivalent, for the first pass.
  - We run it locally. You get a raw transcript.
  - There are many cool open source libraries that you can just plug in and it should work (whisperx, etc.)
  - The transcript consists of an array of transcript chunks in JSON that contains start and end time in seconds from start and the transcribed text
  
```
   {
        "start": 49.84,
        "end": 55.040000000000006,
        "transcript": " please recite the Pledge of Allegiance. I pledge a"
    },
```

2. Sentence merging 
  Reassemble transcripted chunks into complete sentences
  - Use a state of the art sentence merge model such as provide by Spacy
  - Attempt to keep timestamps
  
  

3. Entity Extraction

  -This step is important. Basically the problem is the raw transcript above will have mostly likely have the nouns and special (technical) terms wrong. You need to correct that. But before that you need to collect this special words? How...?

 - Use structured API responses from open-source LLMs (like Outlines) or specialized models to extract a list of nouns from a master document. If you don't want to use open-source tools here, almost all commerical APIs offer structure API response too. You can use that too.

  - In our case, for our podcast, we maintain a master document per episode that is basically like a script (for different uses) that contains all proper nouns, special technial terms and such? How do we extract that.

  - We just simply dump that into a LLM (with a structured generation) and it give back an proper array list of special words that we need to keep an eye on.

  - Prompt: "Extract all proper nouns, technical terms, and important concepts from this text. Return as a JSON list." with Structure Generation. Something like that...

4. Transcript Correction

   - Feed the initial transcript and extracted noun list to your LLM.

    - Prompt: "Correct this transcript, paying special attention to the proper nouns and terms in the provided list. Ensure proper punctuation and formatting." (That is not the real prompt, but you get the idea...)

   - Input: Raw transcript + noun list

   - Output: Cleaned-up transcript

5. Speaker Identification

   - Use pyannote.audio (open source!) for speaker diarization.

   - Bonus: Prompt your LLM to map speaker labels to actual names based on context.

6. Topic segmentation
 
   - As LLM have a harder time with longer text, break the transcript into topics using a state of the art topic segmntation model such as TreeSeg

7. Final Formatting

   - Use a simple script to format the transcript into your desired output (e.g., Markdown -> With speaker labels and timing if you want). And just publish.
