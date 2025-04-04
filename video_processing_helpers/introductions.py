import os
import json
import torch
import logging
import traceback
from typing import List, Dict, Any
from setfit import SetFitModel

from .caching import cached_file_object

@cached_file_object('.introductions')
def find_introductions(video_path: str, transcripts):
    ''' Identify segments that are speaker introductions using a trained setfit model '''
    try:
        intro_sentences = []
        imodel = SetFitModel.from_pretrained("gerald29/setfit-bge-small-v1.5-sst2-8-shot-introduction")         
        sentences = [item['transcript'] for item in transcripts]
        labels = imodel.predict(sentences)
        # Filter the transcripts where the corresponding label is 'introduction'
        filtered_transcripts = [transcript for transcript, label in zip(transcripts, labels) if label == 'introduction']
        return filtered_transcripts
    except Exception as e:
         print(f"Error extracting speaker introductions: {e}")
         return None
