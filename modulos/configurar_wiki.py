import tkinter as tk
import tkinter.ttk as tk2
from tkinter import messagebox
from modulos.utils import centralizar_janela

def janela_wkcfg(jp, callback_atualizar, user_agent_atual):
    janela_wkcfg = tk.Toplevel(jp)
    janela_wkcfg.grab_set()
    
    # Centraliza a janela
    centralizar_janela(janela_wkcfg, jp)
    
    label_wkcfg = tk2.Label(janela_wkcfg, text="Informe seu agente de usuário para usar a Wikipedia API:\nExemplo: Nome (Email)", justify="center")
    entry_wkcfg = tk2.Entry(janela_wkcfg, width=30)
    
    wk_lg_var = tk.StringVar(value="")

    def atualizar_idioma():
        callback_atualizar(user_agent_atual, wk_lg_var.get())
    
    label2_wkcfg = tk2.Label(janela_wkcfg, text="Selecione o idioma:")
    label2_wkcfg.pack(padx=10, pady=10)    
    rdb_wkcfg = tk2.Radiobutton(janela_wkcfg, text="Português", variable=wk_lg_var, value="pt", command=atualizar_idioma)
    rdb_wkcfg.pack(padx=10, pady=5)
    rdb_wkcfg2 = tk2.Radiobutton(janela_wkcfg, text="Inglês", variable=wk_lg_var, value="en", command=atualizar_idioma)
    rdb_wkcfg2.pack(padx=10, pady=5)
    
    btn_wkcfg = tk2.Button(janela_wkcfg, text="Salvar configurações")
    btn2_wkcfg = tk2.Button(janela_wkcfg, text="Alterar agente de usuário")
    
    def salvar_config():
        user_agent = entry_wkcfg.get().strip()
        
        # Validação do agente de usuário
        if not user_agent:
            messagebox.showwarning("Erro", "O campo não pode estar vazio!", parent=janela_wkcfg)
            return
        
        if len(user_agent) < 5:
            messagebox.showwarning("Erro", "O campo deve ter no mínimo 5 caracteres!", parent=janela_wkcfg)
            return
        
        idioma = wk_lg_var.get()
        callback_atualizar(user_agent, idioma)
        
        label_wkcfg.pack_forget()
        entry_wkcfg.pack_forget()
        btn_wkcfg.pack_forget()
        
        btn2_wkcfg.pack(padx=10, pady=5)
        
        janela_wkcfg.destroy()

    def selecionar_agent():
        label_wkcfg.pack(padx=10, pady=10)
        entry_wkcfg.pack(padx=10, pady=10)
        btn_wkcfg.pack(padx=10, pady=10)
        
        btn2_wkcfg.pack_forget()
    
    btn_wkcfg.config(command=salvar_config)
    btn2_wkcfg.config(command=selecionar_agent)
    
    # Se USER_AGENT já foi definido, mostra apenas btn2
    if user_agent_atual:
        btn2_wkcfg.pack(padx=10, pady=5)
    else:
        label_wkcfg.pack(padx=10, pady=10)
        entry_wkcfg.pack(padx=10, pady=10)
        btn_wkcfg.pack(padx=10, pady=10)