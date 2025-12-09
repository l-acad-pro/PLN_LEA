import tkinter as tk

def centralizar_janela(janela_filha, janela_pai):
    """
    Centraliza uma janela filha em relação à janela pai.
    
    Args:
        janela_filha: A janela Toplevel que será centralizada
        janela_pai: A janela pai (Tk) como referência
    """
    # Aguarda o update da janela para obter suas dimensões
    janela_filha.update_idletasks()
    
    # Obtém dimensões da janela filha
    largura_filha = janela_filha.winfo_width()
    altura_filha = janela_filha.winfo_height()
    
    # Obtém dimensões e posição da janela pai
    largura_pai = janela_pai.winfo_width()
    altura_pai = janela_pai.winfo_height()
    x_pai = janela_pai.winfo_x()
    y_pai = janela_pai.winfo_y()
    
    # Calcula a posição centralizada
    x = x_pai + (largura_pai // 2) - (largura_filha // 2)
    y = y_pai + (altura_pai // 2) - (altura_filha // 2)
    
    # Define a nova geometria
    janela_filha.geometry(f"+{x}+{y}")