# Use a imagem base do Python
FROM python:3.9

# Copie o código para o contêiner
COPY . /app

# Defina o diretório de trabalho
WORKDIR /app

# Instale as dependências
RUN pip install --no-cache-dir tqdm pillow

# Execute o script Python quando o contêiner for iniciado
CMD ["python", "dmc.py"]

