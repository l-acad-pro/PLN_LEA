import wikipediaapi
import re
from tkinter import SOLID, messagebox, filedialog, simpledialog
import tkinter as tk
import tkinter.ttk as tk2
import csv, json
from modulos import baixar_modelo_spacy, selecionar_modelo_spacy, configurar_wiki

USER_AGENT = None
wk_lg = None
wiki = None

def atualizar_config_wiki(user_agent, idioma):
    global USER_AGENT, wk_lg, wiki
    if idioma:
        wk_lg = idioma

    if user_agent:
        USER_AGENT = user_agent

    # Só recria o objeto se ambos estiverem definidos; permite escolher idioma antes do user agent
    if USER_AGENT and wk_lg:
        wiki = wikipediaapi.Wikipedia(language=wk_lg, user_agent=USER_AGENT)
        messagebox.showinfo("Sucesso", f"Configurações atualizadas!\nIdioma: {wk_lg}\nUser Agent: {USER_AGENT}")

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

    # Garante que o frame de texto esteja visível
    opcao_visualizacao.set("texto")
    atualizar_visualizacao()

    # Substitui o conteúdo do Text
    Texto_texto.delete("1.0", tk.END)
    Texto_texto.insert(tk.END, conteudo)

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
        
        wk_texto1.config(state='normal')
        wk_texto1.delete('1.0', tk.END)
        wk_texto1.insert(tk.END, page.summary)
        wk_texto1.config(state='disabled')
        wk_fonte.config(state='normal')
        wk_fonte.delete(0, tk.END)
        wk_fonte.insert(tk.END, page.fullurl)
        wk_fonte.config(state='readonly')
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao buscar a página:\n{str(e)}")

def atualizar_visualizacao():
    # Mostra o frame selecionado
    if opcao_visualizacao.get() == "texto":
        frame_wiki.pack_forget()
        wk_paned.pack_forget()
        frame_texto.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        texto_etiqueta1.pack(padx=5, pady=5)
        Texto_texto.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        texto_botao_limpar.pack(padx=5, pady=5)
    else:  # wikipedia
        frame_texto.pack_forget()
        texto_etiqueta1.pack_forget()
        Texto_texto.pack_forget()
        texto_botao_limpar.pack_forget()
        frame_wiki.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        wk_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


janelaPrincipal = tk.Tk()
janelaPrincipal.title("Ferramenta de Processamento de Linguagem Natural")
janelaPrincipal.geometry("800x600")
janelaPrincipal.update_idletasks()
x = (janelaPrincipal.winfo_screenwidth() // 2) - 400
y = (janelaPrincipal.winfo_screenheight() // 2) - 300
janelaPrincipal.geometry(f"800x600+{x}+{y}")

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

#Cria um menu "Configurações"
config_menu = tk.Menu(menu_bar, tearoff=0)
config_menu.add_command(label="Selecionar Modelo SpaCy", command=lambda: selecionar_modelo_spacy.abrir_janela_selecionar_modelo(janelaPrincipal))
config_menu.add_command(label="Baixar Modelo SpaCy", command=lambda: baixar_modelo_spacy.abrir_janela_baixar_modelo(janelaPrincipal))
config_menu.add_separator()
config_menu.add_command(label="Configurar API da Wikipedia", command=lambda: configurar_wiki.janela_wkcfg(janelaPrincipal, atualizar_config_wiki, USER_AGENT))
menu_bar.add_cascade(label="Configurações", menu=config_menu)

# Cria um menu "Ajuda"
ajuda_menu = tk.Menu(menu_bar, tearoff=0)
ajuda_menu.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", "Exemplo de menu Tkinter"))
menu_bar.add_cascade(label="Ajuda", menu=ajuda_menu)

# Radio Buttons para seleção de visualização
frame_opcoes = tk2.LabelFrame(janelaPrincipal)
frame_opcoes.pack(side=tk.TOP, padx=10, pady=10)
opcao_visualizacao = tk.StringVar(value="")  # Texto selecionado por padrão
radio_texto = tk2.Radiobutton(frame_opcoes, text="Personalizada", variable=opcao_visualizacao, 
                              value="texto", command=atualizar_visualizacao)
radio_texto.pack(side=tk.LEFT, padx=10, pady=5)
radio_wiki = tk2.Radiobutton(frame_opcoes, text="Wikipedia", variable=opcao_visualizacao, 
                             value="wikipedia", command=atualizar_visualizacao)
radio_wiki.pack(side=tk.LEFT, padx=10, pady=5)

# Frame para Texto
frame_texto = tk2.Frame(janelaPrincipal)
texto_etiqueta1 = tk2.Label(frame_texto, text="Insira o texto ou importe um txt:")
Texto_texto = tk.Text(frame_texto)
texto_botao_limpar = tk2.Button(frame_texto, text="Limpar Texto")

def limpar_texto():
    confirmar = messagebox.askyesno(
        "Confirmar limpeza",
        "A limpeza removerá todos os sinais de pontuação e deixará todas as letras em minúscula.\n\nDeseja continuar?",
        parent=janelaPrincipal
    )
    if not confirmar:
        return

    conteudo = Texto_texto.get("1.0", tk.END)
    sem_pontuacao = re.sub(r"[^\w\s]", "", conteudo)
    resultado = sem_pontuacao.lower()
    Texto_texto.delete("1.0", tk.END)
    Texto_texto.insert(tk.END, resultado)

texto_botao_limpar.config(command=limpar_texto)

# Frame para Wikipedia com PanedWindow
frame_wiki = tk2.Frame(janelaPrincipal)
wk_paned = tk2.Panedwindow(frame_wiki, orient=tk.VERTICAL)

# Painel superior: busca
wiki_top = tk2.Frame(wk_paned)
wk_etiqueta1 = tk2.Label(wiki_top, text="Digite o título da página da Wikipedia:")
wk_entrada1 = tk2.Entry(wiki_top)
wk_botao1 = tk2.Button(wiki_top, text="Buscar", command=wk_buscar)
wk_etiqueta1.pack(anchor="w", padx=5, pady=(5, 2))
wk_entrada1.pack(fill=tk.X, padx=5, pady=2)
wk_botao1.pack(anchor="w", padx=5, pady=2)

# Painel inferior: resumo e fonte
wiki_bottom = tk2.Frame(wk_paned)
wk_etiqueta2 = tk2.Label(wiki_bottom, text="Resumo da página:")
wk_texto1 = tk.Text(wiki_bottom, state='disabled')
wk_etiqueta2.pack(anchor="w", padx=5, pady=(5, 2))
wk_texto1.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

fonte_container = tk2.Frame(wiki_bottom)
wk_etiqueta3 = tk2.Label(fonte_container, text="Fonte:")
wk_fonte = tk2.Entry(fonte_container, width=50, state='readonly')
wk_etiqueta3.pack(side=tk.LEFT, padx=(0, 5))
wk_fonte.pack(side=tk.LEFT, fill=tk.X, expand=True)
fonte_container.pack(fill=tk.X, padx=5, pady=5)

wk_paned.add(wiki_top, weight=1)
wk_paned.add(wiki_bottom, weight=3)

janelaPrincipal.mainloop()