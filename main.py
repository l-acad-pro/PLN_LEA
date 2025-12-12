"""
Ferramenta de Processamento de Linguagem Natural (PLN)
Aplicação GUI para tokenização, lematização, etiquetagem POS e análise de sentimento.
Utiliza NLTK e spaCy para processamento de texto em português e inglês.
"""

import wikipediaapi
import re
import sys
from tkinter import messagebox, filedialog, simpledialog
import tkinter as tk
import tkinter.ttk as tk2
import csv
import json
import ttkbootstrap as tb
from modulos import selecionar_modelo_spacy, configurar_wiki, ferramentas_nltk, ferramentas_spacy, configuracao, recursos

# Configura NLTK para funcionar com PyInstaller
recursos.configurar_nltk_data()

# ===== CONFIGURAÇÕES GLOBAIS =====
AGENTE_USUARIO = None
wiki_idioma = None
wiki = None

# Controle de estado do texto por aba
texto_foi_limpo_entrada = False
texto_foi_limpo_resumo = False
texto_foi_limpo_conteudo = False
texto_antes_limpar_entrada = None
texto_antes_limpar_resumo = None
texto_antes_limpar_conteudo = None
limite_inicio = None
limite_fim = None
texto_original = None

# Variáveis para controle do processamento spaCy
spacy_processado_completo = False
spacy_dados_processados = []


# ===== CLASSE TOOLTIP =====
class Dica:
    """Exibe tooltip ao passar o mouse sobre um widget"""
    
    def __init__(self, widget, texto, atraso=0.5):
        self.widget = widget
        self.texto = texto
        self.atraso = int(atraso * 1000)
        self.janela_dica = None
        self.id_apos = None
        widget.bind("<Enter>", self.agendar)
        widget.bind("<Leave>", self.ocultar_dica)

    def agendar(self, event=None):
        """Agenda exibição da dica após o atraso"""
        self.id_apos = self.widget.after(self.atraso, self.exibir_dica)

    def exibir_dica(self, event=None):
        """Exibe a janela de dica"""
        if self.janela_dica or not self.texto:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.janela_dica = jd = tk.Toplevel(self.widget)
        jd.wm_overrideredirect(True)
        jd.wm_geometry(f"+{x}+{y}")
        etq = tk.Label(
            jd,
            text=self.texto,
            justify="left",
            background="#f8f9fa",
            foreground="#222",
            relief="solid",
            borderwidth=1,
            padx=8, pady=4,
            wraplength=320
        )
        etq.pack(ipadx=1)

    def ocultar_dica(self, event=None):
        """Oculta a janela de dica"""
        if self.id_apos:
            self.widget.after_cancel(self.id_apos)
            self.id_apos = None
        if self.janela_dica:
            self.janela_dica.destroy()
            self.janela_dica = None


# ===== FUNÇÕES UTILITÁRIAS =====
def fechar_programa():
    """Encerra o programa de forma segura"""
    janela_principal.destroy()
    sys.exit(0)


def atualizar_config_wiki(agente_usuario, idioma, mostrar_msg=True):
    """Atualiza configurações da Wikipedia API e salva no arquivo"""
    global AGENTE_USUARIO, wiki_idioma, wiki
    
    if idioma:
        wiki_idioma = idioma
    if agente_usuario:
        AGENTE_USUARIO = agente_usuario

    if AGENTE_USUARIO and wiki_idioma:
        wiki = wikipediaapi.Wikipedia(language=wiki_idioma, user_agent=AGENTE_USUARIO)
        configuracao.salvar_configuracoes(wiki_user_agent=AGENTE_USUARIO, wiki_idioma=wiki_idioma)
        if mostrar_msg:
            messagebox.showinfo("Sucesso", f"Configurações atualizadas!\nIdioma: {wiki_idioma}\nUser Agent: {AGENTE_USUARIO}")


def ocultar_etqs_sentimento():
    """Oculta os labels de análise de sentimento"""
    try:
        mc_etq_polaridade.pack_forget()
        mc_etq_subjetividade.pack_forget()
    except NameError:
        pass

def resetar_estado_texto(aba="entrada"):
    """Reseta o estado de limpeza e limites de texto para uma aba específica ou todas"""
    global texto_foi_limpo_entrada, texto_foi_limpo_resumo, texto_foi_limpo_conteudo
    global texto_antes_limpar_entrada, texto_antes_limpar_resumo, texto_antes_limpar_conteudo
    global limite_inicio, limite_fim, texto_original
    
    limite_inicio = None
    limite_fim = None
    texto_original = None
    
    try:
        if aba == "entrada" or aba == "todas":
            texto_foi_limpo_entrada = False
            texto_antes_limpar_entrada = None
            texto_btn_limpar.config(text="Limpar Texto", command=limpar_texto)
            texto_btn_limitar.config(text="Limitar Caracteres", command=definir_limites_caracteres)
        if aba == "resumo" or aba == "todas":
            texto_foi_limpo_resumo = False
            texto_antes_limpar_resumo = None
            wk_btn_limpar_resumo.config(text="Limpar Texto", command=limpar_texto)
            wk_btn_limitar_resumo.config(text="Limitar Caracteres", command=definir_limites_caracteres)
        if aba == "conteudo" or aba == "todas":
            texto_foi_limpo_conteudo = False
            texto_antes_limpar_conteudo = None
            wk_btn_limpar_conteudo.config(text="Limpar Texto", command=limpar_texto)
            wk_btn_limitar_conteudo.config(text="Limitar Caracteres", command=definir_limites_caracteres)
    except NameError:
        pass
    
    # Atualiza estado do radiobutton baseado na aba atual
    atualizar_estado_rd_frases()


def atualizar_estado_rd_frases(event=None):
    """Atualiza o estado do radiobutton 'Tokenizar em frases' baseado na aba/sub-aba ativa"""
    try:
        aba_atual = texto_notebook.select()
        if aba_atual == str(frame_texto):
            # Aba Entrada
            if texto_foi_limpo_entrada:
                mc_rd_frases.config(state='disabled')
                if tipo_tokenizacao.get() == 2:
                    tipo_tokenizacao.set(1)
                    atualizar_estado_checkbuttons()
            else:
                mc_rd_frases.config(state='normal')
        else:
            # Aba Wikipedia
            sub_aba = wiki_sub_notebook.select()
            if sub_aba == str(tab_resumo):
                if texto_foi_limpo_resumo:
                    mc_rd_frases.config(state='disabled')
                    if tipo_tokenizacao.get() == 2:
                        tipo_tokenizacao.set(1)
                        atualizar_estado_checkbuttons()
                else:
                    mc_rd_frases.config(state='normal')
            else:
                if texto_foi_limpo_conteudo:
                    mc_rd_frases.config(state='disabled')
                    if tipo_tokenizacao.get() == 2:
                        tipo_tokenizacao.set(1)
                        atualizar_estado_checkbuttons()
                else:
                    mc_rd_frases.config(state='normal')
    except NameError:
        pass


