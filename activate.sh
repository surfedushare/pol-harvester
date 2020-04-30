#!/usr/bin/env bash


# Setup shell environment inside containers
# Docker Compose may have created a mount directory, which we don't want
if [ -d "shell/.bash_history" ]; then rm -rf "shell/.bash_history"; fi
touch shell/.bash_history

# Load environment variables similar to how docker-compose does it
export $(cat .env | xargs)

# Either activate a conda environment (typically local) or activate a pip venv (typically dev server)
if [ "$(command -v conda)" ]
then
    conda activate surf-harvester;
elif [ -d venv ]
then
    source venv/bin/activate
fi
