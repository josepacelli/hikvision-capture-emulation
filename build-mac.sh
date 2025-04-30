docker buildx build --pull --no-cache --platform linux/arm64 \
  -t atlantatecnologia/at-captura-simulador:arm64 \
  --push .