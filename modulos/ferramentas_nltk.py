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
        texto: String contendo o texto a ser tokenizado
        
    Returns:
        Lista de tokens (palavras)
    """
    try:
        tokens = word_tokenize(texto)
        return tokens
    except LookupError:
        # Se o tokenizador não estiver disponível, tenta baixar
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
        texto: String contendo o texto a ser tokenizado
        
    Returns:
        Lista de sentenças
    """
    try:
        sentencas = sent_tokenize(texto)
        return sentencas
    except LookupError:
        # Se o tokenizador não estiver disponível, tenta baixar
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
        idioma: 'english' ou 'portuguese' para selecionar o idioma das stopwords
        
    Returns:
        Lista de tokens sem stopwords
    """
    try:
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words(idioma))
        return [token for token in tokens if token.lower() not in stop_words]
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words(idioma))
            return [token for token in tokens if token.lower() not in stop_words]
        except Exception as e:
            raise Exception(f"Erro ao remover stopwords: {str(e)}")

def obter_types(tokens):
    """
    Retorna apenas os types (tokens únicos) removendo duplicatas.
    
    Args:
        tokens: Lista de tokens
        
    Returns:
        Lista de tokens únicos (types)
    """
    # Mantém a ordem de primeira ocorrência
    seen = set()
    types = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            types.append(token)
    return types

def formatar_tokens_para_exibicao(tokens):
    """
    Formata a lista de tokens para exibição em Text widget.
    
    Args:
        tokens: Lista de tokens
        
    Returns:
        String formatada com os tokens
    """
    resultado = ", ".join(tokens)
    return resultado

def verificar_corpora_disponiveis():
    """Verifica quais corpora estão disponíveis"""
    corpora_info = {
        'gutenberg': {'disponivel': False, 'textos': []},
        'machado': {'disponivel': False, 'textos': []}
    }
    
    try:
        corpora_info['gutenberg']['textos'] = gutenberg.fileids()
        corpora_info['gutenberg']['disponivel'] = True
    except LookupError:
        pass
    
    try:
        corpora_info['machado']['textos'] = machado.fileids()
        corpora_info['machado']['disponivel'] = True
    except LookupError:
        pass
    
    return corpora_info

def obter_texto_corpus(corpus_nome, arquivo):
    """Obtém o texto bruto de um arquivo do corpus"""
    try:
        if corpus_nome == 'gutenberg':
            return gutenberg.raw(arquivo)
        elif corpus_nome == 'machado':
            return machado.raw(arquivo)
    except Exception as e:
        raise Exception(f"Erro ao carregar texto: {str(e)}")

def janela_selecionar_corpora(janela_pai, callback_carregar_texto):
    """Abre janela para seleção de corpora do NLTK"""
    janela = tk.Toplevel(janela_pai)
    janela.title("Selecionar Corpus NLTK")
    janela.geometry("600x400")
    janela.transient(janela_pai)
    janela.grab_set()
    janela.lift()
    janela.focus_set()
    
    # Centraliza a janela usando utils
    utils.centralizar_janela(janela, janela_pai)
    
    # Frame superior com instruções
    frame_info = tk2.Frame(janela)
    frame_info.pack(fill=tk.X, padx=10, pady=10)
    
    tk2.Label(frame_info, text="Selecione um corpus e um texto:", 
              font=('Arial', 10, 'bold')).pack(anchor='w')
    
    # Frame principal com notebooks para cada corpus
    notebook = tk2.Notebook(janela)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Verifica corpora disponíveis
    corpora_info = verificar_corpora_disponiveis()
    
    # Variável para armazenar seleção
    selecao = {'corpus': None, 'arquivo': None}
    
    def criar_aba_corpus(corpus_nome, titulo):
        """Cria uma aba para um corpus específico"""
        frame = tk2.Frame(notebook)
        
        if not corpora_info[corpus_nome]['disponivel']:
            # Mostra mensagem de erro se corpus não estiver disponível
            msg_frame = tk2.Frame(frame)
            msg_frame.pack(expand=True)
            tk2.Label(msg_frame, text=f"⚠ Corpus '{corpus_nome}' não disponível", 
                     font=('Arial', 12, 'bold'), foreground='red').pack(pady=10)
            tk2.Label(msg_frame, text=f"Para baixar, execute no terminal Python:",
                     font=('Arial', 9)).pack()
            tk2.Label(msg_frame, text=f"import nltk\nnltk.download('{corpus_nome}')",
                     font=('Courier', 9), background='#f0f0f0', 
                     relief=tk.SUNKEN, padx=10, pady=5).pack(pady=5)
            return frame
        
        # Lista de textos
        textos = corpora_info[corpus_nome]['textos']
        
        # Frame com listbox e scrollbar
        list_frame = tk2.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk2.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                            selectmode=tk.SINGLE, font=('Courier', 9))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Popula listbox
        for texto in textos:
            listbox.insert(tk.END, texto)
        
        # Label com informação
        info_label = tk2.Label(frame, text=f"Total: {len(textos)} texto(s) disponível(is)",
                              font=('Arial', 9), foreground='gray')
        info_label.pack(pady=5)
        
        def on_select(event):
            """Atualiza seleção quando item é clicado"""
            if listbox.curselection():
                idx = listbox.curselection()[0]
                selecao['corpus'] = corpus_nome
                selecao['arquivo'] = textos[idx]
        
        listbox.bind('<<ListboxSelect>>', on_select)
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
            messagebox.showwarning("Seleção vazia", 
                                  "Por favor, selecione um texto da lista.",
                                  parent=janela)
            return
        
        try:
            texto = obter_texto_corpus(selecao['corpus'], selecao['arquivo'])
            callback_carregar_texto(texto, selecao['corpus'], selecao['arquivo'])
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao carregar", 
                               f"Não foi possível carregar o texto:\n{str(e)}",
                               parent=janela)
    
    botao_carregar = tk2.Button(frame_botoes, text="Carregar Texto", 
                               command=carregar_e_fechar)
    botao_carregar.pack(side=tk.LEFT, padx=5)
    
    botao_cancelar = tk2.Button(frame_botoes, text="Cancelar", 
                               command=janela.destroy)
    botao_cancelar.pack(side=tk.LEFT, padx=5)
