#!/bin/bash

set -a
source .env
set +a

vals eval -f app/values.yaml | helm upgrade --install foodgram app \
  -n foodgram \
  -f -
