#!/bin/bash

set -a
source .env
set +a

helm secrets --evaluate-templates -b vals upgrade --install foodgram app \
  -n foodgram \
  -f app/values.yaml