def atualizar_contador_texto(event=None):
    """Atualiza o contador de caracteres da aba Entrada"""
    ocultar_etqs_sentimento()
    conteudo = texto_text.get("1.0", tk.END)
    total_chars = len(conteudo) - 1
    if total_chars > 0:
        texto_etq_contador.config(text=f"Caracteres: {total_chars}")
        texto_etq_contador.pack(padx=5, pady=2)
    else:
        texto_etq_contador.pack_forget()
    
    # Reseta os botões quando o texto é alterado pelo usuário (via KeyRelease)
    if event and event.type.name == 'KeyRelease':
        resetar_estado_texto("entrada")


def definir_limites_caracteres():
    """Abre diálogo para definir limites de caracteres para processamento"""
    global limite_inicio, limite_fim, texto_original
    
    aba_atual = texto_notebook.select()
    if aba_atual == str(frame_texto):
        conteudo = texto_text.get("1.0", tk.END).strip()
    else:
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            conteudo = wk_text_resumo.get("1.0", tk.END).strip()
        else:
            conteudo = wk_text_conteudo.get("1.0", tk.END).strip()
    
    if not conteudo:
        messagebox.showwarning("Texto vazio", "Não há texto para definir limites.", parent=janela_principal)
        return
    
    texto_original = conteudo
    total_chars = len(conteudo)
    
    inicio = simpledialog.askinteger(
        "Limitador de Caracteres",
        f"Texto possui {total_chars} caracteres.\n\nEm qual caractere o texto deve COMEÇAR?\n(Digite 0 ou 1 para começar do início)",
        parent=janela_principal,
        minvalue=0,
        maxvalue=total_chars
    )
    
    if inicio is None:
        return
    
    inicio = max(0, inicio - 1) if inicio > 0 else 0
    
    fim = simpledialog.askinteger(
        "Limitador de Caracteres",
        f"Em qual caractere o texto deve TERMINAR?\n(Digite {total_chars} para ir até o final)",
        parent=janela_principal,
        minvalue=inicio + 1,
        maxvalue=total_chars
    )
    
    if fim is None:
        return
    
    limite_inicio = inicio
    limite_fim = fim
    fragmento = conteudo[inicio:fim]
    
    if aba_atual == str(frame_texto):
        texto_text.delete("1.0", tk.END)
        texto_text.insert(tk.END, fragmento)
        atualizar_contador_texto()
    else:
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            wk_text_resumo.config(state='normal')
            wk_text_resumo.delete("1.0", tk.END)
            wk_text_resumo.insert(tk.END, fragmento)
            wk_text_resumo.config(state='disabled')
            atualizar_contador_resumo()
        else:
            wk_text_conteudo.config(state='normal')
            wk_text_conteudo.delete("1.0", tk.END)
            wk_text_conteudo.insert(tk.END, fragmento)
            wk_text_conteudo.config(state='disabled')
            atualizar_contador_conteudo()
    
    texto_btn_limitar.config(text="Remover Limites", command=resetar_limites)
    wk_btn_limitar_resumo.config(text="Remover Limites", command=resetar_limites)
    wk_btn_limitar_conteudo.config(text="Remover Limites", command=resetar_limites)
    
    messagebox.showinfo(
        "Limites Aplicados",
        f"O texto foi limitado:\n\nInício: caractere {inicio + 1}\nFim: caractere {fim}\nTotal: {fim - inicio} caracteres",
        parent=janela_principal
    )


def resetar_limites():
    """Remove os limites de caracteres e restaura o texto original"""
    global limite_inicio, limite_fim, texto_original
    
    if texto_original is None:
        messagebox.showwarning("Sem texto original", "Não há texto original para restaurar.", parent=janela_principal)
        return
    
    aba_atual = texto_notebook.select()
    if aba_atual == str(frame_texto):
        texto_text.delete("1.0", tk.END)
        texto_text.insert(tk.END, texto_original)
        atualizar_contador_texto()
    else:
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            wk_text_resumo.config(state='normal')
            wk_text_resumo.delete("1.0", tk.END)
            wk_text_resumo.insert(tk.END, texto_original)
            wk_text_resumo.config(state='disabled')
            atualizar_contador_resumo()
        else:
            wk_text_conteudo.config(state='normal')
            wk_text_conteudo.delete("1.0", tk.END)
            wk_text_conteudo.insert(tk.END, texto_original)
            wk_text_conteudo.config(state='disabled')
            atualizar_contador_conteudo()
    
    limite_inicio = None
    limite_fim = None
    texto_original = None
    
    texto_btn_limitar.config(text="Limitar Caracteres", command=definir_limites_caracteres)
    wk_btn_limitar_resumo.config(text="Limitar Caracteres", command=definir_limites_caracteres)
    wk_btn_limitar_conteudo.config(text="Limitar Caracteres", command=definir_limites_caracteres)
    
    messagebox.showinfo("Limites Removidos", "Os limites de caracteres foram removidos.\nO texto completo será processado.", parent=janela_principal)


def atualizar_contador_resumo(event=None):
    """Atualiza o contador de caracteres da sub-aba Resumo"""
    ocultar_etqs_sentimento()
    conteudo = wk_text_resumo.get("1.0", tk.END)
    total_chars = len(conteudo) - 1
    if total_chars > 0:
        wk_etq_contador_resumo.config(text=f"Caracteres: {total_chars}")
        wk_etq_contador_resumo.pack(padx=5, pady=2)
    else:
        wk_etq_contador_resumo.pack_forget()


def atualizar_contador_conteudo(event=None):
    """Atualiza o contador de caracteres da sub-aba Conteúdo"""
    ocultar_etqs_sentimento()
    conteudo = wk_text_conteudo.get("1.0", tk.END)
    total_chars = len(conteudo) - 1
    if total_chars > 0:
        wk_etq_contador_conteudo.config(text=f"Caracteres: {total_chars}")
        wk_etq_contador_conteudo.pack(padx=5, pady=2)
    else:
        wk_etq_contador_conteudo.pack_forget()


