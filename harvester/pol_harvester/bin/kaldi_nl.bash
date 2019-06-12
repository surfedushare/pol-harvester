#!/usr/bin/env bash

# Parse input
INPUT_AUDIO="$BASE_DIR/$1"

# Set Kaldi paths
[ -f $KALDI_ROOT/tools/env.sh ] && . $KALDI_ROOT/tools/env.sh
export PATH=$PWD/utils/:$KALDI_ROOT/src/bin:$KALDI_ROOT/tools/openfst/bin:$KALDI_ROOT/tools/sctk/bin:$KALDI_ROOT/src/fstbin/:$KALDI_ROOT/src/gmmbin/:$KALDI_ROOT/src/featbin/:$KALDI_ROOT/src/lm/:$KALDI_ROOT/src/sgmmbin/:$KALDI_ROOT/src/sgmm2bin/:$KALDI_ROOT/src/fgmmbin/:$KALDI_ROOT/src/latbin/:$KALDI_ROOT/src/nnetbin:$KALDI_ROOT/src/nnet2bin/:$KALDI_ROOT/src/kwsbin:$KALDI_ROOT/src/online2bin/:$KALDI_ROOT/src/ivectorbin/:$KALDI_ROOT/src/lmbin/:$KALDI_ROOT/src/nnet3bin/:$PWD:$PATH
export LC_ALL=C

# Transcribe files
./decode.sh $INPUT_AUDIO $OUTPUT_PATH

# Fail if there were no transcripts
if [! -f "$OUTPUT_PATH/1Best.txt"]; then
    exit 1
fi

# Pass results to stdout
echo "=== TRANSCRIPTION ==="
cat $OUTPUT_PATH/1Best.txt
echo "=== END TRANSCRIPTION ==="

# Clean up
rm -r $OUTPUT_PATH
