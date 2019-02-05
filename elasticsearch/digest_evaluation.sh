#!/bin/bash
INDEX=$1
echo "DCG"
cat ${INDEX}_dcg.json | jq '.metric_score'
echo "expected reciprocal rank"
cat ${INDEX}_expected_reciprocal_rank.json | jq '.metric_score'
echo "mean_reciprocal_rank"
cat ${INDEX}_mean_reciprocal_rank.json | jq '.metric_score'
echo "precision"
cat ${INDEX}_precision.json | jq '.metric_score'
