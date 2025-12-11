"""
Funções utilitárias para a interface gráfica.
"""

import tkinter as tk


def centralizar_janela(janela_filha, janela_pai):
    """
    Centraliza uma janela filha em relação à janela pai.
    
    Args:
        janela_filha: Janela Toplevel que será centralizada
        janela_pai: Janela pai (Tk) como referência
    """
    janela_filha.update_idletasks()
    
    largura_filha = janela_filha.winfo_width()
    altura_filha = janela_filha.winfo_height()
    
    largura_pai = janela_pai.winfo_width()
    altura_pai = janela_pai.winfo_height()
    x_pai = janela_pai.winfo_x()
    y_pai = janela_pai.winfo_y()
    
    x = x_pai + (largura_pai // 2) - (largura_filha // 2)
    y = y_pai + (altura_pai // 2) - (altura_filha // 2)
    
    janela_filha.geometry(f"+{x}+{y}")
