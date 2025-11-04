#!/bin/sh

# Install basic packages
pip install ffmpeg==7.0.1
pip install torch==2.8.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
pip install torchcodec==0.7.0 --no-cache-dir
# GPU
#pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# Other Packages
pip install -r requirements.txt
pip install git+https://github.com/geraldthewes/topic-treeseg.git

# Install Spacy model
python -m spacy download en_core_web_sm
