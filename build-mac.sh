docker buildx build --pull --no-cache --platform linux/arm64 \
  -t atlantatecnologia/at-balanca-haenni-simulador:latest \
  --push .