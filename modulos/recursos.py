"""
Módulo para gerenciar recursos quando empacotado com PyInstaller.
Fornece funções para localizar arquivos e dados em ambos os ambientes.
"""

import sys
import os


def esta_empacotado():
    """
    Verifica se o programa está rodando como executável PyInstaller.
    
    Returns:
        True se empacotado, False se em desenvolvimento
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def obter_diretorio_base():
    """
    Retorna o diretório base do programa.
    
    Returns:
        Caminho do diretório base (diferente se empacotado ou não)
    """
    if esta_empacotado():
        # PyInstaller extrai para _MEIPASS
        return sys._MEIPASS
    else:
        # Desenvolvimento: diretório do projeto
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def obter_diretorio_executavel():
    """
    Retorna o diretório onde o executável está localizado.
    Útil para salvar arquivos de configuração ao lado do .exe
    
    Returns:
        Caminho do diretório do executável
    """
    if esta_empacotado():
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def obter_caminho_recurso(caminho_relativo):
    """
    Obtém o caminho absoluto de um recurso.
    
    Args:
        caminho_relativo: Caminho relativo ao diretório base
        
    Returns:
        Caminho absoluto do recurso
    """
    return os.path.join(obter_diretorio_base(), caminho_relativo)


def configurar_nltk_data():
    """
    Configura o caminho dos dados NLTK quando empacotado.
    Deve ser chamado antes de usar funções NLTK.
    """
    import nltk
    
    if esta_empacotado():
        nltk_data_path = os.path.join(sys._MEIPASS, 'nltk_data')
        if os.path.exists(nltk_data_path):
            nltk.data.path.insert(0, nltk_data_path)
    
    # Também verifica diretório padrão do usuário
    user_nltk_data = os.path.expanduser('~/nltk_data')
    if os.path.exists(user_nltk_data) and user_nltk_data not in nltk.data.path:
        nltk.data.path.append(user_nltk_data)


def listar_modelos_spacy_disponiveis():
    """
    Lista os modelos spaCy disponíveis (instalados ou empacotados).
    
    Returns:
        Lista de nomes de modelos disponíveis
    """
    # Modelos suportados pela aplicação
    MODELOS_SUPORTADOS = ['pt_core_news_sm', 'en_core_web_sm']
    
    if esta_empacotado():
        # Quando empacotado, retorna os modelos que foram incluídos no .exe
        from pathlib import Path
        base = Path(sys._MEIPASS)
        modelos_disponiveis = []
        for modelo in MODELOS_SUPORTADOS:
            # collect_data_files coloca em modelo/modelo-versao/
            modelo_dir = base / modelo
            if modelo_dir.exists():
                # Encontra o subdiretório com a versão (ex: pt_core_news_sm-3.8.0)
                for subdir in modelo_dir.iterdir():
                    if subdir.is_dir() and subdir.name.startswith(modelo):
                        modelos_disponiveis.append(modelo)
                        break
        return modelos_disponiveis
    else:
        # Em desenvolvimento, usa a função do spaCy
        try:
            from spacy.util import get_installed_models
            return list(get_installed_models())
        except Exception:
            return []


def carregar_modelo_spacy(nome_modelo):
    """
    Carrega um modelo spaCy de forma compatível com PyInstaller.
    
    Args:
        nome_modelo: Nome do modelo (ex: 'pt_core_news_sm')
        
    Returns:
        Modelo spaCy carregado
        
    Raises:
        Exception: Se o modelo não puder ser carregado
    """
    import spacy
    from pathlib import Path
    
    if esta_empacotado():
        # Quando empacotado, carrega do diretório _MEIPASS
        base = Path(sys._MEIPASS)
        modelo_dir = base / nome_modelo
        
        if modelo_dir.exists():
            # Encontra o subdiretório com a versão (ex: pt_core_news_sm-3.8.0)
            for subdir in modelo_dir.iterdir():
                if subdir.is_dir() and subdir.name.startswith(nome_modelo):
                    return spacy.load(subdir)
            raise Exception(f"Modelo '{nome_modelo}' encontrado mas sem versão válida")
        else:
            raise Exception(f"Modelo '{nome_modelo}' não encontrado no executável")
    else:
        # Em desenvolvimento, carrega normalmente
        return spacy.load(nome_modelo)
