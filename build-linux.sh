docker buildx build --pull --no-cache --platform linux/amd64 \
  -t atlantatecnologia/at-captura-simulador:latest \
  --push .



#docker buildx build --pull --no-cache --platform linux/amd64,linux/arm64 \
#  -t atlantatecnologia/at-video-rtsp-simulador:latest \
#  -f Dockerfile.vlc \
#  --push .
