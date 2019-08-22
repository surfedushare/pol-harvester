#!/usr/bin/env bash

# Parse input
INPUT_AUDIO="$BASE_DIR/$1"

# Set Kaldi paths
[ -f $KALDI_ROOT/tools/env.sh ] && . $KALDI_ROOT/tools/env.sh
export PATH=$PWD/utils/:$KALDI_ROOT/src/bin:$KALDI_ROOT/tools/openfst/bin:$KALDI_ROOT/tools/sctk/bin:$KALDI_ROOT/src/fstbin/:$KALDI_ROOT/src/gmmbin/:$KALDI_ROOT/src/featbin/:$KALDI_ROOT/src/lm/:$KALDI_ROOT/src/sgmmbin/:$KALDI_ROOT/src/sgmm2bin/:$KALDI_ROOT/src/fgmmbin/:$KALDI_ROOT/src/latbin/:$KALDI_ROOT/src/nnetbin:$KALDI_ROOT/src/nnet2bin/:$KALDI_ROOT/src/kwsbin:$KALDI_ROOT/src/online2bin/:$KALDI_ROOT/src/ivectorbin/:$KALDI_ROOT/src/lmbin/:$KALDI_ROOT/src/nnet3bin/:$PWD:$PATH
export LC_ALL=C

# Transcribe files
./decode.sh $INPUT_AUDIO $OUTPUT_PATH

# Check transcription success and exit on fail
STAGE=$(<$OUTPUT_PATH/intermediate/stage)
if [ "$STAGE" != "Done" ]; then
    echo "Stage: $STAGE"
    cat $OUTPUT_PATH/intermediate/log 1>&2
    exit 1
fi

# Pass results to stdout
echo "Stage: $STAGE"
echo "=== LOG ==="
cat $OUTPUT_PATH/intermediate/log
echo "=== END LOG ==="
echo "=== TRANSCRIPTION ==="
cat $OUTPUT_PATH/1Best.txt
echo "=== END TRANSCRIPTION ==="
echo "=== CONFIDENCES ==="
cat $OUTPUT_PATH/1Best.ctm
echo "=== END CONFIDENCES ==="
echo "=== SEGMENTATION ==="
for liumsegments in $OUTPUT_PATH/liumlog/*.seg; do
    cat $liumsegments
done
echo "=== END SEGMENTATION ==="

# Clean up
rm -r $OUTPUT_PATH
