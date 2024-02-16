# Organizador de Imagens

Este é um script Python que organiza imagens em pastas com base em suas datas de criação, otimiza as imagens e adiciona metadados como data de criação e autor.

## Como usar

### Com `docker run`

`docker run -u $(id -u):$(id -g) -v $(pwd)/temp:/app/temp -v $(pwd)/organizado:/app/organizado dmc-organize`

