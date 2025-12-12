# PLN-LEA

Projeto de Processamento de Linguagem Natural (PLN) com interface gráfica (Tkinter/ttkbootstrap), integrando NLTK, spaCy e consultas à Wikipedia.

Este trabalho se trata de um pré-requisito para a obtenção do título em Bacharelado em Línguas Estrangeiras Aplicadas ao Multilinguismo e à Sociedade da Informação, desenvolvido na Universidade de Brasília (UnB).

## Visão Geral
- Tokenização (palavras, frases, opções avançadas)
- Lematização e etiquetagem morfossintática (spaCy)
- Análise de sentimentos (TextBlob/NLTK)
- Consulta e extração de conteúdo da Wikipedia
- Empacotamento com PyInstaller (executável standalone)

## Requisitos
- Python 3.10+
- Ambiente virtual recomendado
- Pacotes principais: `nltk`, `spacy`, `ttkbootstrap`, `wikipedia-api`, `textblob`
- Modelos spaCy: `pt_core_news_sm`, `en_core_web_sm`

## Instalação
```bash
# Criar e ativar ambiente (Windows PowerShell)
python -m venv env_tcc
./env_tcc/Scripts/Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Baixar modelos do spaCy (se necessário)
python -m spacy download pt_core_news_sm
python -m spacy download en_core_web_sm
```

## Execução
```bash
# Rodar a aplicação
python main.py
```

## Empacotamento (PyInstaller)
```bash
# Gerar executável único
pyinstaller PLN_LEA.spec
```

## Estrutura
```
PLN_LEA/
├─ main.py
├─ modulos/
│  ├─ baixar_modelo_spacy.py
│  ├─ configurar_wiki.py
│  ├─ ferramentas_nltk.py
│  ├─ ferramentas_spacy.py
│  ├─ selecionar_modelo_spacy.py
│  └─ utils.py
└─ README.md
```

## Observações
- O projeto foi pensado para uso acadêmico e demonstração de técnicas de PLN.
- Para portabilidade, recomenda-se empacotar os modelos spaCy e dados necessários via `PLN_LEA.spec`.

## Créditos
- Universidade de Brasília (UnB)
- Curso: Línguas Estrangeiras Aplicadas ao Multilinguismo e à Sociedade da Informação
- Bibliotecas: NLTK, spaCy, TextBlob, ttkbootstrap, wikipedia-api
