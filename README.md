# hikvision-capture-emulation

## Descrição
Este projeto é um simulador para captura de imagens de câmeras HIKVISION e PUMATRONIC. Ele utiliza URLs de captura para retornar imagens no formato MJPEG, permitindo a emulação de dispositivos de captura de vídeo.

## Funcionalidades
- Simulação de endpoints de captura de imagens.
- Geração de imagens aleatórias com texto sobreposto.
- Carregamento de imagens aleatórias de uma pasta específica.
- Suporte a autenticação básica (HTTP Basic Authentication).
- Configuração de atrasos simulados nas respostas.
- Simulação de erros de sobrecarga do servidor (HTTP 503).
- Detecção e bloqueio de requisições duplicadas.
- Possibilidade de gerar imagens inválidas para testes.

## Requisitos
- Python 3.8 ou superior.
- Dependências listadas no arquivo `requirements.txt`.

## Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/hikvision-capture-emulation.git
   cd hikvision-capture-emulation