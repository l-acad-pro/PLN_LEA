import spacy
import tkinter as tk
from tkinter import ttk, messagebox
from spacy.util import get_installed_models
from modulos.utils import centralizar_janela
from modulos import configuracao

def abrir_janela_selecionar_modelo(jp):
    janelaSMS = tk.Toplevel(jp)
    janelaSMS.grab_set()
    janelaSMS.lift()
    janelaSMS.focus_set()
    centralizar_janela(janelaSMS, jp)
    label1 = ttk.Label(janelaSMS, text="Escolha o modelo:")
    label1.pack(padx=10, pady=10)
    modelos = list(get_installed_models())
    combo = ttk.Combobox(janelaSMS, values=modelos)
    combo.pack(padx=10, pady=10)

    def selecionar_modelo():
        global modelo, nlp
        modelo = combo.get()
        if not modelo:
            messagebox.showwarning("Seleção vazia", 
                                  "Por favor, selecione um modelo da lista.",
                                  parent=janelaSMS)
            return
        try:
            nlp = spacy.load(modelo)
            # Salva no arquivo de configuração
            configuracao.salvar_configuracoes(spacy_modelo=modelo)
            messagebox.showinfo("Sucesso", 
                              f"Modelo '{modelo}' carregado com sucesso!",
                              parent=janelaSMS)
            janelaSMS.destroy()
        except Exception as e:
            messagebox.showerror("Erro", 
                               f"Não foi possível carregar o modelo:\n{str(e)}",
                               parent=janelaSMS)

    btn1 = ttk.Button(janelaSMS, text="Selecionar modelo", command=selecionar_modelo)
    btn1.pack(padx=10, pady=10)