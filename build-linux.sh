#!/bin/bash
docker buildx create --use --name mybuilder
docker buildx inspect mybuilder --bootstrap
docker buildx build --pull --no-cache --platform linux/amd64,linux/arm64 \
  -f Dockerfile \
  -t atlantatecnologia/at-captura-simulador:latest \
  -t atlantatecnologia/at-captura-simulador:arm64 \
  --push .
