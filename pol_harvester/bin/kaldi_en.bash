#!/usr/bin/env bash

# Parse input
INPUT_AUDIO=$1

# Set Kaldi command (cmd.sh)
export train_cmd="queue.pl"
export decode_cmd="queue.pl --mem 4G"
export mkgraph_cmd="queue.pl --mem 8G"

# Set Kaldi paths (path.sh)
export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$PWD:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file $KALDI_ROOT/tools/config/common_path.sh is not present -> Exit!" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh
export PATH=$KALDI_ROOT/tools/sctk/bin:$PATH
export LC_ALL=C

# Transcribe files
online2-wav-nnet3-latgen-faster \
    --online=false \
    --do-endpointing=false \
    --frame-subsampling-factor=3 \
    --config=exp/tdnn_7b_chain_online/conf/online.conf \
    --max-active=7000 \
    --beam=15.0 \
    --lattice-beam=6.0 \
    --acoustic-scale=1.0 \
    --word-symbol-table=exp/tdnn_7b_chain_online/graph_pp/words.txt \
    exp/tdnn_7b_chain_online/final.mdl \
    exp/tdnn_7b_chain_online/graph_pp/HCLG.fst \
    'ark:echo utterance-id1 utterance-id1|' \
    "scp:echo utterance-id1 $INPUT_AUDIO |" \
    'ark:/dev/null'
