#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create a bin directory for ffmpeg if it doesn't exist
mkdir -p bin

# Download static ffmpeg if not present
if [ ! -f bin/ffmpeg ]; then
    echo "Downloading ffmpeg..."
    # Download static build for Linux amd64 (standard for Render)
    curl -L https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/linux-x64.tar.gz | tar xz -C bin --strip-components=1
    chmod +x bin/ffmpeg
    echo "ffmpeg installed to bin/ffmpeg"
else
    echo "ffmpeg already exists in bin/ffmpeg"
fi
