# Usar a imagem base do Python 3.9
FROM python:3.12-alpine

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o arquivo requirements.txt para o container
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação para o container
COPY main.py main.py
COPY imagem/ imagem/
COPY video/ video/
COPY requirements.txt requirements.txt

# Expor a porta padrão do Uvicorn
EXPOSE 8005

# Comando para iniciar o servidor FastAPI com Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]