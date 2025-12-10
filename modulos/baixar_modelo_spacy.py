import spacy.cli
import tkinter as tk
from tkinter import Entry, ttk
from modulos.utils import centralizar_janela

def abrir_janela_baixar_modelo(jp):
     janelaBMS = tk.Toplevel(jp)
     janelaBMS.grab_set()
     janelaBMS.lift()
     janelaBMS.focus_set()
     centralizar_janela(janelaBMS, jp)
     label1 = ttk.Label(janelaBMS, text="Informe o modelo a ser baixado:")
     label1.pack(padx=10, pady=5)
     label2 = ttk.Label(janelaBMS, text="Consulte o site do spaCy para obter os modelos disponíveis.", font=("Arial", 8))
     label2.pack(padx=10, pady=2)
     entry1 = Entry(janelaBMS)
     entry1.pack(padx=10, pady=10)

     def baixar_modelo():
          spacy.cli.download(entry1.get())

     btn1 = ttk.Button(janelaBMS, text="Baixar modelo", command=baixar_modelo)
     btn1.pack(padx=10, pady=10)