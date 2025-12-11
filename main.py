import wikipediaapi
import re
from tkinter import messagebox, filedialog, simpledialog
import tkinter as tk
import tkinter.ttk as tk2
import csv, json
import ttkbootstrap as tb
from modulos import selecionar_modelo_spacy, configurar_wiki, ferramentas_nltk, ferramentas_spacy, configuracao

USER_AGENT = None
wk_lg = None
wiki = None
texto_foi_limpo = False

# Variáveis para limitação de caracteres
limite_inicio = None
limite_fim = None
texto_original = None  # Armazena o texto antes de aplicar limites
texto_antes_limpar = None  # Armazena o texto antes de limpar

class ToolTip:
    def __init__(self, widget, text, delay=0.5):
        self.widget = widget
        self.text = text
        self.delay = int(delay * 1000)
        self.tip_window = None
        self.after_id = None
        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide_tip)

    def schedule(self, event=None):
        self.after_id = self.widget.after(self.delay, self.show_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#f8f9fa",  # cor mais clara, estilo ttk
            foreground="#222",      # texto escuro
            relief="solid",          # borda sólida
            borderwidth=1,          # borda muito fina (1 pixel)
            #font=("Open Sans", 10),  # fonte mais moderna
            padx=8, pady=4,         # espaçamento interno
            wraplength=320          # quebra de linha para textos longos
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def atualizar_config_wiki(user_agent, idioma, mostrar_msg=True):
    global USER_AGENT, wk_lg, wiki
    if idioma:
        wk_lg = idioma

    if user_agent:
        USER_AGENT = user_agent

    # Só recria o objeto se ambos estiverem definidos; permite escolher idioma antes do user agent
    if USER_AGENT and wk_lg:
        wiki = wikipediaapi.Wikipedia(language=wk_lg, user_agent=USER_AGENT)
        # Salva no arquivo de configuração
        configuracao.salvar_configuracoes(wiki_user_agent=USER_AGENT, wiki_idioma=wk_lg)
        if mostrar_msg:
            messagebox.showinfo("Sucesso", f"Configurações atualizadas!\nIdioma: {wk_lg}\nUser Agent: {USER_AGENT}")

def atualizar_contador_texto(event=None):
    """Atualiza o contador de caracteres da aba Personalizada"""
    conteudo = Texto_texto.get("1.0", tk.END)
    total_chars = len(conteudo) - 1  # Remove o \n final que o Text sempre adiciona
    if total_chars > 0:
        texto_contador.config(text=f"Caracteres: {total_chars}")
        texto_contador.pack(padx=5, pady=2)
    else:
        texto_contador.pack_forget()

def definir_limites_caracteres():
    """Abre diálogo para definir limites de caracteres para processamento"""
    global limite_inicio, limite_fim, texto_original
    
    # Obtém o texto atual
    aba_atual = texto_notebook.select()
    if aba_atual == str(frame_texto):
        conteudo = Texto_texto.get("1.0", tk.END).strip()
    else:  # frame_wiki
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            conteudo = wk_texto1.get("1.0", tk.END).strip()
        else:  # tab_conteudo
            conteudo = wk_texto2.get("1.0", tk.END).strip()
    
    if not conteudo:
        messagebox.showwarning("Texto vazio", 
                              "Não há texto para definir limites.",
                              parent=janelaPrincipal)
        return
    
    # Armazena o texto original antes de aplicar limites
    texto_original = conteudo
    
    total_chars = len(conteudo)
    
    # Diálogo para caractere inicial
    inicio = simpledialog.askinteger(
        "Limitador de Caracteres",
        f"Texto possui {total_chars} caracteres.\n\nEm qual caractere o texto deve COMEÇAR?\n(Digite 0 ou 1 para começar do início)",
        parent=janelaPrincipal,
        minvalue=0,
        maxvalue=total_chars
    )
    
    if inicio is None:  # Cancelou
        return
    
    # Ajusta para índice Python (começando em 0)
    inicio = max(0, inicio - 1) if inicio > 0 else 0
    
    # Diálogo para caractere final
    fim = simpledialog.askinteger(
        "Limitador de Caracteres",
        f"Em qual caractere o texto deve TERMINAR?\n(Digite {total_chars} para ir até o final)",
        parent=janelaPrincipal,
        minvalue=inicio + 1,
        maxvalue=total_chars
    )
    
    if fim is None:  # Cancelou
        return
    
    # Define os limites globais
    limite_inicio = inicio
    limite_fim = fim
    
    # Extrai o fragmento limitado
    fragmento = conteudo[inicio:fim]
    
    # Atualiza o Text widget com o fragmento limitado
    if aba_atual == str(frame_texto):
        Texto_texto.delete("1.0", tk.END)
        Texto_texto.insert(tk.END, fragmento)
        atualizar_contador_texto()
    else:  # frame_wiki
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            wk_texto1.config(state='normal')
            wk_texto1.delete("1.0", tk.END)
            wk_texto1.insert(tk.END, fragmento)
            wk_texto1.config(state='disabled')
            atualizar_contador_resumo()
        else:  # tab_conteudo
            wk_texto2.config(state='normal')
            wk_texto2.delete("1.0", tk.END)
            wk_texto2.insert(tk.END, fragmento)
            wk_texto2.config(state='disabled')
            atualizar_contador_conteudo()
    
    # Oculta botões de limitar e mostra botões de remover limites
    texto_botao_limitar.pack_forget()
    texto_botao_resetar.pack(side=tk.LEFT, padx=5, after=texto_botao_restaurar)
    
    wk_botao_limitar_resumo.pack_forget()
    wk_botao_resetar_resumo.pack(side=tk.RIGHT, padx=2, before=wk_botao_limitar_resumo)
    
    wk_botao_limitar_conteudo.pack_forget()
    wk_botao_resetar_conteudo.pack(side=tk.RIGHT, padx=2, before=wk_botao_limitar_conteudo)
    
    # Mostra confirmação
    messagebox.showinfo(
        "Limites Aplicados",
        f"O texto foi limitado:\n\nInício: caractere {inicio + 1}\nFim: caractere {fim}\nTotal: {fim - inicio} caracteres",
        parent=janelaPrincipal
    )

def resetar_limites():
    """Remove os limites de caracteres definidos e restaura o texto original"""
    global limite_inicio, limite_fim, texto_original
    
    # Verifica se há texto original armazenado
    if texto_original is None:
        messagebox.showwarning("Sem texto original",
                              "Não há texto original para restaurar.",
                              parent=janelaPrincipal)
        return
    
    # Restaura o texto original no Text widget
    aba_atual = texto_notebook.select()
    if aba_atual == str(frame_texto):
        Texto_texto.delete("1.0", tk.END)
        Texto_texto.insert(tk.END, texto_original)
        atualizar_contador_texto()
    else:  # frame_wiki
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            wk_texto1.config(state='normal')
            wk_texto1.delete("1.0", tk.END)
            wk_texto1.insert(tk.END, texto_original)
            wk_texto1.config(state='disabled')
            atualizar_contador_resumo()
        else:  # tab_conteudo
            wk_texto2.config(state='normal')
            wk_texto2.delete("1.0", tk.END)
            wk_texto2.insert(tk.END, texto_original)
            wk_texto2.config(state='disabled')
            atualizar_contador_conteudo()
    
    # Limpa as variáveis de limite
    limite_inicio = None
    limite_fim = None
    texto_original = None
    
    # Oculta botões de remover limites e mostra botões de limitar
    texto_botao_resetar.pack_forget()
    texto_botao_limitar.pack(side=tk.LEFT, padx=5, after=texto_botao_restaurar)
    
    wk_botao_resetar_resumo.pack_forget()
    wk_botao_limitar_resumo.pack(side=tk.RIGHT, padx=2, before=wk_botao_resetar_resumo)
    
    wk_botao_resetar_conteudo.pack_forget()
    wk_botao_limitar_conteudo.pack(side=tk.RIGHT, padx=2, before=wk_botao_resetar_conteudo)
    
    messagebox.showinfo("Limites Removidos", 
                       "Os limites de caracteres foram removidos.\nO texto completo será processado.",
                       parent=janelaPrincipal)

def atualizar_contador_resumo(event=None):
    """Atualiza o contador de caracteres da sub-aba Resumo"""
    conteudo = wk_texto1.get("1.0", tk.END)
    total_chars = len(conteudo) - 1
    if total_chars > 0:
        wk_contador_resumo.config(text=f"Caracteres: {total_chars}")
        wk_contador_resumo.pack(padx=5, pady=2)
    else:
        wk_contador_resumo.pack_forget()

def atualizar_contador_conteudo(event=None):
    """Atualiza o contador de caracteres da sub-aba Conteúdo"""
    conteudo = wk_texto2.get("1.0", tk.END)
    total_chars = len(conteudo) - 1
    if total_chars > 0:
        wk_contador_conteudo.config(text=f"Caracteres: {total_chars}")
        wk_contador_conteudo.pack(padx=5, pady=2)
    else:
        wk_contador_conteudo.pack_forget()

def abrir_arquivo():
    caminho = filedialog.askopenfilename(
        title="Selecione um arquivo de texto",
        filetypes=[("Arquivo de texto", "*.txt")],
        parent=janelaPrincipal
    )
    if not caminho:  
        return
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except UnicodeDecodeError:
        with open(caminho, "r", encoding="latin-1") as f:
            conteudo = f.read()
    except Exception as e:
        messagebox.showerror("Erro ao abrir", f"Não foi possível abrir o arquivo:\n{e}")
        return

    # Mostra aba "Personalizada" ao abrir arquivo
    texto_notebook.select(frame_texto)

    # Substitui o conteúdo do Text
    Texto_texto.delete("1.0", tk.END)
    Texto_texto.insert(tk.END, conteudo)
    
    # Atualiza contador de caracteres
    atualizar_contador_texto()

def processar_tokenizacao():
    """Tokeniza o texto com NLTK e spaCy, exibindo os resultados em seus respectivos Texts"""
    global limite_inicio, limite_fim
    
    # Verifica se há modelo spaCy carregado
    if not hasattr(selecionar_modelo_spacy, 'nlp') or selecionar_modelo_spacy.nlp is None:
        messagebox.showwarning(
            "Modelo não carregado",
            "É necessário selecionar um modelo spaCy no menu Configurações antes de tokenizar.",
            parent=janelaPrincipal
        )
        return
    
    # Verifica qual aba está ativa no notebook de texto
    aba_atual = texto_notebook.select()
    
    if aba_atual == str(frame_texto):
        texto = Texto_texto.get("1.0", tk.END).strip()
    else:  # frame_wiki
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            texto = wk_texto1.get("1.0", tk.END).strip()
        else:  # tab_conteudo
            texto = wk_texto2.get("1.0", tk.END).strip()
    
    if not texto:
        messagebox.showwarning("Texto vazio", 
                              "Não há texto para processar. Insira um texto ou busque na Wikipedia.",
                              parent=janelaPrincipal)
        return
    
    # Aplica limitação de caracteres se definida
    if limite_inicio is not None and limite_fim is not None:
        texto = texto[limite_inicio:limite_fim]
    
    erros = []
    total_nltk = 0
    total_spacy = 0
    
    # Processa com NLTK
    try:
        # Verifica o tipo de tokenização
        if tipo_tokenizacao.get() == 2:  # Tokenizar em frases
            tokens_nltk = ferramentas_nltk.tokenizar_sentencas(texto)
        else:  # Tokenizar em palavras
            tokens_nltk = ferramentas_nltk.tokenizar_texto(texto)
            
            # Aplica opções dos checkbuttons
            if incluir_stopwords.get():
                tokens_nltk = ferramentas_nltk.remover_stopwords(tokens_nltk, idioma_stopwords.get())
            
            if tokenizar_types.get():
                tokens_nltk = ferramentas_nltk.obter_types(tokens_nltk)
        
        resultado_nltk = ferramentas_nltk.formatar_tokens_para_exibicao(tokens_nltk)
        total_nltk = len(tokens_nltk)
        
        # Exibe no Text do NLTK
        nltk_texto.delete("1.0", tk.END)
        nltk_texto.insert(tk.END, resultado_nltk)
        
        # Atualiza e exibe o total de tokens NLTK
        nltk_total.config(text=f"Total de tokens: {total_nltk}")
        nltk_total.pack(padx=5, pady=5)
        
    except Exception as e:
        erros.append(f"NLTK: {str(e)}")
    
    # Processa com spaCy
    try:
        nlp = selecionar_modelo_spacy.nlp
        modelo_nome = selecionar_modelo_spacy.modelo if hasattr(selecionar_modelo_spacy, 'modelo') else "Desconhecido"
        
        tokens_spacy = ferramentas_spacy.tokenizar_texto(texto, nlp)
        
        # Aplica opções dos checkbuttons (mesmas do NLTK)
        if incluir_stopwords.get():
            tokens_spacy = ferramentas_spacy.remover_stopwords(tokens_spacy, idioma_stopwords.get())
        
        if tokenizar_types.get():
            tokens_spacy = ferramentas_spacy.obter_types(tokens_spacy)
        
        resultado_spacy = ferramentas_spacy.formatar_tokens_para_exibicao(tokens_spacy)
        total_spacy = len(tokens_spacy)
        
        # Exibe no Text do spaCy
        spacy_texto.delete("1.0", tk.END)
        spacy_texto.insert(tk.END, resultado_spacy)
        
        # Atualiza e exibe o total de tokens spaCy
        spacy_total.config(text=f"Total de tokens: {total_spacy}")
        spacy_total.pack(padx=5, pady=5)
        
    except Exception as e:
        erros.append(f"spaCy: {str(e)}")
    
    # Exibe mensagens de erro se houver
    if erros:
        messagebox.showwarning("Aviso", "Erros durante o processamento:\n" + "\n".join(erros),
                             parent=janelaPrincipal)
    else:
        messagebox.showinfo("Sucesso", "Tokenização realizada com sucesso em NLTK e spaCy!",
                          parent=janelaPrincipal)

def analisar_sentimento():
    """Analisa o sentimento do texto usando spacytextblob"""
    # Verifica se há modelo spaCy carregado
    if not hasattr(selecionar_modelo_spacy, 'nlp') or selecionar_modelo_spacy.nlp is None:
        messagebox.showwarning(
            "Modelo não carregado",
            "É necessário selecionar um modelo spaCy no menu Configurações antes de analisar sentimento.",
            parent=janelaPrincipal
        )
        return
    
    # Verifica qual aba está ativa no notebook de texto
    aba_atual = texto_notebook.select()
    
    if aba_atual == str(frame_texto):
        texto = Texto_texto.get("1.0", tk.END).strip()
    else:  # frame_wiki
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            texto = wk_texto1.get("1.0", tk.END).strip()
        else:  # tab_conteudo
            texto = wk_texto2.get("1.0", tk.END).strip()
    
    if not texto:
        messagebox.showwarning("Texto vazio", 
                              "Não há texto para analisar. Insira um texto ou busque na Wikipedia.",
                              parent=janelaPrincipal)
        return
    
    try:
        nlp = selecionar_modelo_spacy.nlp
        resultado = ferramentas_spacy.analisar_sentimento(texto, nlp)
        polaridade = resultado['polaridade']
        subjetividade = resultado['subjetividade']
        
        # Atualiza os labels com os resultados
        mc_etq_polaridade.config(text=f"Polaridade: {polaridade} {'(Positivo)' if polaridade > 0.1 else '(Negativo)' if polaridade < -0.1 else '(Neutro)'}")
        mc_etq_subjetividade.config(text=f"Subjetividade: {subjetividade}")
        
        # Mostra os labels
        mc_etiqueta_frame1.pack_forget()
        mc_botao_tokenizar.pack_forget()
        mc_etq_polaridade.pack(padx=5, pady=5)
        mc_etq_subjetividade.pack(padx=5, pady=5)
        mc_etiqueta_frame1.pack(pady=10)
        mc_botao_tokenizar.pack(pady=10)
        
        messagebox.showinfo("Análise Concluída", 
                           f"Análise de sentimento realizada com sucesso!\n\nPolaridade: {polaridade}\nSubjetividade: {subjetividade}",
                           parent=janelaPrincipal)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro na análise de sentimento: {str(e)}", parent=janelaPrincipal)

def carregar_texto_corpus(texto, corpus_nome, arquivo):
    """Callback para carregar texto de corpus no Text widget"""
    # Mostra aba "Personalizada" ao carregar corpus
    texto_notebook.select(frame_texto)
    
    # Substitui o conteúdo do Text
    Texto_texto.delete("1.0", tk.END)
    Texto_texto.insert(tk.END, texto)
    
    # Atualiza contador de caracteres
    atualizar_contador_texto()
    
    messagebox.showinfo("Corpus carregado", 
                       f"Texto carregado com sucesso!\n\nCorpus: {corpus_nome}\nArquivo: {arquivo}",
                       parent=janelaPrincipal)

def wk_buscar():
    global USER_AGENT, wk_lg
    # Verifica se USER_AGENT ou wk_lg estão vazios
    if not USER_AGENT or not wk_lg:
        messagebox.showwarning("Configuração necessária", 
                              "É preciso configurar a API da Wikipedia no menu Configurações!")
        return
    
    # Verifica se a entrada está vazia
    if not wk_entrada1.get().strip():
        messagebox.showwarning("Campo vazio", 
                              "Por favor, digite o título da página da Wikipedia!")
        return
    
    try:
        page = wiki.page(wk_entrada1.get())
        
        # Verifica se a página existe
        if not page.exists():
            messagebox.showwarning("Página não encontrada", 
                                  f"A página '{wk_entrada1.get()}' não foi encontrada na Wikipedia!")
            return
        
        # Preenche aba Resumo
        wk_texto1.config(state='normal')
        wk_texto1.delete('1.0', tk.END)
        wk_texto1.insert(tk.END, page.summary)
        wk_texto1.config(state='disabled')
        wk_fonte.config(state='normal')
        wk_fonte.delete(0, tk.END)
        wk_fonte.insert(tk.END, page.fullurl)
        wk_fonte.config(state='readonly')
        
        # Preenche aba Conteúdo
        wk_texto2.config(state='normal')
        wk_texto2.delete('1.0', tk.END)
        wk_texto2.insert(tk.END, page.text)
        wk_texto2.config(state='disabled')
        
        # Atualiza contadores
        atualizar_contador_resumo()
        atualizar_contador_conteudo()
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao buscar a página:\n{str(e)}")
try:
    janelaPrincipal = tb.Window(themename="cosmo")
except Exception:
    janelaPrincipal = tk.Tk()

janelaPrincipal.title("Ferramenta de Processamento de Linguagem Natural")
janelaPrincipal.geometry("1000x800")
janelaPrincipal.update_idletasks()
x = (janelaPrincipal.winfo_screenwidth() // 2) - 450
y = (janelaPrincipal.winfo_screenheight() // 2) - 350
janelaPrincipal.geometry(f"900x700+{x}+{y}")

# Carrega configurações salvas do arquivo config.ini
def carregar_configuracoes_salvas():
    """Carrega as configurações salvas e aplica ao programa"""
    global USER_AGENT, wk_lg, wiki
    
    config = configuracao.carregar_configuracoes()
    
    # Carrega configurações da Wikipedia
    if config['wiki_user_agent']:
        USER_AGENT = config['wiki_user_agent']
    if config['wiki_idioma']:
        wk_lg = config['wiki_idioma']
    
    # Recria objeto Wikipedia se ambos estiverem definidos
    if USER_AGENT and wk_lg:
        wiki = wikipediaapi.Wikipedia(language=wk_lg, user_agent=USER_AGENT)
    
    # Carrega modelo spaCy se configurado
    if config['spacy_modelo']:
        try:
            import spacy
            selecionar_modelo_spacy.nlp = spacy.load(config['spacy_modelo'])
            selecionar_modelo_spacy.modelo = config['spacy_modelo']
        except Exception as e:
            print(f"Erro ao carregar modelo spaCy salvo: {e}")

# Executa o carregamento das configurações
carregar_configuracoes_salvas()

# Cria a barra de menu
menu_bar = tk.Menu(janelaPrincipal)
janelaPrincipal.config(menu=menu_bar)

# Cria um menu "Arquivo"
arquivo_menu = tk.Menu(menu_bar, tearoff=0)
arquivo_menu.add_command(label="Abrir Arquivo", accelerator="Ctrl+O", command=abrir_arquivo)
janelaPrincipal.bind("<Control-o>", lambda event: abrir_arquivo())
arquivo_menu.add_separator()  # linha separadora
arquivo_menu.add_command(label="Sair")
menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)

# Cria um menu "Corpora"
corpora_menu = tk.Menu(menu_bar, tearoff=0)
corpora_menu.add_command(label="Selecionar Corpus do NLTK", 
                        command=lambda: ferramentas_nltk.janela_selecionar_corpora(janelaPrincipal, carregar_texto_corpus))
menu_bar.add_cascade(label="Corpora", menu=corpora_menu)

#Cria um menu "Configurações"
config_menu = tk.Menu(menu_bar, tearoff=0)
config_menu.add_command(label="Configurar API da Wikipedia", command=lambda: configurar_wiki.janela_wkcfg(janelaPrincipal, atualizar_config_wiki, USER_AGENT))
config_menu.add_command(label="Selecionar Modelo SpaCy", command=lambda: selecionar_modelo_spacy.abrir_janela_selecionar_modelo(janelaPrincipal))
menu_bar.add_cascade(label="Configurações", menu=config_menu)

# Cria um menu "Ajuda"
ajuda_menu = tk.Menu(menu_bar, tearoff=0)
ajuda_menu.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", "Exemplo de menu Tkinter"))
menu_bar.add_cascade(label="Ajuda", menu=ajuda_menu)

# Container principal com dois notebooks e um espaço central para botões
container_principal = tk2.Frame(janelaPrincipal)
container_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Notebook esquerdo: Personalizada e Wikipedia
texto_notebook = tk2.Notebook(container_principal)
texto_notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

# Espaço central para botões futuros
menu_central = tk2.Frame(container_principal)
menu_central.pack(side=tk.LEFT, padx=5, expand=True)

# Variáveis de controle
tipo_tokenizacao = tk.IntVar(value=1)  # 1=palavras, 2=frases
incluir_stopwords = tk.BooleanVar(value=False)
tokenizar_types = tk.BooleanVar(value=False)
idioma_stopwords = tk.StringVar(value='portuguese')  # 'english' ou 'portuguese'

def atualizar_estado_checkbuttons():
    """Bloqueia checkbuttons quando tokenizar em frases está selecionado"""
    if tipo_tokenizacao.get() == 2:  # Tokenizar em frases
        mc_check1.config(state='disabled')
        mc_check2.config(state='disabled')
        # Esconde os radiobuttons de idioma
        mc_radio_pt.pack_forget()
        mc_radio_en.pack_forget()
    else:  # Tokenizar em palavras
        mc_check1.config(state='normal')
        mc_check2.config(state='normal')
        # Atualiza visibilidade dos radiobuttons de idioma
        atualizar_visibilidade_idioma()

def atualizar_visibilidade_idioma():
    """Mostra/oculta radiobuttons de idioma baseado no estado do checkbox de stopwords"""
    if incluir_stopwords.get():  # Se o checkbox estiver marcado (incluir stopwords)
        # Remove e reinsere mc_check2 para garantir ordem correta
        mc_check2.pack_forget()
        mc_radio_pt.pack(anchor='w', padx=20, pady=2)
        mc_radio_en.pack(anchor='w', padx=20, pady=2)
        mc_check2.pack(anchor='w', padx=10, pady=5)
    else:
        mc_radio_pt.pack_forget()
        mc_radio_en.pack_forget()

def verificar_disponibilidade_frases():
    """Verifica se tokenizar em frases pode ser selecionado"""
    global texto_foi_limpo
    if texto_foi_limpo and tipo_tokenizacao.get() == 2:
        messagebox.showwarning("Opção indisponível",
                              "Tokenizar em frases não está disponível após limpar o texto.",
                              parent=janelaPrincipal)
        tipo_tokenizacao.set(1)  # Volta para tokenizar em palavras
        atualizar_estado_checkbuttons()

mc_botao_anlsnt = tk2.Button(menu_central, text="Análise de Sentimentos", command=analisar_sentimento)
mc_botao_anlsnt.pack(pady=10)
mc_etq_polaridade = tk2.Label(menu_central, text="Polaridade: --", foreground="blue")
mc_etq_subjetividade = tk2.Label(menu_central, text="Subjetividade: --", foreground="blue")
mc_etq_polaridade.pack_forget()
mc_etq_subjetividade.pack_forget()
ToolTip(mc_etq_polaridade, "Polaridade indica se o texto é positivo, negativo ou neutro")
ToolTip(mc_etq_subjetividade, "A subjetividade indica se o texto expressa opinião (maior valor) ou fato (menor valor)")
mc_etiqueta_frame1 = tk2.LabelFrame(menu_central, text="Escolha o tipo de tokenização:")
mc_etiqueta_frame1.pack(pady=10)
mc_radio1 = tk2.Radiobutton(mc_etiqueta_frame1, text="Tokenizar em palavras",
                            variable=tipo_tokenizacao, value=1,
                            command=atualizar_estado_checkbuttons)
mc_radio1.pack(anchor='w', padx=10, pady=5)
mc_radio2 = tk2.Radiobutton(mc_etiqueta_frame1, text="Tokenizar em frases",
                            variable=tipo_tokenizacao, value=2,
                            command=lambda: [verificar_disponibilidade_frases(), atualizar_estado_checkbuttons()])
mc_radio2.pack(anchor='w', padx=10, pady=5)
mc_check1 = tk2.Checkbutton(mc_etiqueta_frame1, text="Incluir stopwords",
                            variable=incluir_stopwords,
                            command=atualizar_visibilidade_idioma)
mc_check1.pack(anchor='w', padx=10, pady=5)
ToolTip(mc_check1, "Stopwords são palavras de alta frequência sem muito conteúdo semântico")

# Radiobuttons para seleção de idioma das stopwords (inicialmente ocultos)
mc_radio_pt = tk2.Radiobutton(mc_etiqueta_frame1, text="Do português",
                              variable=idioma_stopwords, value='portuguese')
mc_radio_en = tk2.Radiobutton(mc_etiqueta_frame1, text="Do inglês",
                              variable=idioma_stopwords, value='english')

mc_check2 = tk2.Checkbutton(mc_etiqueta_frame1, text="Tokenizar types",
                            variable=tokenizar_types)
ToolTip(mc_check2, "Type é uma forma lexical distinta (cada palavra única)")
mc_check2.pack(anchor='w', padx=10, pady=5)


mc_botao_tokenizar = tk2.Button(menu_central, text="Tokenizar", command=processar_tokenizacao)
mc_botao_tokenizar.pack(pady=10)
ToolTip(mc_botao_tokenizar, "Tokenizar o texto selecionado")


# Notebook direito: NLTK e spaCy
nlp_container = tk2.Frame(container_principal)
nlp_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

nlp_notebook = tk2.Notebook(nlp_container)
nlp_notebook.pack(fill=tk.BOTH, expand=True)

# Mantém os notebooks com larguras iguais mesmo ao redimensionar
def equalizar_larguras(event=None):
    largura_total = container_principal.winfo_width()
    largura_toolbar = menu_central.winfo_width()
    largura_util = max(largura_total - largura_toolbar - 10, 100)
    metade = max(largura_util // 2, 100)
    texto_notebook.configure(width=metade)
    nlp_notebook.configure(width=metade)

container_principal.bind("<Configure>", equalizar_larguras)

# Aba NLTK
tab_nltk = tk2.Frame(nlp_notebook)
nltk_etiqueta = tk2.Label(tab_nltk, text="Processamento com NLTK")
nltk_etiqueta.pack(padx=5, pady=5)
nltk_texto = tk.Text(tab_nltk)
nltk_texto.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
nltk_total = tk2.Label(tab_nltk, text="")

# Aba spaCy
tab_spacy = tk2.Frame(nlp_notebook)
spacy_etiqueta = tk2.Label(tab_spacy, text="Processamento com spaCy")
spacy_etiqueta.pack(padx=5, pady=5)
spacy_texto = tk.Text(tab_spacy)
spacy_texto.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
spacy_total = tk2.Label(tab_spacy, text="")

nlp_notebook.add(tab_nltk, text="NLTK")
nlp_notebook.add(tab_spacy, text="spaCy")

# Frame de botões fora das abas, mas dentro do nlp_container (para salvar resultados de ambas as abas)
nlp_conteudo_frame = tk2.Frame(nlp_container)
nlp_conteudo_frame.pack(anchor='center', pady=5)
nlp_botao1 = tk2.Button(nlp_conteudo_frame, text="Salvar como TXT")
nlp_botao1.pack(side=tk.LEFT, padx=10)
nlp_botao2 = tk2.Button(nlp_conteudo_frame, text="Salvar como CSV")
nlp_botao2.pack(side=tk.LEFT, padx=10)
nlp_botao3 = tk2.Button(nlp_conteudo_frame, text="Salvar como JSON")
nlp_botao3.pack(side=tk.LEFT, padx=10)

# Frame para Texto (aba Personalizada)
frame_texto = tk2.Frame(texto_notebook)
texto_etiqueta1 = tk2.Label(frame_texto, text="Insira o texto ou importe um txt:")
Texto_texto = tk.Text(frame_texto)

# Frame para botões da aba Personalizada (botões serão criados depois que as funções forem definidas)
texto_botoes_frame = tk2.Frame(frame_texto)

texto_contador = tk2.Label(frame_texto, text="Caracteres: 0")

def limpar_texto():
    global texto_foi_limpo, texto_antes_limpar
    
    # Verifica qual aba está ativa
    aba_atual = texto_notebook.select()
    if aba_atual == str(frame_texto):
        widget_texto = Texto_texto
        conteudo = widget_texto.get("1.0", tk.END).strip()
    else:  # frame_wiki - verifica qual sub-aba
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            widget_texto = wk_texto1
        else:  # tab_conteudo
            widget_texto = wk_texto2
        widget_texto.config(state='normal')
        conteudo = widget_texto.get("1.0", tk.END).strip()
    
    # Valida se há texto para limpar
    if not conteudo:
        if aba_atual != str(frame_texto):
            widget_texto.config(state='disabled')
        messagebox.showwarning(
            "Texto vazio",
            "Não há texto para limpar.",
            parent=janelaPrincipal
        )
        return
    
    confirmar = messagebox.askyesno(
        "Confirmar limpeza",
        "A limpeza removerá todos os sinais de pontuação e deixará todas as letras em minúscula.\n\nDeseja continuar?",
        parent=janelaPrincipal
    )
    if not confirmar:
        if aba_atual != str(frame_texto):
            widget_texto.config(state='disabled')
        return
    
    # Armazena o texto antes de limpar
    texto_antes_limpar = conteudo

    sem_pontuacao = re.sub(r"[^\w\s]", "", conteudo)
    resultado = sem_pontuacao.lower()
    widget_texto.delete("1.0", tk.END)
    widget_texto.insert(tk.END, resultado)

    # Se for Wikipedia, volta para disabled
    if aba_atual != str(frame_texto):
        widget_texto.config(state='disabled')
    
    # Atualiza contadores apropriados
    if aba_atual == str(frame_texto):
        atualizar_contador_texto()
    else:  # frame_wiki
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            atualizar_contador_resumo()
        else:
            atualizar_contador_conteudo()
    
    # Marca que o texto foi limpo e bloqueia tokenização em frases
    texto_foi_limpo = True
    mc_radio2.config(state='disabled')
    if tipo_tokenizacao.get() == 2:
        tipo_tokenizacao.set(1)
        atualizar_estado_checkbuttons()
    
    # Alterna botões: oculta Limpar e mostra Restaurar
    if aba_atual == str(frame_texto):
        texto_botao_limpar.pack_forget()
        texto_botao_restaurar.pack(side=tk.LEFT, padx=5, before=texto_botao_limitar)
    else:
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            wk_botao2.pack_forget()
            wk_botao_restaurar_resumo.pack(side=tk.RIGHT, padx=2, after=wk_etiqueta2)
        else:
            wk_botao_conteudo_limpar.pack_forget()
            wk_botao_restaurar_conteudo.pack(side=tk.RIGHT, padx=2, after=wk_etiqueta_conteudo)

def restaurar_texto():
    """Restaura o texto antes da limpeza"""
    global texto_foi_limpo, texto_antes_limpar
    
    # Verifica se há texto armazenado
    if texto_antes_limpar is None:
        messagebox.showwarning("Sem texto original",
                              "Não há texto original para restaurar.",
                              parent=janelaPrincipal)
        return
    
    # Verifica qual aba está ativa
    aba_atual = texto_notebook.select()
    if aba_atual == str(frame_texto):
        Texto_texto.delete("1.0", tk.END)
        Texto_texto.insert(tk.END, texto_antes_limpar)
        atualizar_contador_texto()
    else:  # frame_wiki
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            wk_texto1.config(state='normal')
            wk_texto1.delete("1.0", tk.END)
            wk_texto1.insert(tk.END, texto_antes_limpar)
            wk_texto1.config(state='disabled')
            atualizar_contador_resumo()
        else:  # tab_conteudo
            wk_texto2.config(state='normal')
            wk_texto2.delete("1.0", tk.END)
            wk_texto2.insert(tk.END, texto_antes_limpar)
            wk_texto2.config(state='disabled')
            atualizar_contador_conteudo()
    
    # Limpa as variáveis
    texto_foi_limpo = False
    texto_antes_limpar = None
    
    # Reativa tokenização em frases
    mc_radio2.config(state='normal')
    
    # Alterna botões: oculta Restaurar e mostra Limpar
    if aba_atual == str(frame_texto):
        texto_botao_restaurar.pack_forget()
        texto_botao_limpar.pack(side=tk.LEFT, padx=5, before=texto_botao_limitar)
    else:
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            wk_botao_restaurar_resumo.pack_forget()
            wk_botao2.pack(side=tk.RIGHT, padx=2, after=wk_etiqueta2)
        else:
            wk_botao_restaurar_conteudo.pack_forget()
            wk_botao_conteudo_limpar.pack(side=tk.RIGHT, padx=2, after=wk_etiqueta_conteudo)

# Cria os botões da aba Personalizada após as funções estarem definidas
texto_botao_limpar = tk2.Button(texto_botoes_frame, text="Limpar Texto", command=limpar_texto)
texto_botao_restaurar = tk2.Button(texto_botoes_frame, text="Restaurar Texto", command=restaurar_texto)
texto_botao_limitar = tk2.Button(texto_botoes_frame, text="Limitar Caracteres", command=definir_limites_caracteres)
texto_botao_resetar = tk2.Button(texto_botoes_frame, text="Remover Limites", command=resetar_limites)

# Frame para Wikipedia com busca e sub-abas (Resumo e Conteúdo)
frame_wiki = tk2.Frame(texto_notebook)
wk_etiqueta1 = tk2.Label(frame_wiki, text="Digite o título da página da Wikipedia:", justify="center")
wk_entrada1 = tk2.Entry(frame_wiki, width=30)
wk_botao1 = tk2.Button(frame_wiki, text="Buscar", command=wk_buscar)
wk_etiqueta1.pack(padx=5, pady=(5, 2))
wk_entrada1.pack(padx=5, pady=2)
wk_botao1.pack(padx=5, pady=2)
ToolTip(wk_botao1, "Certifique-se de incluir inicial maiúscula e acentuação correta.")

# Sub-notebook para Resumo e Conteúdo
wiki_sub_notebook = tk2.Notebook(frame_wiki)
wiki_sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Aba Resumo
tab_resumo = tk2.Frame(wiki_sub_notebook)
resumo_header = tk2.Frame(tab_resumo)
wk_etiqueta2 = tk2.Label(resumo_header, text="Resumo da página:")
wk_botao2 = tk2.Button(resumo_header, text="Limpar Texto", command=limpar_texto)
wk_botao_restaurar_resumo = tk2.Button(resumo_header, text="Restaurar Texto", command=restaurar_texto)
wk_botao_limitar_resumo = tk2.Button(resumo_header, text="Limitar Caracteres", command=definir_limites_caracteres)
wk_botao_resetar_resumo = tk2.Button(resumo_header, text="Remover Limites", command=resetar_limites)
wk_etiqueta2.pack(side=tk.LEFT)
wk_botao_resetar_resumo.pack(side=tk.RIGHT, padx=2)
wk_botao_limitar_resumo.pack(side=tk.RIGHT, padx=2)
wk_botao_restaurar_resumo.pack(side=tk.RIGHT, padx=2)
wk_botao2.pack(side=tk.RIGHT, padx=2)
# Botões começam todos visíveis mas serão gerenciados pela lógica
wk_botao_restaurar_resumo.pack_forget()  # Começa oculto
wk_botao_resetar_resumo.pack_forget()  # Começa oculto
resumo_header.pack(fill=tk.X, padx=5, pady=(5, 2))

wk_texto1 = tk.Text(tab_resumo, state='disabled')
wk_texto1.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

wk_contador_resumo = tk2.Label(tab_resumo, text="Caracteres: 0")
# Contador começa oculto, só aparece quando houver conteúdo

# Aba Conteúdo
tab_conteudo = tk2.Frame(wiki_sub_notebook)
conteudo_header = tk2.Frame(tab_conteudo)
wk_etiqueta_conteudo = tk2.Label(conteudo_header, text="Conteúdo completo:")
wk_botao_conteudo_limpar = tk2.Button(conteudo_header, text="Limpar Texto", command=limpar_texto)
wk_botao_restaurar_conteudo = tk2.Button(conteudo_header, text="Restaurar Texto", command=restaurar_texto)
wk_botao_limitar_conteudo = tk2.Button(conteudo_header, text="Limitar Caracteres", command=definir_limites_caracteres)
wk_botao_resetar_conteudo = tk2.Button(conteudo_header, text="Remover Limites", command=resetar_limites)
wk_etiqueta_conteudo.pack(side=tk.LEFT)
wk_botao_resetar_conteudo.pack(side=tk.RIGHT, padx=2)
wk_botao_limitar_conteudo.pack(side=tk.RIGHT, padx=2)
wk_botao_restaurar_conteudo.pack(side=tk.RIGHT, padx=2)
wk_botao_conteudo_limpar.pack(side=tk.RIGHT, padx=2)
# Botões começam todos visíveis mas serão gerenciados pela lógica
wk_botao_restaurar_conteudo.pack_forget()  # Começa oculto
wk_botao_resetar_conteudo.pack_forget()  # Começa oculto
conteudo_header.pack(fill=tk.X, padx=5, pady=(5, 2))

wk_texto2 = tk.Text(tab_conteudo, state='disabled')
wk_texto2.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

wk_contador_conteudo = tk2.Label(tab_conteudo, text="Caracteres: 0")
# Contador começa oculto, só aparece quando houver conteúdo

wiki_sub_notebook.add(tab_resumo, text="Resumo")
wiki_sub_notebook.add(tab_conteudo, text="Conteúdo")

# Rótulo e entrada de fonte em frame_wiki
wk_etiqueta3 = tk2.Label(frame_wiki, text="Fonte:")
wk_fonte = tk2.Entry(frame_wiki, width=50, state='readonly')

wk_etiqueta3.pack(side=tk.LEFT, pady=(5, 2))
wk_fonte.pack(side=tk.LEFT, padx=5, pady=2)
# Contador começa oculto, só aparece quando houver conteúdo

# Adiciona abas ao notebook
texto_notebook.add(frame_texto, text="Personalizada")
texto_notebook.add(frame_wiki, text="Wikipedia")

# Layout inicial da aba Personalizada
texto_etiqueta1.pack(padx=5, pady=5)
Texto_texto.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

# Frame de botões da aba Personalizada
texto_botoes_frame.pack(pady=5)
texto_botao_resetar.pack(side=tk.LEFT, padx=5)
texto_botao_limitar.pack(side=tk.LEFT, padx=5)
texto_botao_restaurar.pack(side=tk.LEFT, padx=5)
texto_botao_limpar.pack(side=tk.LEFT, padx=5)
# Oculta botões que começam invisíveis
texto_botao_restaurar.pack_forget()
texto_botao_resetar.pack_forget()
# texto_contador começa oculto, só aparece quando houver conteúdo

# Vincula eventos de atualização para contadores
Texto_texto.bind("<KeyRelease>", atualizar_contador_texto)
Texto_texto.bind("<<Modified>>", atualizar_contador_texto)

janelaPrincipal.mainloop()