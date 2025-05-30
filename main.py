import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from PIL import Image, ImageDraw, ImageFont
import io
import random
import time
import threading
import asyncio
from datetime import datetime
from typing import Optional, Generator
import secrets

app = FastAPI()

security = HTTPBasic()

from fastapi.middleware.cors import CORSMiddleware

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos os domínios (ajuste conforme necessário)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Configurações globais
REQUEST_DELAY_SECONDS = 0  # Tempo de atraso (configurável)
OVERLOAD_PROBABILITY = 0.05  # Probabilidade de simular erro de sobrecarga (10%)
ERROR_PROBABILITY = 0.00  # Probabilidade de retornar um JPEG inválido (20%)
DUPLICATE_REQUEST_CHECK = {}  # Armazena controle de requisições duplicadas
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "adm")
    correct_password = secrets.compare_digest(credentials.password, "123")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Usuario ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"},
        )

# Função para gerar uma imagem aleatória
def generate_random_image(width=1920, height=1080):
    # Criação da imagem com fundo aleatório
    image = Image.new('RGB', (width, height), color=(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    ))

    # Adicionar texto de overlay
    draw = ImageDraw.Draw(image)
    text = "Imagem de Teste"
    font = ImageFont.load_default()  # Usando fonte padrão (sem necessidade de instalação)

    # Posição centralizada do texto
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]  # Largura do texto
    text_height = text_bbox[3] - text_bbox[1]  # Altura do texto
    position = ((width - text_width) // 2, (height - text_height) // 2)

    # Adicionar o texto à imagem
    draw.text(position, text, font=font, fill="white")

    return image

# Função para simular atraso configurado
def simulate_delay(delay: int):
    time.sleep(delay)

# Limpeza de entradas antigas
def cleanup_requests():
    """Remove requisições duplicadas antigas após 10 segundos"""
    now = datetime.now()
    for key in list(DUPLICATE_REQUEST_CHECK.keys()):
        last_request = datetime.strptime(DUPLICATE_REQUEST_CHECK[key], "%Y-%m-%d %H:%M:%S")
        if (now - last_request).seconds > 10:  # Limpeza após 10 segundos
            del DUPLICATE_REQUEST_CHECK[key]

# Função para carregar uma imagem aleatória da pasta 'imagem'
def load_random_image_from_folder(folder_path='imagem'):
    # Lista todos os arquivos na pasta
    files = os.listdir(folder_path)
    # Filtra apenas arquivos de imagem (opcional, dependendo do conteúdo da pasta)
    image_files = [f for f in files if f.endswith(('.png', '.jpg', '.jpeg'))]
    # Escolhe um arquivo de imagem aleatoriamente
    random_image_file = random.choice(image_files)
    # Carrega a imagem
    image_path = os.path.join(folder_path, random_image_file)
    image = Image.open(image_path)
    return image

# Endpoint para servir a imagem
@app.get("/ISAPI/Streaming/channels/0/picture")
@app.get("/ISAPI/Streaming/channels/1/picture")
@app.get("/ISAPI/Streaming/channels/2/picture")
@app.get("/api/snapshot.cgi")
async def serve_image(
    request: Request,
    delay: Optional[int] = REQUEST_DELAY_SECONDS,
    random_image: Optional[bool] = False,
    credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    global DUPLICATE_REQUEST_CHECK

    # Simula atraso configurado
    if delay > 0:
        simulate_delay(delay)

    # Simula erro de sobrecarga (503)
    if random.random() < OVERLOAD_PROBABILITY:
        raise HTTPException(status_code=503, detail="Server overload, try again later")

    # Gera identificador único usando IP + data/hora
    request_ip = request.client.host
    request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Data/hora formatada
    request_id = f"{request_ip}_{request_time}"

    #  Checa requisições duplicadas
    if request_ip in DUPLICATE_REQUEST_CHECK:
        last_request_time = DUPLICATE_REQUEST_CHECK[request_ip]
        # Se a requisição ocorrer no mesmo segundo, trata como duplicada
        if last_request_time == request_time:
            raise HTTPException(status_code=429, detail="Duplicate request detected")

    DUPLICATE_REQUEST_CHECK[request_ip] = request_time

    # Remove entradas antigas após um tempo (limpeza em segundo plano)
    threading.Thread(target=cleanup_requests).start()

    # Simula um JPEG inválido com base em uma probabilidade
    if random.random() < ERROR_PROBABILITY:
        img_io = io.BytesIO(b"")  # JPEG inválido (2 bytes)
        print(f"JPEG inválido gerado para {request_ip}")
        return StreamingResponse(img_io, media_type="image/jpeg")

    # Gera a imagem
    if random_image:
        image = generate_random_image()
    else:
        image = load_random_image_from_folder()
    img_io = io.BytesIO()
    image.save(img_io, 'JPEG')
    img_io.seek(0)

    return StreamingResponse(img_io, media_type='image/jpeg')

VIDEO_FILE_PATH = './video/video.mp4'

def get_video_stream() -> Generator[bytes, None, None]:
    """Gera um stream contínuo do vídeo em loop"""
    chunk_size = 1024 * 1024  # 1MB por chunk

    if not os.path.exists(VIDEO_FILE_PATH):
        raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {VIDEO_FILE_PATH}")

    while True:  # Loop infinito para repetir o vídeo
        try:
            with open(VIDEO_FILE_PATH, 'rb') as video_file:
                while chunk := video_file.read(chunk_size):
                    yield chunk
        except Exception as e:
            print(f"Erro ao acessar o arquivo de vídeo: {e}")
            break
        print(f"Reiniciando o vídeo: {VIDEO_FILE_PATH}")
        time.sleep(0.5)  # Pequena pausa antes de reiniciar o vídeo (opcional)

@app.get("/Streaming/channels/102/httppreview")
async def stream_video():
    """
    Endpoint que simula streaming de vídeo em loop contínuo
    Acesse via: http://172.10.1.78:8890/Streaming/channels/101/httppreview
    """
    return StreamingResponse(
        get_video_stream(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": f"inline; filename={os.path.basename(VIDEO_FILE_PATH)}",
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache",
        }
    )

@app.get("/Streaming/channels/101/httppreview")
async def stream_video(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Endpoint que simula streaming de vídeo MJPEG
    Acesse via: http://172.10.1.78:8890/Streaming/channels/101/httppreview
    """

    async def mjpeg_generator():
        # Cabeçalho MJPEG
        boundary = "mjpegboundary"
        yield f"--{boundary}\r\n".encode()

        # Loop para simular frames do vídeo
        while True:
            try:
                # Carrega uma imagem aleatória da pasta para simular um frame do vídeo
                image = load_random_image_from_folder()

                # Converte para JPEG e para bytes
                img_io = io.BytesIO()
                image.save(img_io, format='JPEG')
                img_bytes = img_io.getvalue()

                # Monta o frame MJPEG
                content = (
                    f"Content-Type: image/jpeg\r\n"
                    f"Content-Length: {len(img_bytes)}\r\n\r\n"
                ).encode()

                yield content
                yield img_bytes
                yield f"\r\n--{boundary}\r\n".encode()

                # Controla o framerate (ajuste conforme necessário)
                await asyncio.sleep(0.1)  # ~10 FPS

            except Exception as e:
                print(f"Erro ao gerar frame MJPEG: {e}")
                await asyncio.sleep(1)

    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=mjpegboundary",
        headers={
            "Cache-Control": "no-cache"
        }
    )


@app.get("/")
async def root():
    """
    Endpoint raiz que retorna informações básicas sobre o simulador
    """
    return {
        "aplicação": "Simulador Hikvision",
        "versão": "1.6",
        "endpoints_disponíveis": [
            "/ISAPI/Streaming/channels/{0,1,2}/picture",
            "/api/snapshot.cgi",
            "/Streaming/channels/101/httppreview",
            "/Streaming/channels/102/httppreview"
        ]
    }