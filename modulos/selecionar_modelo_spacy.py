"""
Módulo para seleção de modelo spaCy.
Exibe janela para escolher entre os modelos instalados.
"""

import spacy
import tkinter as tk
from tkinter import ttk, messagebox
from spacy.util import get_installed_models
from modulos.utils import centralizar_janela
from . import configuracao

# Variáveis globais do modelo
modelo = None
pln = None


def abrir_janela_selecionar_modelo(janela_pai):
    """Abre janela para seleção do modelo spaCy"""
    global modelo, pln
    
    janela = tk.Toplevel(janela_pai)
    janela.title("Selecionar Modelo spaCy")
    janela.transient(janela_pai)
    janela.grab_set()
    janela.lift()
    janela.focus_set()
    centralizar_janela(janela, janela_pai)
    
    etq_titulo = ttk.Label(janela, text="Escolha o modelo:")
    etq_titulo.pack(padx=10, pady=10)
    
    modelos = list(get_installed_models())
    combo_modelos = ttk.Combobox(janela, values=modelos)
    combo_modelos.pack(padx=10, pady=10)

    def selecionar_modelo():
        """Carrega o modelo selecionado"""
        global modelo, pln
        modelo = combo_modelos.get()
        
        if not modelo:
            messagebox.showwarning(
                "Seleção vazia",
                "Por favor, selecione um modelo da lista.",
                parent=janela
            )
            return
        
        try:
            pln = spacy.load(modelo)
            configuracao.salvar_configuracoes(spacy_modelo=modelo)
            messagebox.showinfo(
                "Sucesso",
                f"Modelo '{modelo}' carregado com sucesso!",
                parent=janela
            )
            janela.destroy()
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível carregar o modelo:\n{str(e)}",
                parent=janela
            )

    btn_selecionar = ttk.Button(janela, text="Selecionar modelo", command=selecionar_modelo)
    btn_selecionar.pack(padx=10, pady=10)
