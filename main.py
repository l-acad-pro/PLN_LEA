import wikipediaapi
from tkinter import SOLID, messagebox, filedialog, simpledialog
import tkinter as tk
import tkinter.ttk as tk2
from modulos import baixar_modelo_spacy, selecionar_modelo_spacy, configurar_wiki

USER_AGENT = None
wk_lg = None
wiki = None

def atualizar_config_wiki(user_agent, idioma):
    global USER_AGENT, wk_lg, wiki
    USER_AGENT = user_agent
    wk_lg = idioma
    # Recria o objeto wiki com as novas configurações
    wiki = wikipediaapi.Wikipedia(language=wk_lg, user_agent=USER_AGENT)
    messagebox.showinfo("Sucesso", f"Configurações atualizadas!\nIdioma: {idioma}\nUser Agent: {user_agent}")

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
        wk_etiqueta1.pack_forget()
        wk_entrada1.pack_forget()
        wk_etiqueta2.pack_forget()
        wk_texto1.pack_forget()
        wk_botao1.pack_forget()
        wk_etiqueta3.pack_forget()
        wk_fonte.pack_forget()
        frame_texto.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        texto_etiqueta1.pack(padx=5, pady=5)
        Texto_texto.pack(padx=5, pady=5)
    else:  # wikipedia
        frame_texto.pack_forget()
        texto_etiqueta1.pack_forget()
        Texto_texto.pack_forget()
        frame_wiki.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        wk_etiqueta1.pack(padx=5, pady=5)
        wk_entrada1.pack(padx=5, pady=5)
        wk_botao1.pack(padx=5, pady=5)
        wk_etiqueta2.pack(padx=5, pady=5)
        wk_texto1.pack(padx=5, pady=5)
        wk_etiqueta3.pack(side=tk.LEFT, padx=5, pady=5)
        wk_fonte.pack(side=tk.LEFT, padx=5, pady=5)


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
arquivo_menu.add_command(label="Abrir Arquivo")
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
frame_opcoes = tk2.Frame(janelaPrincipal, borderwidth=2, relief=SOLID)
frame_opcoes.pack(side=tk.TOP, padx=10, pady=10)
opcao_etiqueta = tk2.Label(frame_opcoes, text="Selecione a fonte de dados:")
opcao_etiqueta.pack(side=tk.LEFT, padx=10, pady=5)
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

# Frame para Wikipedia
frame_wiki = tk2.Frame(janelaPrincipal)
wk_etiqueta1 = tk2.Label(frame_wiki, text="Digite o título da página da Wikipedia:")
wk_entrada1 = tk2.Entry(frame_wiki)
wk_botao1 = tk2.Button(frame_wiki, text="Buscar", command=wk_buscar)
wk_etiqueta2 = tk2.Label(frame_wiki, text="Resumo da página:")
wk_texto1 = tk.Text(frame_wiki, state='disabled')
wk_etiqueta3 = tk2.Label(frame_wiki, text="Fonte:")
wk_fonte = tk2.Entry(frame_wiki, width=50, state='readonly')

janelaPrincipal.mainloop()