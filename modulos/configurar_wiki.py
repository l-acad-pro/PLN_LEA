"""
Módulo para configuração da API Wikipedia.
Exibe janela para definir agente de usuário e idioma.
"""

import tkinter as tk
import tkinter.ttk as tk2
from tkinter import messagebox
from modulos.utils import centralizar_janela


def janela_wkcfg(janela_pai, callback_atualizar, agente_usuario_atual):
    """
    Abre janela para configuração da Wikipedia API.
    
    Args:
        janela_pai: Janela principal da aplicação
        callback_atualizar: Função para atualizar configurações
        agente_usuario_atual: Agente de usuário atual (se existir)
    """
    janela = tk.Toplevel(janela_pai)
    janela.title("Configuração da Wikipedia API")
    janela.transient(janela_pai)
    janela.grab_set()
    janela.lift()
    janela.focus_set()
    centralizar_janela(janela, janela_pai)
    
    # Widgets para entrada do agente de usuário
    etq_instrucao = tk2.Label(
        janela,
        text="Informe seu agente de usuário para usar a Wikipedia API:\n\nExemplo: Nome (Email)",
        justify="center"
    )
    ent_agente = tk2.Entry(janela, width=30)
    
    # Variável para idioma
    var_idioma = tk.StringVar(value="")

    def atualizar_idioma():
        """Atualiza o idioma selecionado"""
        callback_atualizar(agente_usuario_atual, var_idioma.get())
    
    # Widgets de seleção de idioma
    etq_idioma = tk2.Label(janela, text="Selecione o idioma:")
    etq_idioma.pack(padx=10, pady=10)
    
    rd_portugues = tk2.Radiobutton(
        janela,
        text="Português",
        variable=var_idioma,
        value="pt",
        command=atualizar_idioma
    )
    rd_portugues.pack(padx=10, pady=5)
    
    rd_ingles = tk2.Radiobutton(
        janela,
        text="Inglês",
        variable=var_idioma,
        value="en",
        command=atualizar_idioma
    )
    rd_ingles.pack(padx=10, pady=5)
    
    # Botões
    btn_salvar = tk2.Button(janela, text="Salvar configurações")
    btn_alterar = tk2.Button(janela, text="Alterar agente de usuário")
    
    def salvar_config():
        """Salva as configurações do agente de usuário"""
        agente = ent_agente.get().strip()
        
        if not agente:
            messagebox.showwarning("Erro", "O campo não pode estar vazio!", parent=janela)
            return
        
        if len(agente) < 5:
            messagebox.showwarning("Erro", "O campo deve ter no mínimo 5 caracteres!", parent=janela)
            return
        
        idioma = var_idioma.get()
        callback_atualizar(agente, idioma)
        
        etq_instrucao.pack_forget()
        ent_agente.pack_forget()
        btn_salvar.pack_forget()
        
        btn_alterar.pack(padx=10, pady=5)
        janela.destroy()

    def exibir_entrada_agente():
        """Exibe campos para entrada do agente de usuário"""
        etq_instrucao.pack(padx=10, pady=(10, 0))
        ent_agente.pack(padx=10, pady=10)
        btn_salvar.pack(padx=10, pady=10)
        btn_alterar.pack_forget()
    
    btn_salvar.config(command=salvar_config)
    btn_alterar.config(command=exibir_entrada_agente)
    
    # Layout inicial depende do estado atual
    if agente_usuario_atual:
        btn_alterar.pack(padx=10, pady=5)
    else:
        etq_instrucao.pack(padx=10, pady=(10, 0))
        ent_agente.pack(padx=10, pady=10)
        btn_salvar.pack(padx=10, pady=10)