def abrir_arquivo():
    """Abre arquivo de texto e carrega na aba Entrada"""
    caminho = filedialog.askopenfilename(
        title="Selecione um arquivo de texto",
        filetypes=[("Arquivo de texto", "*.txt")],
        parent=janela_principal
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

    texto_notebook.select(frame_texto)
    texto_text.delete("1.0", tk.END)
    texto_text.insert(tk.END, conteudo)
    atualizar_contador_texto()


def processar_tokenizacao(forcar_tokenizacao_simples=False):
    """Tokeniza o texto com NLTK e spaCy, exibindo os resultados
    
    Args:
        forcar_tokenizacao_simples: Se True, ignora checkboxes de lematização/etiquetagem no spaCy
    """
    global limite_inicio, limite_fim, spacy_processado_completo, spacy_dados_processados
    
    if not hasattr(selecionar_modelo_spacy, 'pln') or selecionar_modelo_spacy.pln is None:
        messagebox.showwarning(
            "Modelo não carregado",
            "É necessário selecionar um modelo spaCy no menu Configurações antes de tokenizar.",
            parent=janela_principal
        )
        return
    
    aba_atual = texto_notebook.select()
    
    if aba_atual == str(frame_texto):
        texto = texto_text.get("1.0", tk.END).strip()
    else:
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            texto = wk_text_resumo.get("1.0", tk.END).strip()
        else:
            texto = wk_text_conteudo.get("1.0", tk.END).strip()
    
    if not texto:
        messagebox.showwarning("Texto vazio", "Não há texto para processar. Insira um texto ou busque na Wikipedia.", parent=janela_principal)
        return
    
    if limite_inicio is not None and limite_fim is not None:
        texto = texto[limite_inicio:limite_fim]
    
    erros = []
    total_nltk = 0
    total_spacy = 0
    
    # Processamento com NLTK
    try:
        if tipo_tokenizacao.get() == 2:
            tokens_nltk = ferramentas_nltk.tokenizar_sentencas(texto)
        else:
            tokens_nltk = ferramentas_nltk.tokenizar_texto(texto)
            
            if incluir_stopwords.get():
                tokens_nltk = ferramentas_nltk.remover_stopwords(tokens_nltk, idioma_stopwords.get())
            
            if tokenizar_types.get():
                tokens_nltk = ferramentas_nltk.obter_types(tokens_nltk)
        
        # Formata tokens: por linha ou separados por vírgula
        if tokenizar_linhas.get():
            resultado_nltk = "\n".join(tokens_nltk)
        else:
            resultado_nltk = ferramentas_nltk.formatar_tokens_para_exibicao(tokens_nltk)
        total_nltk = len(tokens_nltk)
        
        nltk_text.config(state='normal')
        nltk_text.delete("1.0", tk.END)
        nltk_text.insert(tk.END, resultado_nltk)
        nltk_text.config(state='disabled')
        
        nltk_etq_total.config(text=f"Total de tokens: {total_nltk}")
        nltk_etq_total.pack(padx=5, pady=5)
        
    except Exception as e:
        erros.append(f"NLTK: {str(e)}")
    
    # Define variáveis de controle para lematização/etiquetagem
    usar_lematizacao = lematizar_spacy.get() and not forcar_tokenizacao_simples
    usar_etiquetagem = etiquetar_spacy.get() and not forcar_tokenizacao_simples
    
    # Processamento com spaCy
    try:
        pln = selecionar_modelo_spacy.pln
        modelo_nome = selecionar_modelo_spacy.modelo if hasattr(selecionar_modelo_spacy, 'modelo') else "Desconhecido"
        
        if usar_lematizacao or usar_etiquetagem:
            spacy_processado_completo = True
            dados = ferramentas_spacy.processar_completo(
                texto, pln,
                lematizar=usar_lematizacao,
                etiquetar=usar_etiquetagem
            )
            # Armazena dados estruturados para salvar em CSV/JSON
            # dados é uma lista de tuplas: (token,) ou (token, lema) ou (token, pos) ou (token, lema, pos)
            spacy_dados_processados = []
            for item in dados:
                dado = {"token": item[0]}
                idx = 1
                if usar_lematizacao:
                    dado["lema"] = item[idx]
                    idx += 1
                if usar_etiquetagem:
                    dado["POS tag"] = item[idx]
                spacy_dados_processados.append(dado)
            
            resultado_spacy = ferramentas_spacy.formatar_processamento_completo(
                dados,
                lematizar=usar_lematizacao,
                etiquetar=usar_etiquetagem
            )
            total_spacy = len(dados)
        else:
            spacy_processado_completo = False
            spacy_dados_processados = []
            tokens_spacy = ferramentas_spacy.tokenizar_texto(texto, pln)
            
            if incluir_stopwords.get():
                tokens_spacy = ferramentas_spacy.remover_stopwords(tokens_spacy, idioma_stopwords.get())
            
            if tokenizar_types.get():
                tokens_spacy = ferramentas_spacy.obter_types(tokens_spacy)
            
            # Formata tokens: por linha ou separados por vírgula
            if tokenizar_linhas.get():
                resultado_spacy = "\n".join(tokens_spacy)
            else:
                resultado_spacy = ferramentas_spacy.formatar_tokens_para_exibicao(tokens_spacy)
            total_spacy = len(tokens_spacy)
        
        spacy_text.config(state='normal')
        spacy_text.delete("1.0", tk.END)
        spacy_text.insert(tk.END, resultado_spacy)
        spacy_text.config(state='disabled')
        
        spacy_etq_total.config(text=f"Total de tokens: {total_spacy}")
        spacy_etq_total.pack(padx=5, pady=5)
        
    except Exception as e:
        erros.append(f"spaCy: {str(e)}")
    
    if erros:
        messagebox.showwarning("Aviso", "Erros durante o processamento:\n" + "\n".join(erros), parent=janela_principal)
    else:
        # Monta mensagem baseada nas opções usadas
        if forcar_tokenizacao_simples:
            msg = "Tokenização realizada com sucesso em NLTK e spaCy!"
        else:
            operacoes = []
            if usar_lematizacao:
                operacoes.append("lematização")
            if usar_etiquetagem:
                operacoes.append("etiquetagem morfossintática")
            if operacoes:
                msg = f"Processamento realizado com sucesso!\n\nOperações: {', '.join(operacoes)}"
            else:
                msg = "Tokenização realizada com sucesso em NLTK e spaCy!"
        messagebox.showinfo("Sucesso", msg, parent=janela_principal)


def analisar_sentimento():
    """Analisa o sentimento do texto usando spacytextblob"""
    if not hasattr(selecionar_modelo_spacy, 'pln') or selecionar_modelo_spacy.pln is None:
        messagebox.showwarning(
            "Modelo não carregado",
            "É necessário selecionar um modelo spaCy no menu Configurações antes de analisar sentimento.",
            parent=janela_principal
        )
        return
    
    aba_atual = texto_notebook.select()
    
    if aba_atual == str(frame_texto):
        texto = texto_text.get("1.0", tk.END).strip()
    else:
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            texto = wk_text_resumo.get("1.0", tk.END).strip()
        else:
            texto = wk_text_conteudo.get("1.0", tk.END).strip()
    
    if not texto:
        messagebox.showwarning("Texto vazio", "Não há texto para analisar. Insira um texto ou busque na Wikipedia.", parent=janela_principal)
        return
    
    try:
        pln = selecionar_modelo_spacy.pln
        resultado = ferramentas_spacy.analisar_sentimento(texto, pln)
        polaridade = resultado['polaridade']
        subjetividade = resultado['subjetividade']
        
        mc_etq_polaridade.config(text=f"Polaridade: {polaridade} {'(Positivo)' if polaridade > 0.1 else '(Negativo)' if polaridade < -0.1 else '(Neutro)'}")
        mc_etq_subjetividade.config(text=f"Subjetividade: {subjetividade}")
        
        mc_frame_tokenizacao.pack_forget()
        mc_btn_tokenizar.pack_forget()
        mc_etq_polaridade.pack(padx=5, pady=5)
        mc_etq_subjetividade.pack(padx=5, pady=5)
        mc_frame_tokenizacao.pack(pady=10)
        mc_btn_tokenizar.pack(pady=10)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na análise de sentimento: {str(e)}", parent=janela_principal)


def carregar_texto_corpus(texto, corpus_nome, arquivo):
    """Callback para carregar texto de corpus no widget Text"""
    texto_notebook.select(frame_texto)
    texto_text.delete("1.0", tk.END)
    texto_text.insert(tk.END, texto)
    atualizar_contador_texto()
    
    messagebox.showinfo("Corpus carregado", f"Texto carregado com sucesso!\n\nCorpus: {corpus_nome}\nArquivo: {arquivo}", parent=janela_principal)


def exibir_pos_tags():
    """Exibe janela com todas as POS tags do spaCy e suas descrições em português"""
    janela_tags = tk.Toplevel(janela_principal)
    janela_tags.title("Etiquetas Morfossintáticas (POS Tags)")
    
    # Calcula metade do tamanho da janela principal
    largura = janela_principal.winfo_width() // 2
    altura = janela_principal.winfo_height() // 2
    
    janela_tags.geometry(f"{largura}x{altura}")
    janela_tags.transient(janela_principal)
    janela_tags.grab_set()
    janela_tags.lift()
    janela_tags.focus_set()
    
    # Centraliza a janela
    janela_tags.update_idletasks()
    x = janela_principal.winfo_x() + (janela_principal.winfo_width() // 2) - (largura // 2)
    y = janela_principal.winfo_y() + (janela_principal.winfo_height() // 2) - (altura // 2)
    janela_tags.geometry(f"+{x}+{y}")
    
    # Frame principal
    frame = tk2.Frame(janela_tags)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Título
    titulo = tk2.Label(frame, text="POS Tags Universais do spaCy", font=("Open Sans", 12, "bold"))
    titulo.pack(pady=(0, 10))
    
    # Descrição
    descricao = tk2.Label(frame, text="Etiquetas utilizadas para classificação morfossintática dos tokens:", font=("Open Sans", 10))
    descricao.pack(pady=(0, 10))
    
    # Frame com scrollbar
    frame_scroll = tk2.Frame(frame)
    frame_scroll.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = tk2.Scrollbar(frame_scroll)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    texto_tags = tk.Text(frame_scroll, wrap=tk.WORD, yscrollcommand=scrollbar.set, state='normal', font=("Open Sans", 10))
    texto_tags.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=texto_tags.yview)
    
    # Configura tag para texto em negrito
    texto_tags.tag_configure("bold", font=("Open Sans", 10, "bold"))
    
    # Lista de POS tags com descrições em português e inglês
    # (tag, nome_pt, nome_en, descricao_pt, exemplo_pt, exemplo_en)
    pos_tags_data = [
        ("ADJ", "Adjetivo", "Adjective", "Palavras que qualificam ou modificam substantivos.", "bonito, grande, feliz", "beautiful, big, happy"),
        ("ADV", "Advérbio", "Adverb", "Palavras que modificam verbos, adjetivos ou outros advérbios.", "rapidamente, muito, aqui", "quickly, very, here"),
        ("ADP", "Adposição (Preposição)", "Adposition", "Palavras que estabelecem relações entre termos.", "de, para, com, em", "of, to, with, in"),
        ("AUX", "Verbo Auxiliar", "Auxiliary Verb", "Verbos que auxiliam outros verbos na formação de tempos compostos.", "ter, haver, ser, estar", "have, be, will, would"),
        ("CCONJ", "Conjunção Coordenativa", "Coordinating Conjunction", "Palavras que conectam elementos de mesma função sintática.", "e, ou, mas, porém", "and, or, but, yet"),
        ("DET", "Determinante", "Determiner", "Palavras que determinam ou especificam substantivos.", "o, a, um, este, meu", "the, a, this, my"),
        ("INTJ", "Interjeição", "Interjection", "Palavras que expressam emoções ou reações.", "ah, oh, ufa, oba", "oh, wow, oops, hey"),
        ("NOUN", "Substantivo", "Noun", "Palavras que nomeiam seres, objetos, lugares ou conceitos.", "casa, pessoa, amor", "house, person, love"),
        ("NUM", "Numeral", "Numeral", "Palavras que indicam quantidade ou ordem.", "um, dois, primeiro", "one, two, first"),
        ("PART", "Partícula", "Particle", "Palavras funcionais que não se encaixam em outras categorias.", "não (em alguns contextos)", "not, 's, n't"),
        ("PRON", "Pronome", "Pronoun", "Palavras que substituem ou acompanham substantivos.", "ele, ela, isso, quem", "he, she, it, who"),
        ("PROPN", "Nome Próprio", "Proper Noun", "Nomes que designam entidades específicas.", "João, São Paulo, Google", "John, New York, Google"),
        ("PUNCT", "Pontuação", "Punctuation", "Sinais de pontuação.", ". , ! ? ; :", ". , ! ? ; :"),
        ("SCONJ", "Conjunção Subordinativa", "Subordinating Conjunction", "Palavras que introduzem orações subordinadas.", "que, se, quando, porque", "that, if, when, because"),
        ("SYM", "Símbolo", "Symbol", "Símbolos não alfabéticos.", "$, %, @, +", "$, %, @, +"),
        ("VERB", "Verbo", "Verb", "Palavras que expressam ações, estados ou processos.", "correr, ser, pensar", "run, be, think"),
        ("X", "Outro", "Other", "Palavras que não se encaixam nas categorias acima.", "palavras estrangeiras", "foreign words, typos"),
        ("SPACE", "Espaço", "Space", "Espaços em branco (geralmente filtrados na tokenização).", "", ""),
    ]
    
    # Insere as tags com formatação
    for tag, nome_pt, nome_en, descricao_tag, exemplo_pt, exemplo_en in pos_tags_data:
        texto_tags.insert(tk.END, f"{tag}: ", "bold")
        texto_tags.insert(tk.END, f"{nome_pt} ({nome_en})\n")
        texto_tags.insert(tk.END, f"    {descricao_tag}\n")
        if exemplo_pt:
            texto_tags.insert(tk.END, f"    Exemplo (PT): {exemplo_pt}\n")
            texto_tags.insert(tk.END, f"    Exemplo (EN): {exemplo_en}\n")
        texto_tags.insert(tk.END, "\n")
    
    texto_tags.config(state='disabled')
    
    # Botão fechar
    btn_fechar = tk2.Button(frame, text="Fechar", command=janela_tags.destroy)
    btn_fechar.pack(pady=10)


def wk_buscar():
    """Busca página na Wikipedia e exibe resumo e conteúdo"""
    global AGENTE_USUARIO, wiki_idioma
    
    if not AGENTE_USUARIO or not wiki_idioma:
        messagebox.showwarning("Configuração necessária", "É preciso configurar a API da Wikipedia no menu Configurações!")
        return
    
    if not wk_ent_busca.get().strip():
        messagebox.showwarning("Campo vazio", "Por favor, digite o título da página da Wikipedia!")
        return
    
    try:
        page = wiki.page(wk_ent_busca.get())
        
        if not page.exists():
            messagebox.showwarning("Página não encontrada", f"A página '{wk_ent_busca.get()}' não foi encontrada na Wikipedia!")
            return
        
        wk_text_resumo.config(state='normal')
        wk_text_resumo.delete('1.0', tk.END)
        wk_text_resumo.insert(tk.END, page.summary)
        wk_text_resumo.config(state='disabled')
        wk_ent_fonte.config(state='normal')
        wk_ent_fonte.delete(0, tk.END)
        wk_ent_fonte.insert(tk.END, page.fullurl)
        wk_ent_fonte.config(state='readonly')
        
        wk_text_conteudo.config(state='normal')
        wk_text_conteudo.delete('1.0', tk.END)
        wk_text_conteudo.insert(tk.END, page.text)
        wk_text_conteudo.config(state='disabled')
        
        atualizar_contador_resumo()
        atualizar_contador_conteudo()
        
        # Reseta os botões da Wikipedia ao buscar novo conteúdo
        resetar_estado_texto("resumo")
        resetar_estado_texto("conteudo")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao buscar a página:\n{str(e)}")


# === INICIALIZAÇÃO DA JANELA PRINCIPAL ===
try:
    janela_principal = tb.Window(themename="cosmo")
except Exception:
    janela_principal = tk.Tk()

janela_principal.title("Ferramenta de Processamento de Linguagem Natural")

# Obtém dimensões da tela e calcula 80%
largura_tela = janela_principal.winfo_screenwidth()
altura_tela = janela_principal.winfo_screenheight()
largura_janela = int(largura_tela * 0.8)
altura_janela = int(altura_tela * 0.8)

# Centraliza a janela na tela
x = (largura_tela - largura_janela) // 2
y = (altura_tela - altura_janela) // 2

janela_principal.geometry(f"{largura_janela}x{altura_janela}+{x}+{y}")


def carregar_configuracoes_salvas():
    """Carrega as configurações salvas e aplica ao programa"""
    global AGENTE_USUARIO, wiki_idioma, wiki
    
    config = configuracao.carregar_configuracoes()
    
    if config['wiki_user_agent']:
        AGENTE_USUARIO = config['wiki_user_agent']
    if config['wiki_idioma']:
        wiki_idioma = config['wiki_idioma']
    
    if AGENTE_USUARIO and wiki_idioma:
        wiki = wikipediaapi.Wikipedia(language=wiki_idioma, user_agent=AGENTE_USUARIO)
    
    if config['spacy_modelo']:
        try:
            # Usa carregamento compatível com PyInstaller
            selecionar_modelo_spacy.pln = recursos.carregar_modelo_spacy(config['spacy_modelo'])
            selecionar_modelo_spacy.modelo = config['spacy_modelo']
        except Exception as e:
            print(f"Erro ao carregar modelo spaCy salvo: {e}")


carregar_configuracoes_salvas()

# === BARRA DE MENU ===
barra_menu = tk.Menu(janela_principal)
janela_principal.config(menu=barra_menu)

menu_arquivo = tk.Menu(barra_menu, tearoff=0)
menu_arquivo.add_command(label="Abrir Arquivo", accelerator="Ctrl+O", command=abrir_arquivo)
janela_principal.bind("<Control-o>", lambda event: abrir_arquivo())
menu_arquivo.add_separator()
menu_arquivo.add_command(label="Sair", accelerator="Alt+F4", command=fechar_programa)
barra_menu.add_cascade(label="Arquivo", menu=menu_arquivo)

menu_corpora = tk.Menu(barra_menu, tearoff=0)
menu_corpora.add_command(label="Selecionar Corpus do NLTK", command=lambda: ferramentas_nltk.janela_selecionar_corpora(janela_principal, carregar_texto_corpus))
barra_menu.add_cascade(label="Corpora", menu=menu_corpora)

menu_config = tk.Menu(barra_menu, tearoff=0)
menu_config.add_command(label="Configurar API da Wikipedia", command=lambda: configurar_wiki.janela_wkcfg(janela_principal, atualizar_config_wiki, AGENTE_USUARIO))
menu_config.add_command(label="Selecionar Modelo SpaCy", command=lambda: selecionar_modelo_spacy.abrir_janela_selecionar_modelo(janela_principal))
barra_menu.add_cascade(label="Configurações", menu=menu_config)

menu_ajuda = tk.Menu(barra_menu, tearoff=0)
menu_ajuda.add_command(label="Etiquetas morfossintáticas (POS tags)", command=exibir_pos_tags)
menu_ajuda.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", "Ferramenta de PLN para TCC"))
barra_menu.add_cascade(label="Ajuda", menu=menu_ajuda)

# === CONTAINER PRINCIPAL ===
container_principal = tk2.Frame(janela_principal)
container_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Notebook esquerdo: Entrada e Wikipedia
texto_notebook = tk2.Notebook(container_principal)
texto_notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

# Menu central para botões
menu_central = tk2.Frame(container_principal)
menu_central.pack(side=tk.LEFT, padx=5, expand=True)

# === VARIÁVEIS DE CONTROLE ===
tipo_tokenizacao = tk.IntVar(value=1)
incluir_stopwords = tk.BooleanVar(value=False)
tokenizar_types = tk.BooleanVar(value=False)
tokenizar_linhas = tk.BooleanVar(value=False)
idioma_stopwords = tk.StringVar(value='portuguese')
lematizar_spacy = tk.BooleanVar(value=False)
etiquetar_spacy = tk.BooleanVar(value=False)


def atualizar_estado_btn_processar():
    """Ativa/desativa o botão Processar baseado nos checkboxes do spaCy"""
    try:
        if lematizar_spacy.get() or etiquetar_spacy.get():
            spacy_btn_processar.config(state='normal')
        else:
            spacy_btn_processar.config(state='disabled')
    except NameError:
        pass


def atualizar_estado_checkbuttons():
    """Bloqueia checkbuttons quando tokenizar em frases está selecionado"""
    if tipo_tokenizacao.get() == 2:
        mc_check_stopwords.config(state='disabled')
        mc_check_types.config(state='disabled')
        mc_rd_portugues.pack_forget()
        mc_rd_ingles.pack_forget()
        try:
            spacy_frame_opcoes.pack_forget()
        except NameError:
            pass
    else:
        mc_check_stopwords.config(state='normal')
        mc_check_types.config(state='normal')
        atualizar_visibilidade_idioma()
        try:
            if not spacy_frame_opcoes.winfo_ismapped():
                spacy_frame_opcoes.pack(padx=5, pady=5, after=spacy_etq_titulo)
        except (NameError, tk.TclError):
            pass


def atualizar_visibilidade_idioma():
    """Mostra/oculta radiobuttons de idioma baseado no checkbox de stopwords"""
    if incluir_stopwords.get():
        mc_check_types.pack_forget()
        mc_rd_portugues.pack(anchor='w', padx=20, pady=2)
        mc_rd_ingles.pack(anchor='w', padx=20, pady=2)
        mc_check_types.pack(anchor='w', padx=10, pady=5)
    else:
        mc_rd_portugues.pack_forget()
        mc_rd_ingles.pack_forget()


def verificar_disponibilidade_frases():
    """Verifica se tokenizar em frases pode ser selecionado"""
    atualizar_estado_rd_frases()


# === WIDGETS DO MENU CENTRAL ===
mc_btn_sentimento = tk2.Button(menu_central, text="Análise de Sentimentos", command=analisar_sentimento)
mc_btn_sentimento.pack(pady=10)
Dica(mc_btn_sentimento, "Analisa a polaridade e subjetividade do texto")

mc_etq_polaridade = tk2.Label(menu_central, text="Polaridade: --", foreground="blue")
mc_etq_subjetividade = tk2.Label(menu_central, text="Subjetividade: --", foreground="blue")
mc_etq_polaridade.pack_forget()
mc_etq_subjetividade.pack_forget()
Dica(mc_etq_polaridade, "Polaridade indica se o texto é positivo, negativo ou neutro")
Dica(mc_etq_subjetividade, "A subjetividade indica se o texto expressa opinião (maior valor) ou fato (menor valor)")

mc_frame_tokenizacao = tk2.LabelFrame(menu_central, text="Escolha o tipo de tokenização:")
mc_frame_tokenizacao.pack(pady=10)

mc_rd_palavras = tk2.Radiobutton(mc_frame_tokenizacao, text="Tokenizar em palavras", variable=tipo_tokenizacao, value=1, command=atualizar_estado_checkbuttons)
mc_rd_palavras.pack(anchor='w', padx=10, pady=5)

mc_rd_frases = tk2.Radiobutton(mc_frame_tokenizacao, text="Tokenizar em frases", variable=tipo_tokenizacao, value=2, command=lambda: [verificar_disponibilidade_frases(), atualizar_estado_checkbuttons()])
mc_rd_frases.pack(anchor='w', padx=10, pady=5)

mc_check_linha = tk2.Checkbutton(mc_frame_tokenizacao, text="Token por linha", variable=tokenizar_linhas)
mc_check_linha.pack(anchor='w', padx=10, pady=5)
Dica(mc_check_linha, "Exibe cada token em uma linha separada ao invés de separados por vírgula")

mc_check_stopwords = tk2.Checkbutton(mc_frame_tokenizacao, text="Incluir stopwords", variable=incluir_stopwords, command=atualizar_visibilidade_idioma)
mc_check_stopwords.pack(anchor='w', padx=10, pady=5)
Dica(mc_check_stopwords, "Stopwords são palavras de alta frequência sem muito conteúdo semântico")

mc_rd_portugues = tk2.Radiobutton(mc_frame_tokenizacao, text="Do português", variable=idioma_stopwords, value='portuguese')
mc_rd_ingles = tk2.Radiobutton(mc_frame_tokenizacao, text="Do inglês", variable=idioma_stopwords, value='english')

mc_check_types = tk2.Checkbutton(mc_frame_tokenizacao, text="Tokenizar types", variable=tokenizar_types)
Dica(mc_check_types, "Type é uma forma lexical distinta (cada palavra única)")
mc_check_types.pack(anchor='w', padx=10, pady=5)

mc_btn_tokenizar = tk2.Button(menu_central, text="Tokenizar", command=lambda: processar_tokenizacao(forcar_tokenizacao_simples=True))
mc_btn_tokenizar.pack(pady=10)
Dica(mc_btn_tokenizar, "Tokenizar é transformar um texto contínuo em partes manipuláveis")

# === NOTEBOOK DE RESULTADOS (NLTK e spaCy) ===
pln_container = tk2.Frame(container_principal)
pln_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

pln_notebook = tk2.Notebook(pln_container)
pln_notebook.pack(fill=tk.BOTH, expand=True)


def equalizar_larguras(event=None):
    """Mantém os notebooks com larguras iguais ao redimensionar"""
    largura_total = container_principal.winfo_width()
    largura_toolbar = menu_central.winfo_width()
    largura_util = max(largura_total - largura_toolbar - 10, 100)
    metade = max(largura_util // 2, 100)
    texto_notebook.configure(width=metade)
    pln_notebook.configure(width=metade)


container_principal.bind("<Configure>", equalizar_larguras)

# Aba NLTK
tab_nltk = tk2.Frame(pln_notebook)
nltk_etq_titulo = tk2.Label(tab_nltk, text="Processamento com NLTK")
nltk_etq_titulo.pack(padx=5, pady=5)
nltk_text = tk.Text(tab_nltk, state='disabled')
nltk_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
nltk_etq_total = tk2.Label(tab_nltk, text="")

# Aba spaCy
tab_spacy = tk2.Frame(pln_notebook)
spacy_etq_titulo = tk2.Label(tab_spacy, text="Processar com spaCy")
spacy_etq_titulo.pack(padx=5, pady=5)

spacy_frame_opcoes = tk2.Frame(tab_spacy)
spacy_frame_opcoes.pack(padx=5, pady=5)

spacy_check_lematizar = tk2.Checkbutton(spacy_frame_opcoes, text="Lematizar", variable=lematizar_spacy, command=atualizar_estado_btn_processar)
spacy_check_lematizar.pack(side=tk.LEFT, padx=5)
Dica(spacy_check_lematizar, "Lematização reduz tokens à sua forma base")

spacy_check_etiquetar = tk2.Checkbutton(spacy_frame_opcoes, text="Etiquetar", variable=etiquetar_spacy, command=atualizar_estado_btn_processar)
spacy_check_etiquetar.pack(side=tk.LEFT, padx=5)
Dica(spacy_check_etiquetar, "Etiquetar (POS tag) atribui categorias gramaticais aos tokens")

spacy_btn_processar = tk2.Button(spacy_frame_opcoes, text="Processar", state='disabled', command=processar_tokenizacao)
spacy_btn_processar.pack(side=tk.LEFT, padx=5)

spacy_text = tk.Text(tab_spacy, state='disabled')
spacy_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
spacy_etq_total = tk2.Label(tab_spacy, text="")

pln_notebook.add(tab_nltk, text="NLTK")
pln_notebook.add(tab_spacy, text="spaCy")

# Variável para controlar se o processamento spaCy foi feito com lematização/etiquetagem
spacy_processado_completo = False
spacy_dados_processados = []  # Armazena os dados estruturados do spaCy


def salvar_resultado():
    """Salva o resultado da aba em destaque (NLTK ou spaCy)"""
    aba_atual = pln_notebook.select()
    
    if aba_atual == str(tab_nltk):
        # Aba NLTK - salvar em .txt
        conteudo = nltk_text.get("1.0", tk.END).strip()
        if not conteudo:
            messagebox.showwarning("Texto vazio", "Não há resultado para salvar.", parent=janela_principal)
            return
        
        caminho = filedialog.asksaveasfilename(
            title="Salvar resultado NLTK",
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt")],
            parent=janela_principal
        )
        if not caminho:
            return
        
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(conteudo)
            messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{caminho}", parent=janela_principal)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{e}", parent=janela_principal)
    
    else:
        # Aba spaCy
        conteudo = spacy_text.get("1.0", tk.END).strip()
        if not conteudo:
            messagebox.showwarning("Texto vazio", "Não há resultado para salvar.", parent=janela_principal)
            return
        
        if spacy_processado_completo and spacy_dados_processados:
            # Processamento com lematização/etiquetagem - salvar em .txt, .csv ou .json
            caminho = filedialog.asksaveasfilename(
                title="Salvar resultado spaCy",
                defaultextension=".txt",
                filetypes=[("Arquivo de texto", "*.txt"), ("Arquivo CSV", "*.csv"), ("Arquivo JSON", "*.json")],
                parent=janela_principal
            )
            if not caminho:
                return
            
            try:
                if caminho.endswith(".json"):
                    with open(caminho, "w", encoding="utf-8") as f:
                        json.dump(spacy_dados_processados, f, ensure_ascii=False, indent=2)
                elif caminho.endswith(".csv"):
                    # CSV com cabeçalhos baseados nos dados disponíveis
                    with open(caminho, "w", encoding="utf-8", newline='') as f:
                        if spacy_dados_processados:
                            cabecalhos = list(spacy_dados_processados[0].keys())
                            escritor = csv.DictWriter(f, fieldnames=cabecalhos)
                            escritor.writeheader()
                            escritor.writerows(spacy_dados_processados)
                else:
                    # Salvar como .txt
                    with open(caminho, "w", encoding="utf-8") as f:
                        f.write(conteudo)
                
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{caminho}", parent=janela_principal)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{e}", parent=janela_principal)
        else:
            # Tokenização simples - salvar em .txt
            caminho = filedialog.asksaveasfilename(
                title="Salvar resultado spaCy",
                defaultextension=".txt",
                filetypes=[("Arquivo de texto", "*.txt")],
                parent=janela_principal
            )
            if not caminho:
                return
            
            try:
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(conteudo)
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{caminho}", parent=janela_principal)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{e}", parent=janela_principal)


