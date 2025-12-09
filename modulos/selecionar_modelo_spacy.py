import spacy
import tkinter as tk
from tkinter import ttk
from spacy.util import get_installed_models
from modulos.utils import centralizar_janela

def abrir_janela_selecionar_modelo(jp):
    janelaSMS = tk.Toplevel(jp)
    janelaSMS.grab_set()
    centralizar_janela(janelaSMS, jp)
    label1 = ttk.Label(janelaSMS, text="Escolha o modelo:")
    label1.pack(padx=10, pady=10)
    modelos = list(get_installed_models())
    combo = ttk.Combobox(janelaSMS, values=modelos)
    combo.pack(padx=10, pady=10)

    def selecionar_modelo():
        global modelo, nlp
        modelo = combo.get()
        nlp = spacy.load(modelo)

    btn1 = ttk.Button(janelaSMS, text="Selecionar modelo", command=selecionar_modelo)
    btn1.pack(padx=10, pady=10)