import os
from datetime import datetime
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import configparser
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

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

class ProcessamentoDeImagensApp:
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = 'config.ini'
        self.root = tk.Tk()
        self.root.title("Configuração de Processamento de Imagens")
        self.estilo = ttk.Style("darkly")
        self.estilo.configure('TLabel', font=('Arial', 10))
        self.estilo.configure('TButton', font=('Arial', 10), bootstyle=SUCCESS)
        self.estilo.configure('TEntry', font=('Arial', 10), padding=5)

        self.frame_principal = ttk.Frame(self.root, padding="10 10 10 10")
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        self.entry_pasta_origem = ttk.Entry(self.frame_principal, width=50)
        self.entry_pasta_origem.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=5)

        self.entry_pasta_destino = ttk.Entry(self.frame_principal, width=50)
        self.entry_pasta_destino.grid(column=1, row=1, sticky=(tk.W, tk.E), pady=5)

        self.entry_autor = ttk.Entry(self.frame_principal, width=50)
        self.entry_autor.grid(column=1, row=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(self.frame_principal, text="Atualizar Lista de Pastas", command=self.atualizar_lista_de_pastas).grid(column=0, row=3, sticky=tk.W, pady=10)

        self.button_processando = ttk.Button(self.frame_principal, text="Iniciar Processamento", bootstyle=SUCCESS, command=self.iniciar_thread_de_processamento)
        self.button_processando.grid(column=2, row=3, sticky=tk.E, pady=10)

        self.colunas = ('nome_pasta', 'total_arquivos')
        self.lista_pastas = ttk.Treeview(self.root, columns=self.colunas, show='headings', bootstyle='info')
        self.lista_pastas.heading('nome_pasta', text='Nome da Pasta')
        self.lista_pastas.column('nome_pasta', width=200)
        self.lista_pastas.heading('total_arquivos', text='Total de Arquivos')
        self.lista_pastas.column('total_arquivos', width=100, anchor=tk.CENTER)
        self.lista_pastas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.barra_progresso = ttk.Progressbar(self.root, bootstyle="striped", orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.barra_progresso.pack(fill=tk.X, padx=10, pady=5, after=self.frame_principal)

        self.label_progresso = ttk.Label(self.root, text="")
        self.label_progresso.pack(padx=10, pady=5, after=self.barra_progresso)

        self.carregar_configuracoes()
        self.configurar_botoes()

        self.atualizar_lista_de_pastas()

    def carregar_configuracoes(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            if 'PastaOrigem' in self.config['CONFIG']:
                self.entry_pasta_origem.insert(0, self.config['CONFIG']['PastaOrigem'])
                self.entry_pasta_origem.configure(state='readonly')
            else:
                self.entry_pasta_origem.insert(0, "./temp/")
                self.entry_pasta_origem.configure(state='readonly')

            if 'PastaDestino' in self.config['CONFIG']:
                self.entry_pasta_destino.insert(0, self.config['CONFIG']['PastaDestino'])
                self.entry_pasta_destino.configure(state='readonly')
            else:
                self.entry_pasta_destino.insert(0, "./organizado/")
                self.entry_pasta_destino.configure(state='readonly')

            if 'Autor' in self.config['CONFIG']:
                self.entry_autor.insert(0, self.config['CONFIG']['Autor'])
            else:
                self.entry_autor.insert(0, "Lucas Macedo")

    def salvar_configuracoes(self):
        self.config['CONFIG'] = {
            'PastaOrigem': self.entry_pasta_origem.get(),
            'PastaDestino': self.entry_pasta_destino.get(),
            'Autor': self.entry_autor.get()
        }
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def configurar_botoes(self):
        self.button_processando.config(command=self.iniciar_thread_de_processamento)

    def iniciar_thread_de_processamento(self):
        self.salvar_configuracoes()
        pasta_origem = self.entry_pasta_origem.get()
        pasta_destino = self.entry_pasta_destino.get()
        autor = self.entry_autor.get()
        self.button_processando.config(text="Processando...", state=tk.DISABLED)
        Thread(target=self.processar_imagens, args=(pasta_origem, pasta_destino, autor, self.atualizar_progresso, self.button_processando), daemon=True).start()

    def contar_arquivos_no_diretorio(self, caminho_diretorio):
        """Conta os arquivos em um diretório."""
        return sum([len(arquivos) for r, d, arquivos in os.walk(caminho_diretorio)])

    def atualizar_lista_de_pastas(self):
        """Atualiza a lista de pastas e o total de arquivos na tabela."""
        caminho_pasta = self.entry_pasta_origem.get()
        for i in self.lista_pastas.get_children():
            self.lista_pastas.delete(i)
        if os.path.exists(caminho_pasta):
            for diretorio in os.listdir(caminho_pasta):
                caminho_dir = os.path.join(caminho_pasta, diretorio)
                if os.path.isdir(caminho_dir):
                    total_arquivos = self.contar_arquivos_no_diretorio(caminho_dir)
                    if not self.validar_nome_pasta(diretorio):
                        # Destaque em vermelho os nomes de pastas que não seguem a regra
                        self.lista_pastas.insert('', 'end', values=(diretorio, total_arquivos), tags='error')
                    else:
                        self.lista_pastas.insert('', 'end', values=(diretorio, total_arquivos))
        self.lista_pastas.tag_configure('error', foreground='red')

    def validar_nome_pasta(self, nome_pasta):
        bundle = nome_pasta.split(" ")
        return self.validar_data(bundle[0]) and len(bundle) > 1

    def validar_data(self, data_str, formato="%Y-%m-%d"):
        try:
            datetime.strptime(data_str, formato)
            return True
        except ValueError:
            return False

    def criar_diretorio_se_necessario(self, diretorio):
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

    def otimizar_imagem(self, caminho_arquivo, imagem_para):
        extensoes_validas = {".jpg", ".jpeg", ".png", ".gif"}
        if os.path.splitext(caminho_arquivo)[1].lower() in extensoes_validas:
            with Image.open(caminho_arquivo) as im:
                im.save(imagem_para)

    def processar_imagens(self, pasta_origem, pasta_destino, autor, callback_progresso, button_processando):
        diretorios = [d for d in os.listdir(pasta_origem) if os.path.isdir(os.path.join(pasta_origem, d))]

        contagem_pastas = 0
        contagem_imagens = 0
        total_imagens = self.contar_arquivos_no_diretorio(pasta_origem)

        for diretorio in diretorios:
            contagem_pastas += 1
            bundle = diretorio.split(" ")
            data = bundle[0]

            caminho_destino = ""
            if self.validar_data(data) and len(bundle) > 1:
                caminho_destino = os.path.join(
                    pasta_destino,
                    data[0:4],
                    meses[data[5:7]],
                    data[8:10] + "_" + data[5:7] + "_" + data[0:4],
                )
            else:
                print(f"{diretorio} Não corresponde ao formato dd-mm-yy")
                continue

            if len(bundle) > 1:
                caminho_destino += " - " + " ".join(bundle[1:])

            self.criar_diretorio_se_necessario(caminho_destino)

            numero = 0
            for arquivo in os.listdir(os.path.join(pasta_origem, diretorio)):
                numero += 1
                nome = f"{data[8:10]}.{data[5:7]}.{data[0:4]}_{autor}_{numero:05d}"
                imagem_para = os.path.join(caminho_destino, nome + os.path.splitext(arquivo)[1])
                self.otimizar_imagem(os.path.join(pasta_origem, diretorio, arquivo), imagem_para)
                contagem_imagens += 1
                progresso_atual = 100 * contagem_imagens / total_imagens
                callback_progresso(progresso_atual, contagem_imagens, total_imagens)

        print(f"\n{contagem_pastas} pastas organizadas\n")
        button_processando.config(text="Iniciar Processamento", state=tk.NORMAL)
        messagebox.showinfo("Sucesso", "O processamento de imagens foi concluído com sucesso!")

    def selecionar_pasta_origem(self):
        diretorio = filedialog.askdirectory()
        if diretorio:
            self.entry_pasta_origem.configure(state='normal')
            self.entry_pasta_origem.delete(0, tk.END)
            self.entry_pasta_origem.insert(0, diretorio)
            self.entry_pasta_origem.configure(state='readonly')
            self.atualizar_lista_de_pastas()

    def selecionar_pasta_destino(self):
        diretorio = filedialog.askdirectory()
        if diretorio:
            self.entry_pasta_destino.configure(state='normal')
            self.entry_pasta_destino.delete(0, tk.END)
            self.entry_pasta_destino.insert(0, diretorio)
            self.entry_pasta_destino.configure(state='readonly')

    def atualizar_progresso(self, valor, numero_processado, total_arquivos):
        self.barra_progresso['value'] = valor
        self.label_progresso.config(text=f"{int(valor)}% ({numero_processado}/{total_arquivos})")

    def run(self):
        ttk.Label(self.frame_principal, text="Pasta de Origem:").grid(column=0, row=0, sticky=tk.W, pady=5)
        ttk.Button(self.frame_principal, text="Selecionar", command=self.selecionar_pasta_origem).grid(column=2, row=0)

        ttk.Label(self.frame_principal, text="Pasta de Destino:").grid(column=0, row=1, sticky=tk.W, pady=5)
        ttk.Button(self.frame_principal, text="Selecionar", command=self.selecionar_pasta_destino).grid(column=2, row=1)

        ttk.Label(self.frame_principal, text="Autor:").grid(column=0, row=2, sticky=tk.W, pady=5)

        self.root.mainloop()

if __name__ == "__main__":
    app = ProcessamentoDeImagensApp()
    app.run()