def atualizar_dica_salvar(event=None):
    """Atualiza a dica do botão Salvar baseado na aba em destaque"""
    aba_atual = pln_notebook.select()
    if aba_atual == str(tab_nltk):
        dica_salvar.texto = "Salvar texto em .txt"
    else:
        dica_salvar.texto = "Salvar texto em .txt, .csv ou .json"


# Frame de botões para salvar resultados
pln_frame_botoes = tk2.Frame(pln_container)
pln_frame_botoes.pack(anchor='center', pady=5)
pln_btn_salvar = tk2.Button(pln_frame_botoes, text="Salvar", command=salvar_resultado)
pln_btn_salvar.pack(side=tk.LEFT, padx=10, pady=5)
dica_salvar = Dica(pln_btn_salvar, "Salvar texto em .txt")

# Vincula evento de troca de aba para atualizar a dica
pln_notebook.bind("<<NotebookTabChanged>>", atualizar_dica_salvar)

# === ABA ENTRADA ===
frame_texto = tk2.Frame(texto_notebook)
texto_etq_instrucao = tk2.Label(frame_texto, text="Insira o texto ou importe um txt:")
texto_text = tk.Text(frame_texto)

texto_frame_botoes = tk2.Frame(frame_texto)
texto_etq_contador = tk2.Label(frame_texto, text="Caracteres: 0")


