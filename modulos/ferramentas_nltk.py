"""
Ferramentas de Processamento de Linguagem Natural com NLTK.
Funções para tokenização, remoção de stopwords e seleção de corpora.
"""

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import gutenberg, machado
import tkinter as tk
import tkinter.ttk as tk2
from tkinter import messagebox
from . import utils

def tokenizar_texto(texto):
    """
    Tokeniza o texto em palavras usando NLTK.
    
    Args:
        texto: Texto a ser tokenizado
        
    Returns:
        Lista de tokens (palavras)
    """
    try:
        tokens = word_tokenize(texto)
        return tokens
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
            tokens = word_tokenize(texto)
            return tokens
        except Exception as e:
            raise Exception(f"Erro ao tokenizar: {str(e)}")


def tokenizar_sentencas(texto):
    """
    Tokeniza o texto em sentenças usando NLTK.
    
    Args:
        texto: Texto a ser tokenizado
        
    Returns:
        Lista de sentenças
    """
    try:
        sentencas = sent_tokenize(texto)
        return sentencas
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
            sentencas = sent_tokenize(texto)
            return sentencas
        except Exception as e:
            raise Exception(f"Erro ao tokenizar sentenças: {str(e)}")


def remover_stopwords(tokens, idioma='english'):
    """
    Remove stopwords da lista de tokens.
    
    Args:
        tokens: Lista de tokens
        idioma: 'english' ou 'portuguese'
        
    Returns:
        Lista de tokens sem stopwords
    """
    try:
        from nltk.corpus import stopwords
        palavras_vazias = set(stopwords.words(idioma))
        return [token for token in tokens if token.lower() not in palavras_vazias]
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
            from nltk.corpus import stopwords
            palavras_vazias = set(stopwords.words(idioma))
            return [token for token in tokens if token.lower() not in palavras_vazias]
        except Exception as e:
            raise Exception(f"Erro ao remover stopwords: {str(e)}")


def obter_types(tokens):
    """
    Retorna apenas os types (tokens únicos) removendo duplicatas.
    
    Args:
        tokens: Lista de tokens
        
    Returns:
        Lista de tokens únicos mantendo ordem de ocorrência
    """
    vistos = set()
    types = []
    for token in tokens:
        if token not in vistos:
            vistos.add(token)
            types.append(token)
    return types


def formatar_tokens_para_exibicao(tokens):
    """
    Formata lista de tokens para exibição em widget Text.
    
    Args:
        tokens: Lista de tokens
        
    Returns:
        String formatada com tokens separados por vírgula
    """
    return ", ".join(tokens)


def verificar_corpora_disponiveis():
    """
    Verifica quais corpora estão disponíveis.
    
    Returns:
        Dicionário com informações dos corpora disponíveis
    """
    info_corpora = {
        'gutenberg': {'disponivel': False, 'textos': []},
        'machado': {'disponivel': False, 'textos': []}
    }
    
    try:
        info_corpora['gutenberg']['textos'] = gutenberg.fileids()
        info_corpora['gutenberg']['disponivel'] = True
    except LookupError:
        pass
    
    try:
        info_corpora['machado']['textos'] = machado.fileids()
        info_corpora['machado']['disponivel'] = True
    except LookupError:
        pass
    
    return info_corpora


def obter_texto_corpus(nome_corpus, arquivo):
    """
    Obtém o texto bruto de um arquivo do corpus.
    
    Args:
        nome_corpus: Nome do corpus ('gutenberg' ou 'machado')
        arquivo: Nome do arquivo dentro do corpus
        
    Returns:
        Texto bruto do arquivo
    """
    try:
        if nome_corpus == 'gutenberg':
            return gutenberg.raw(arquivo)
        elif nome_corpus == 'machado':
            return machado.raw(arquivo)
    except Exception as e:
        raise Exception(f"Erro ao carregar texto: {str(e)}")


