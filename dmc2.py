import os
from datetime import datetime
from PIL import Image
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import configparser

# Constantes e Dicionário para os meses
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

def contar_arquivos_no_diretorio(caminho_diretorio):
    """Conta os arquivos em um diretório."""
    return sum([len(arquivos) for r, d, arquivos in os.walk(caminho_diretorio)])

def atualizar_lista_de_pastas(caminho_pasta, tree):
    """Atualiza a lista de pastas e o total de arquivos na tabela."""
    for i in tree.get_children():
        tree.delete(i)
    if os.path.exists(caminho_pasta):
        for diretorio in os.listdir(caminho_pasta):
            caminho_dir = os.path.join(caminho_pasta, diretorio)
            if os.path.isdir(caminho_dir):
                total_arquivos = contar_arquivos_no_diretorio(caminho_dir)
                tree.insert('', 'end', values=(diretorio, total_arquivos))

def validar_data(data_str, formato="%Y-%m-%d"):
    try:
        datetime.strptime(data_str, formato)
        return True
    except ValueError:
        return False

def criar_diretorio_se_necessario(diretorio):
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)

def otimizar_imagem(caminho_arquivo, imagem_para):
    extensoes_validas = {".jpg", ".jpeg", ".png", ".gif"}
    if os.path.splitext(caminho_arquivo)[1].lower() in extensoes_validas:
        with Image.open(caminho_arquivo) as im:
            im.save(imagem_para)

def processar_imagens(pasta_origem, pasta_destino, autor, callback_progresso, button_processando):
    diretorios = [d for d in os.listdir(pasta_origem) if os.path.isdir(os.path.join(pasta_origem, d))]
    contagem_pastas = 0
    contagem_imagens = 0
    total_imagens = contar_arquivos_no_diretorio(pasta_origem)
    for diretorio in diretorios:
        contagem_pastas += 1
        bundle = diretorio.split(" ")
        data = bundle[0]
        nome_pasta = diretorio

        caminho_destino = ""
        if validar_data(data):
            caminho_destino = os.path.join(
                pasta_destino,
                data[0:4],
                meses[data[5:7]],
                data[8:10] + "_" + data[5:7] + "_" + data[0:4],
            )
        else:
            print(f"{nome_pasta} Não corresponde ao formato dd-mm-yy")
            continue

        if len(bundle) > 1:
            caminho_destino += " - " + " ".join(bundle[1:])

        criar_diretorio_se_necessario(caminho_destino)

        numero = 0
        for arquivo in os.listdir(os.path.join(pasta_origem, diretorio)):
            numero += 1
            nome = f"{data[8:10]}.{data[5:7]}.{data[0:4]}_{autor}_{numero:05d}"
            imagem_para = os.path.join(caminho_destino, nome + os.path.splitext(arquivo)[1])
            otimizar_imagem(os.path.join(pasta_origem, diretorio, arquivo), imagem_para)
            contagem_imagens += 1
            progresso_atual = 100 * contagem_imagens / total_imagens
            callback_progresso(progresso_atual, contagem_imagens, total_imagens)

    print(f"\n{contagem_pastas} pastas organizadas\n")
    button_processando.config(text="Iniciar Processamento", state=tk.NORMAL)
    messagebox.showinfo("Sucesso", "O processamento de imagens foi concluído com sucesso!")