def limpar_texto():
    """Remove pontuação e converte para minúsculas"""
    global texto_foi_limpo_entrada, texto_foi_limpo_resumo, texto_foi_limpo_conteudo
    global texto_antes_limpar_entrada, texto_antes_limpar_resumo, texto_antes_limpar_conteudo
    
    aba_atual = texto_notebook.select()
    if aba_atual == str(frame_texto):
        widget_texto = texto_text
        conteudo = widget_texto.get("1.0", tk.END).strip()
    else:
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            widget_texto = wk_text_resumo
        else:
            widget_texto = wk_text_conteudo
        widget_texto.config(state='normal')
        conteudo = widget_texto.get("1.0", tk.END).strip()
    
    if not conteudo:
        if aba_atual != str(frame_texto):
            widget_texto.config(state='disabled')
        messagebox.showwarning("Texto vazio", "Não há texto para limpar.", parent=janela_principal)
        return
    
    confirmar = messagebox.askyesno(
        "Confirmar limpeza",
        "A limpeza removerá todos os sinais de pontuação e deixará todas as letras em minúsculas.\n\nDeseja continuar?",
        parent=janela_principal
    )
    if not confirmar:
        if aba_atual != str(frame_texto):
            widget_texto.config(state='disabled')
        return
    
    texto_antes_limpar_atual = conteudo
    sem_pontuacao = re.sub(r"[^\w\s]", "", conteudo)
    resultado = sem_pontuacao.lower()
    widget_texto.delete("1.0", tk.END)
    widget_texto.insert(tk.END, resultado)

    if aba_atual != str(frame_texto):
        widget_texto.config(state='disabled')
    
    if aba_atual == str(frame_texto):
        texto_foi_limpo_entrada = True
        texto_antes_limpar_entrada = texto_antes_limpar_atual
        atualizar_contador_texto()
        texto_btn_limpar.config(text="Restaurar Texto", command=restaurar_texto)
    else:
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            texto_foi_limpo_resumo = True
            texto_antes_limpar_resumo = texto_antes_limpar_atual
            atualizar_contador_resumo()
            wk_btn_limpar_resumo.config(text="Restaurar Texto", command=restaurar_texto)
        else:
            texto_foi_limpo_conteudo = True
            texto_antes_limpar_conteudo = texto_antes_limpar_atual
            atualizar_contador_conteudo()
            wk_btn_limpar_conteudo.config(text="Restaurar Texto", command=restaurar_texto)
    
    atualizar_estado_rd_frases()