def janela_selecionar_corpora(janela_pai, callback_carregar_texto):
    """
    Abre janela para seleção de corpora do NLTK.
    
    Args:
        janela_pai: Janela principal da aplicação
        callback_carregar_texto: Função para carregar texto selecionado
    """
    janela = tk.Toplevel(janela_pai)
    janela.title("Selecionar Corpus NLTK")
    janela.geometry("600x400")
    janela.transient(janela_pai)
    janela.grab_set()
    janela.lift()
    janela.focus_set()
    
    utils.centralizar_janela(janela, janela_pai)
    
    # Frame superior com instruções
    frame_info = tk2.Frame(janela)
    frame_info.pack(fill=tk.X, padx=10, pady=10)
    
    tk2.Label(
        frame_info,
        text="Selecione um corpus para carregar o texto:",
        font=('Arial', 10, 'bold')
    ).pack(anchor='w')
    
    # Notebook para cada corpus
    notebook = tk2.Notebook(janela)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    info_corpora = verificar_corpora_disponiveis()
    selecao = {'corpus': None, 'arquivo': None}
    
    def criar_aba_corpus(nome_corpus, titulo):
        """Cria uma aba para um corpus específico"""
        frame = tk2.Frame(notebook)
        
        if not info_corpora[nome_corpus]['disponivel']:
            # Mensagem de erro se corpus não disponível
            frame_msg = tk2.Frame(frame)
            frame_msg.pack(expand=True)
            tk2.Label(
                frame_msg,
                text=f"⚠ Corpus '{nome_corpus}' não disponível",
                font=('Arial', 12, 'bold'),
                foreground='red'
            ).pack(pady=10)
            tk2.Label(
                frame_msg,
                text=f"Para baixar, execute no terminal Python:",
                font=('Arial', 9)
            ).pack()
            tk2.Label(
                frame_msg,
                text=f"import nltk\nnltk.download('{nome_corpus}')",
                font=('Courier', 9),
                background='#f0f0f0',
                relief=tk.SUNKEN,
                padx=10, pady=5
            ).pack(pady=5)
            return frame
        
        textos = info_corpora[nome_corpus]['textos']
        
        # Frame com listbox e scrollbar
        frame_lista = tk2.Frame(frame)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk2.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            font=('Courier', 9)
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Popula listbox
        for texto in textos:
            listbox.insert(tk.END, texto)
        
        etq_info = tk2.Label(
            frame,
            text=f"Total: {len(textos)} texto(s) disponível(is)",
            font=('Arial', 9),
            foreground='gray'
        )
        etq_info.pack(pady=5)
        
        def ao_selecionar(event):
            """Atualiza seleção quando item é clicado"""
            if listbox.curselection():
                idx = listbox.curselection()[0]
                selecao['corpus'] = nome_corpus
                selecao['arquivo'] = textos[idx]
        
        listbox.bind('<<ListboxSelect>>', ao_selecionar)
        listbox.bind('<Double-Button-1>', lambda e: carregar_e_fechar())
        
        return frame
    
    # Cria abas para Gutenberg e Machado
    aba_gutenberg = criar_aba_corpus('gutenberg', 'Gutenberg')
    aba_machado = criar_aba_corpus('machado', 'Machado de Assis')
    
    notebook.add(aba_machado, text='Machado de Assis (Português)')
    notebook.add(aba_gutenberg, text='Gutenberg (Inglês)')
    
    # Frame de botões
    frame_botoes = tk2.Frame(janela)
    frame_botoes.pack(fill=tk.X, padx=10, pady=10)
    
    def carregar_e_fechar():
        """Carrega o texto selecionado e fecha a janela"""
        if not selecao['corpus'] or not selecao['arquivo']:
            messagebox.showwarning(
                "Seleção vazia",
                "Por favor, selecione um texto da lista.",
                parent=janela
            )
            return
        
        try:
            texto = obter_texto_corpus(selecao['corpus'], selecao['arquivo'])
            callback_carregar_texto(texto, selecao['corpus'], selecao['arquivo'])
            janela.destroy()
        except Exception as e:
            messagebox.showerror(
                "Erro ao carregar",
                f"Não foi possível carregar o texto:\n{str(e)}",
                parent=janela
            )
    
    btn_carregar = tk2.Button(frame_botoes, text="Carregar Texto", command=carregar_e_fechar)
    btn_carregar.pack(side=tk.LEFT, padx=5)
    
    btn_cancelar = tk2.Button(frame_botoes, text="Cancelar", command=janela.destroy)
    btn_cancelar.pack(side=tk.LEFT, padx=5)