def iniciar_interface_grafica():
    config = configparser.ConfigParser()
    config_file = 'config.ini'

    def salvar_config():
        config['CONFIG'] = {
            'PastaOrigem': entry_pasta_origem.get(),
            'PastaDestino': entry_pasta_destino.get(),
            'Autor': entry_autor.get()
        }
        with open(config_file, 'w') as configfile:
            config.write(configfile)

    if os.path.exists(config_file):
        config.read(config_file)

    def iniciar_thread_de_processamento():
        salvar_config()
        pasta_origem = entry_pasta_origem.get()
        pasta_destino = entry_pasta_destino.get()
        autor = entry_autor.get()
        button_processando.config(text="Processando...", state=tk.DISABLED)
        Thread(target=processar_imagens, args=(pasta_origem, pasta_destino, autor, atualizar_progresso, button_processando), daemon=True).start()

    def selecionar_pasta_origem():
        diretorio = filedialog.askdirectory()
        if diretorio:
            entry_pasta_origem.delete(0, tk.END)
            entry_pasta_origem.insert(0, diretorio)
            atualizar_lista_de_pastas(diretorio, lista_pastas)

    def selecionar_pasta_destino():
        diretorio = filedialog.askdirectory()
        if diretorio:
            entry_pasta_destino.delete(0, tk.END)
            entry_pasta_destino.insert(0, diretorio)

    def atualizar_progresso(valor, numero_processado, total_arquivos):
        barra_progresso['value'] = valor
        label_progresso.config(text=f"{int(valor)}% ({numero_processado}/{total_arquivos})")

    root = tk.Tk()
    root.title("Configuração de Processamento de Imagens")

    estilo = ttk.Style()
    estilo.configure('TLabel', font=('Arial', 10))
    estilo.configure('TButton', font=('Arial', 10), background='lightblue')
    estilo.configure('TEntry', font=('Arial', 10), padding=5)

    frame_principal = ttk.Frame(root, padding="10 10 10 10")
    frame_principal.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame_principal, text="Pasta de Origem:").grid(column=0, row=0, sticky=tk.W, pady=5)
    entry_pasta_origem = ttk.Entry(frame_principal, width=50)
    entry_pasta_origem.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=5)
    if 'PastaOrigem' in config['CONFIG']:
        entry_pasta_origem.insert(0, config['CONFIG']['PastaOrigem'])
    else:
        entry_pasta_origem.insert(0, "./temp/")
    ttk.Button(frame_principal, text="Selecionar", command=selecionar_pasta_origem).grid(column=2, row=0)

    ttk.Label(frame_principal, text="Pasta de Destino:").grid(column=0, row=1, sticky=tk.W, pady=5)
    entry_pasta_destino = ttk.Entry(frame_principal, width=50)
    entry_pasta_destino.grid(column=1, row=1, sticky=(tk.W, tk.E), pady=5)
    if 'PastaDestino' in config['CONFIG']:
        entry_pasta_destino.insert(0, config['CONFIG']['PastaDestino'])
    else:
        entry_pasta_destino.insert(0, "./organizado/")
    ttk.Button(frame_principal, text="Selecionar", command=selecionar_pasta_destino).grid(column=2, row=1)

    ttk.Label(frame_principal, text="Autor:").grid(column=0, row=2, sticky=tk.W, pady=5)
    entry_autor = ttk.Entry(frame_principal, width=50)
    entry_autor.grid(column=1, row=2, sticky=(tk.W, tk.E), pady=5)
    if 'Autor' in config['CONFIG']:
        entry_autor.insert(0, config['CONFIG']['Autor'])
    else:
        entry_autor.insert(0, "Lucas Macedo")

    button_processando = ttk.Button(frame_principal, text="Iniciar Processamento", command=iniciar_thread_de_processamento)
    button_processando.grid(column=0, row=3, columnspan=3, pady=10)

    colunas = ('nome_pasta', 'total_arquivos')
    lista_pastas = ttk.Treeview(root, columns=colunas, show='headings')
    lista_pastas.heading('nome_pasta', text='Nome da Pasta')
    lista_pastas.column('nome_pasta', width=200)
    lista_pastas.heading('total_arquivos', text='Total de Arquivos')
    lista_pastas.column('total_arquivos', width=100)
    lista_pastas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    pasta_inicial = entry_pasta_origem.get()
    atualizar_lista_de_pastas(pasta_inicial, lista_pastas)

    barra_progresso = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
    barra_progresso.pack(fill=tk.X, padx=10, pady=5, after=frame_principal)

    label_progresso = ttk.Label(root, text="")
    label_progresso.pack(padx=10, pady=5, after=barra_progresso)

    root.mainloop()

if __name__ == "__main__":
    iniciar_interface_grafica()
