<!-- markdownlint-disable -->

# API Overview

## Modules

- [`steps`](./steps.md#module-steps)
- [`steps.caching`](./steps.caching.md#module-stepscaching)
- [`steps.diarization`](./steps.diarization.md#module-stepsdiarization)
- [`steps.entities`](./steps.entities.md#module-stepsentities)
- [`steps.format`](./steps.format.md#module-stepsformat)
- [`steps.helpers`](./steps.helpers.md#module-stepshelpers)
- [`steps.introductions`](./steps.introductions.md#module-stepsintroductions)
- [`steps.merge_sentences`](./steps.merge_sentences.md#module-stepsmerge_sentences)
- [`steps.models`](./steps.models.md#module-stepsmodels)
- [`steps.standardize`](./steps.standardize.md#module-stepsstandardize)
- [`steps.topic_segmentation`](./steps.topic_segmentation.md#module-stepstopic_segmentation)
- [`steps.transcription`](./steps.transcription.md#module-stepstranscription)

## Classes

- [`VideoTranscriber`](./mst.VideoTranscriber.md#class-videotranscriber): Main class for end-to-end video transcription pipeline.
- [`models.CorrectedText`](./steps.models.md#class-correctedtext)
- [`models.NounList`](./steps.models.md#class-nounlist)
- [`models.Speaker_Mapping`](./steps.models.md#class-speaker_mapping)

## Functions

- [`caching.cached_file`](./steps.caching.md#function-cached_file): A decorator that caches the output of a function to a file.
- [`caching.cached_file_object`](./steps.caching.md#function-cached_file_object): A decorator that caches the output of a function returning a JSON-serializable object to a file.
- [`caching.clear_cache_directory`](./steps.caching.md#function-clear_cache_directory): Clears all files from the cache directory associated with the video_path.
- [`caching.get_cache_directory`](./steps.caching.md#function-get_cache_directory)
- [`caching.get_cache_file`](./steps.caching.md#function-get_cache_file)
- [`caching.load_object_file`](./steps.caching.md#function-load_object_file)
- [`caching.load_text_file`](./steps.caching.md#function-load_text_file)
- [`diarization.get_diarization_pipeline`](./steps.diarization.md#function-get_diarization_pipeline): Gets or initializes the pyannote diarization pipeline.
- [`entities.extract_entities`](./steps.entities.md#function-extract_entities): Extract proper nouns and technical terms from the transcript in batches
- [`entities.extract_persons`](./steps.entities.md#function-extract_persons): Extracts person names from introductions.
- [`entities.get_entity_model`](./steps.entities.md#function-get_entity_model): Gets or initializes the GLiNER entity model.
- [`entities.group_by_label`](./steps.entities.md#function-group_by_label): Groups extracted entities by their labels.
- [`entities.merge_duplicate_texts`](./steps.entities.md#function-merge_duplicate_texts): Merges duplicate entity texts, keeping the one with the highest score.
- [`entities.merge_similar_texts`](./steps.entities.md#function-merge_similar_texts): Merges similar entity texts using AI to select canonical spellings.
- [`helpers.flatten_texts`](./steps.helpers.md#function-flatten_texts): Flattens a dictionary of texts into a simple list.
- [`introductions.map_entities_to_speakers`](./steps.introductions.md#function-map_entities_to_speakers): Maps entities (especially persons) from NER data to speakers from diarization data
- [`introductions.speaker_to_name`](./steps.introductions.md#function-speaker_to_name)
- [`standardize.get_noun_correction_model`](./steps.standardize.md#function-get_noun_correction_model): Gets or initializes the sentence transformer model for noun standardization.
- [`standardize.standardize_nouns_ai`](./steps.standardize.md#function-standardize_nouns_ai): Standardizes nouns using AI-based phonetic similarity via embeddings, preserving line feeds.
- [`topic_segmentation.update_transcript_with_topics`](./steps.topic_segmentation.md#function-update_transcript_with_topics): Updates transcript entries with topic numbers based on topic transitions.
- [`transcription.get_whisper_model`](./steps.transcription.md#function-get_whisper_model): Gets or initializes the Whisper model.
