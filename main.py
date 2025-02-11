import os

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.exceptions import HTTPException
from PIL import Image, ImageDraw, ImageFont
import io
import random
import time
import threading
from datetime import datetime
from typing import Optional

app = FastAPI()

# Configurações globais
REQUEST_DELAY_SECONDS = 0  # Tempo de atraso (configurável)
OVERLOAD_PROBABILITY = 0.00  # Probabilidade de simular erro de sobrecarga (10%)
ERROR_PROBABILITY = 0.00  # Probabilidade de retornar um JPEG inválido (20%)
DUPLICATE_REQUEST_CHECK = {}  # Armazena controle de requisições duplicadas
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

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
async def serve_image(request: Request, delay: Optional[int] = REQUEST_DELAY_SECONDS, random_image: Optional[bool] = False):
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

    # Checa requisições duplicadas
    # if request_ip in DUPLICATE_REQUEST_CHECK:
    #     last_request_time = DUPLICATE_REQUEST_CHECK[request_ip]
    #     # Se a requisição ocorrer no mesmo segundo, trata como duplicada
    #     if last_request_time == request_time:
    #         raise HTTPException(status_code=429, detail="Duplicate request detected")
    #
    # DUPLICATE_REQUEST_CHECK[request_ip] = request_time

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