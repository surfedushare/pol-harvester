#!/usr/bin/env bash

export $(cat .env | xargs)
conda activate surf-harvester
