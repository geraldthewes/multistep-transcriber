#!/bin/sh

# Install ffmpeg (needs to be <= v7) and qwen code
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt update
sudo apt install -y ffmpeg nodejs
sudo npm install -g @qwen-code/qwen-code@latest
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install basic packages
pip install torch==2.8.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
pip install torchcodec==0.7.0 --no-cache-dir
# GPU
#pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# Other Packages
pip install -r requirements.txt
pip install git+https://github.com/geraldthewes/topic-treeseg.git

# Install Spacy model
python -m spacy download en_core_web_sm