def restaurar_texto():
    """Restaura o texto antes da limpeza"""
    global texto_foi_limpo_entrada, texto_foi_limpo_resumo, texto_foi_limpo_conteudo
    global texto_antes_limpar_entrada, texto_antes_limpar_resumo, texto_antes_limpar_conteudo
    
    aba_atual = texto_notebook.select()
    if aba_atual == str(frame_texto):
        if texto_antes_limpar_entrada is None:
            messagebox.showwarning("Sem texto original", "Não há texto original para restaurar.", parent=janela_principal)
            return
        texto_text.delete("1.0", tk.END)
        texto_text.insert(tk.END, texto_antes_limpar_entrada)
        atualizar_contador_texto()
        texto_foi_limpo_entrada = False
        texto_antes_limpar_entrada = None
        texto_btn_limpar.config(text="Limpar Texto", command=limpar_texto)
    else:
        sub_aba = wiki_sub_notebook.select()
        if sub_aba == str(tab_resumo):
            if texto_antes_limpar_resumo is None:
                messagebox.showwarning("Sem texto original", "Não há texto original para restaurar.", parent=janela_principal)
                return
            wk_text_resumo.config(state='normal')
            wk_text_resumo.delete("1.0", tk.END)
            wk_text_resumo.insert(tk.END, texto_antes_limpar_resumo)
            wk_text_resumo.config(state='disabled')
            atualizar_contador_resumo()
            texto_foi_limpo_resumo = False
            texto_antes_limpar_resumo = None
            wk_btn_limpar_resumo.config(text="Limpar Texto", command=limpar_texto)
        else:
            if texto_antes_limpar_conteudo is None:
                messagebox.showwarning("Sem texto original", "Não há texto original para restaurar.", parent=janela_principal)
                return
            wk_text_conteudo.config(state='normal')
            wk_text_conteudo.delete("1.0", tk.END)
            wk_text_conteudo.insert(tk.END, texto_antes_limpar_conteudo)
            wk_text_conteudo.config(state='disabled')
            atualizar_contador_conteudo()
            texto_foi_limpo_conteudo = False
            texto_antes_limpar_conteudo = None
            wk_btn_limpar_conteudo.config(text="Limpar Texto", command=limpar_texto)
    
    atualizar_estado_rd_frases()


