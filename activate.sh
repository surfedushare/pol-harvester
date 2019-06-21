#!/usr/bin/env bash

export $(cat .env | xargs)
source activate surf-harvester
