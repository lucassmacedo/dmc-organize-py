import os
from datetime import datetime
from PIL import Image
from tqdm import tqdm  # Importa a função tqdm para a barra de progresso
from ttkbootstrap import Style  # Importa o estilo do ttkbootstrap


# Constantes
folder_from = "./temp/"
folder_to = "./organizado/"
autor = "Lucas Macedo"
meses = {
    "01": "01_janeiro",
    "02": "02_fevereiro",
    "03": "03_marco",
    "04": "04_abril",
    "05": "05_maio",
    "06": "06_junho",
    "07": "07_julho",
    "08": "08_agosto",
    "09": "09_setembro",
    "10": "10_outubro",
    "11": "11_novembro",
    "12": "12_dezembro"
}


def validate_date(date_str, format="%Y-%m-%d"):
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def mkdir_if_needed(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def optimize_image(file_path, image_to):
    # Verifica se o arquivo é uma imagem
    valid_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    if os.path.splitext(file_path)[1].lower() in valid_extensions:
        with Image.open(file_path) as im:
            im.save(image_to)


# Iteração pelos diretórios
count_folders = 0
for directory in tqdm(os.listdir(folder_from), desc="Organizando pastas"):
    count_folders += 1

    # Extração da data e descrição opcional
    bundle = directory.split(" ")
    date = bundle[0]
    name_folder = directory

    # Validação da data e construção do caminho de destino
    directory_to = ""
    if validate_date(date):
        directory_to = os.path.join(
            folder_to,
            date[0:4],
            meses[date[5:7]],
            date[8:10] + "_" + date[5:7] + "_" + date[0:4],
        )
    else:
        print(f"{name_folder} Não corresponde ao formato dd-mm-yy")
        continue

    if len(bundle) > 1:
        directory_to += " - " + bundle[1]

    # Cria o diretório de destino se necessário
    mkdir_if_needed(directory_to)

    # Processamento dos arquivos
    number = 0
    for file in os.listdir(os.path.join(folder_from, directory)):
        number += 1
        name = f"{date[8:10]}.{date[5:7]}.{date[0:4]}_{autor}_{number:05d}"
        image_to = os.path.join(directory_to, name + os.path.splitext(file)[1])
        # Otimização da imagem
        optimize_image(os.path.join(folder_from, directory, file), image_to)

print(f"\n{count_folders} pastas organizadas\n")
