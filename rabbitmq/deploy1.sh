#!/bin/bash

set -a
source .env
set +a

# Явно экспортируем переменные vault для vals
export VAULT_ADDR=${VAULT_ADDR:-http://vault.localhost}
export VAULT_TOKEN=${VAULT_TOKEN}

# Расшифровываем values.yaml через vals и передаем в helm
vals eval -f values.yaml | helm upgrade --install \
     my-rabbitmq oci://registry-1.docker.io/cloudpirates/rabbitmq \
     -n rabbitmq --create-namespace \
     -f -