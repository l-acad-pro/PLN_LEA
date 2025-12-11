"""
Módulo para gerenciar configurações persistentes do programa.
Salva e carrega configurações de um arquivo config.ini.
Compatível com Windows e Linux, inclusive empacotado com PyInstaller.
"""

import configparser
import os
import sys

ARQUIVO_CONFIG = "config.ini"


def obter_caminho_config():
    """
    Retorna o caminho completo do arquivo de configuração.
    Funciona em desenvolvimento e empacotado com PyInstaller.
    
    Returns:
        Caminho absoluto do arquivo config.ini
    """
    if getattr(sys, 'frozen', False):
        # Executável PyInstaller
        diretorio_base = os.path.dirname(sys.executable)
    else:
        # Desenvolvimento
        diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(diretorio_base, ARQUIVO_CONFIG)


def criar_config_padrao():
    """
    Cria um arquivo de configuração com valores padrão.
    
    Returns:
        Objeto ConfigParser com valores padrão
    """
    config = configparser.ConfigParser()
    
    config['Wikipedia'] = {
        'user_agent': '',
        'idioma': 'pt'
    }
    
    config['SpaCy'] = {
        'modelo': ''
    }
    
    return config


def carregar_configuracoes():
    """
    Carrega as configurações do arquivo config.ini.
    
    Returns:
        Dicionário com as configurações:
        - wiki_user_agent: Agente de usuário da Wikipedia
        - wiki_idioma: Idioma da Wikipedia
        - spacy_modelo: Modelo spaCy selecionado
    """
    config = configparser.ConfigParser()
    caminho = obter_caminho_config()
    
    if not os.path.exists(caminho):
        return {
            'wiki_user_agent': '',
            'wiki_idioma': 'pt',
            'spacy_modelo': ''
        }
    
    try:
        config.read(caminho, encoding='utf-8')
        
        return {
            'wiki_user_agent': config.get('Wikipedia', 'user_agent', fallback=''),
            'wiki_idioma': config.get('Wikipedia', 'idioma', fallback='pt'),
            'spacy_modelo': config.get('SpaCy', 'modelo', fallback='')
        }
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return {
            'wiki_user_agent': '',
            'wiki_idioma': 'pt',
            'spacy_modelo': ''
        }


def salvar_configuracoes(wiki_user_agent=None, wiki_idioma=None, spacy_modelo=None):
    """
    Salva as configurações no arquivo config.ini.
    Apenas atualiza os valores fornecidos (não-None).
    
    Args:
        wiki_user_agent: Agente de usuário para Wikipedia API
        wiki_idioma: Idioma da Wikipedia ('pt' ou 'en')
        spacy_modelo: Nome do modelo spaCy selecionado
        
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    config = configparser.ConfigParser()
    caminho = obter_caminho_config()
    
    if os.path.exists(caminho):
        config.read(caminho, encoding='utf-8')
    else:
        config = criar_config_padrao()
    
    # Garante que as seções existam
    if 'Wikipedia' not in config:
        config['Wikipedia'] = {}
    if 'SpaCy' not in config:
        config['SpaCy'] = {}
    
    # Atualiza apenas os valores fornecidos
    if wiki_user_agent is not None:
        config['Wikipedia']['user_agent'] = wiki_user_agent
    
    if wiki_idioma is not None:
        config['Wikipedia']['idioma'] = wiki_idioma
    
    if spacy_modelo is not None:
        config['SpaCy']['modelo'] = spacy_modelo
    
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            config.write(f)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False


def config_existe():
    """
    Verifica se o arquivo de configuração existe.
    
    Returns:
        True se existe, False caso contrário
    """
    return os.path.exists(obter_caminho_config())