# Botões da aba Entrada
texto_btn_limpar = tk2.Button(texto_frame_botoes, text="Limpar Texto", command=limpar_texto)
texto_btn_limitar = tk2.Button(texto_frame_botoes, text="Limitar Caracteres", command=definir_limites_caracteres)

# === ABA WIKIPEDIA ===
frame_wiki = tk2.Frame(texto_notebook)
wk_etq_busca = tk2.Label(frame_wiki, text="Digite o título da página da Wikipedia:", justify="center")
wk_ent_busca = tk2.Entry(frame_wiki, width=30)
wk_btn_buscar = tk2.Button(frame_wiki, text="Buscar", command=wk_buscar)
wk_etq_busca.pack(padx=5, pady=(5, 2))
wk_ent_busca.pack(padx=5, pady=2)
wk_btn_buscar.pack(padx=5, pady=2)
Dica(wk_btn_buscar, "Certifique-se de incluir inicial maiúscula e acentuação correta.")

# Sub-notebook para Resumo e Conteúdo
wiki_sub_notebook = tk2.Notebook(frame_wiki)
wiki_sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Aba Resumo
tab_resumo = tk2.Frame(wiki_sub_notebook)
resumo_header = tk2.Frame(tab_resumo)
wk_etq_resumo = tk2.Label(resumo_header, text="Resumo da página:")
wk_btn_limpar_resumo = tk2.Button(resumo_header, text="Limpar Texto", command=limpar_texto)
wk_btn_limitar_resumo = tk2.Button(resumo_header, text="Limitar Caracteres", command=definir_limites_caracteres)

