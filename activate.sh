#!/usr/bin/env bash


# Load environment variables similar to how docker-compose does it
export $(cat .env | xargs)

# Either activate a conda environment (typically local) or activate a pip venv (typically dev server)
if [ -x "$(command -v conda)" ]
then
    conda activate surf-harvester;
elif [ -d venv ]
then
    source venv/bin/activate
fi
