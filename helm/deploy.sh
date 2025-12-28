#!/bin/bash

set -a
source .env
set +a

helm secrets upgrade --install foodgram app \
  -n foodgram \
  -f app/values.yaml