wk_etq_resumo.pack(side=tk.LEFT)
wk_btn_limitar_resumo.pack(side=tk.RIGHT, padx=2)
wk_btn_limpar_resumo.pack(side=tk.RIGHT, padx=2)
resumo_header.pack(fill=tk.X, padx=5, pady=(5, 2))

wk_text_resumo = tk.Text(tab_resumo, state='disabled')
wk_text_resumo.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
wk_etq_contador_resumo = tk2.Label(tab_resumo, text="Caracteres: 0")

# Aba Conteúdo
tab_conteudo = tk2.Frame(wiki_sub_notebook)
conteudo_header = tk2.Frame(tab_conteudo)
wk_etq_conteudo = tk2.Label(conteudo_header, text="Conteúdo completo:")
wk_btn_limpar_conteudo = tk2.Button(conteudo_header, text="Limpar Texto", command=limpar_texto)
wk_btn_limitar_conteudo = tk2.Button(conteudo_header, text="Limitar Caracteres", command=definir_limites_caracteres)

wk_etq_conteudo.pack(side=tk.LEFT)
wk_btn_limitar_conteudo.pack(side=tk.RIGHT, padx=2)
wk_btn_limpar_conteudo.pack(side=tk.RIGHT, padx=2)
conteudo_header.pack(fill=tk.X, padx=5, pady=(5, 2))

wk_text_conteudo = tk.Text(tab_conteudo, state='disabled')
wk_text_conteudo.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
wk_etq_contador_conteudo = tk2.Label(tab_conteudo, text="Caracteres: 0")

wiki_sub_notebook.add(tab_resumo, text="Resumo")
wiki_sub_notebook.add(tab_conteudo, text="Conteúdo")

wiki_sub_notebook.bind("<<NotebookTabChanged>>", lambda e: ocultar_etqs_sentimento())

# Fonte da Wikipedia
wk_etq_fonte = tk2.Label(frame_wiki, text="Fonte:")
wk_ent_fonte = tk2.Entry(frame_wiki, width=50, state='readonly')
wk_etq_fonte.pack(side=tk.LEFT, pady=(5, 2))
wk_ent_fonte.pack(side=tk.LEFT, padx=5, pady=2)

# Adiciona abas ao notebook principal
texto_notebook.add(frame_texto, text="Entrada")
texto_notebook.add(frame_wiki, text="Wikipedia")

# Layout da aba Entrada
texto_etq_instrucao.pack(padx=5, pady=5)
texto_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
texto_frame_botoes.pack(pady=5)
texto_btn_limpar.pack(side=tk.LEFT, padx=5)
texto_btn_limitar.pack(side=tk.LEFT, padx=5)

# Vincula eventos de atualização
texto_text.bind("<KeyRelease>", atualizar_contador_texto)
texto_text.bind("<<Modified>>", atualizar_contador_texto)

# Vincula eventos de troca de aba para atualizar estado do radiobutton "Tokenizar em frases"
texto_notebook.bind("<<NotebookTabChanged>>", atualizar_estado_rd_frases)
wiki_sub_notebook.bind("<<NotebookTabChanged>>", atualizar_estado_rd_frases)

# Equaliza larguras após a janela ser renderizada
janela_principal.after(100, equalizar_larguras)

janela_principal.mainloop()
