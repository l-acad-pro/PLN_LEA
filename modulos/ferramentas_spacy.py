"""
Ferramentas de Processamento de Linguagem Natural com spaCy.
Funções para tokenização, lematização, etiquetagem POS e análise de sentimento.
"""

import spacy
import nltk
from nltk.corpus import stopwords


def tokenizar_texto(texto, pln):
    """
    Tokeniza o texto usando um modelo spaCy.
    
    Args:
        texto: Texto a ser tokenizado
        pln: Modelo spaCy carregado
        
    Returns:
        Lista de tokens (excluindo espaços em branco)
    """
    if pln is None:
        raise Exception("Nenhum modelo spaCy foi selecionado. Configure em Configurações > Selecionar Modelo SpaCy")
    
    doc = pln(texto)
    tokens = [token.text for token in doc if not token.is_space]
    return tokens


def remover_stopwords(tokens, idioma='english'):
    """
    Remove stopwords da lista de tokens usando NLTK.
    
    Args:
        tokens: Lista de tokens
        idioma: 'english' ou 'portuguese'
        
    Returns:
        Lista de tokens sem stopwords
    """
    try:
        palavras_vazias = set(stopwords.words(idioma))
        return [token for token in tokens if token.lower() not in palavras_vazias]
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
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


def lematizar_tokens(texto, pln):
    """
    Lematiza o texto usando spaCy (reduz palavras à forma base).
    
    Args:
        texto: Texto a ser lematizado
        pln: Modelo spaCy carregado
        
    Returns:
        Lista de lemas
    """
    if pln is None:
        raise Exception("Nenhum modelo spaCy foi selecionado. Configure em Configurações > Selecionar Modelo SpaCy")
    
    doc = pln(texto)
    lemas = [token.lemma_ for token in doc if not token.is_space]
    return lemas


def etiquetar_tokens(texto, pln):
    """
    Etiqueta o texto com POS tags usando spaCy.
    
    Args:
        texto: Texto a ser etiquetado
        pln: Modelo spaCy carregado
        
    Returns:
        Lista de tuplas (token, etiqueta_POS)
    """
    if pln is None:
        raise Exception("Nenhum modelo spaCy foi selecionado. Configure em Configurações > Selecionar Modelo SpaCy")
    
    doc = pln(texto)
    etiquetas = [(token.text, token.pos_) for token in doc if not token.is_space] # [(token.text, token.pos_) for token in doc if not token.is_space]
    return etiquetas


def processar_completo(texto, pln, lematizar=False, etiquetar=False):
    """
    Processa o texto retornando token, lema e/ou etiqueta conforme solicitado.
    
    Args:
        texto: Texto a ser processado
        pln: Modelo spaCy carregado
        lematizar: Se True, inclui lema no resultado
        etiquetar: Se True, inclui etiqueta POS no resultado
        
    Returns:
        Lista de tuplas com os dados solicitados
    """
    if pln is None:
        raise Exception("Nenhum modelo spaCy foi selecionado. Configure em Configurações > Selecionar Modelo SpaCy")

    doc = pln(texto)
    resultados = []

    for token in doc:
        if token.is_space:
            continue

        dados = [token.text]
        if lematizar:
            dados.append(token.lemma_)
        if etiquetar:
            dados.append(token.pos_)

        resultados.append(tuple(dados))

    return resultados


def formatar_processamento_completo(dados, lematizar=False, etiquetar=False):
    """
    Formata os dados processados para exibição em widget Text.
    Cada token em uma linha no formato: token lema etiqueta
    
    Args:
        dados: Lista de tuplas com os dados processados
        lematizar: Se True, inclui lema na formatação
        etiquetar: Se True, inclui etiqueta na formatação
        
    Returns:
        String formatada com uma entrada por linha
    """
    linhas = []
    for item in dados:
        linhas.append("\t".join(item))
    return "\n".join(linhas)


def formatar_etiquetas_para_exibicao(etiquetas):
    """
    Formata lista de tuplas (token, etiqueta) para exibição.
    
    Args:
        etiquetas: Lista de tuplas (token, etiqueta_POS)
        
    Returns:
        String formatada com tokens etiquetados
    """
    return ",".join([f"{token}/{tag}" for token, tag in etiquetas])


def analisar_sentimento(texto, pln):
    """
    Realiza análise de sentimento usando spacytextblob integrado ao spaCy.
    
    Args:
        texto: Texto a analisar
        pln: Modelo spaCy carregado
        
    Returns:
        Dicionário com 'polaridade' e 'subjetividade' (valores entre -1 e 1)
    """
    if not texto or not texto.strip():
        raise Exception("Texto vazio para análise de sentimento")
    
    if pln is None:
        raise Exception("Nenhum modelo spaCy foi selecionado. Configure em Configurações > Selecionar Modelo SpaCy")
    
    try:
        # Adiciona o pipeline spacytextblob se não estiver presente
        if "spacytextblob" not in pln.pipe_names:
            from spacytextblob.spacytextblob import SpacyTextBlob
            pln.add_pipe("spacytextblob")
        
        doc = pln(texto)
        polaridade = doc._.blob.polarity
        subjetividade = doc._.blob.subjectivity
        
        return {
            'polaridade': round(polaridade, 1),
            'subjetividade': round(subjetividade, 1)
        }
    except Exception as e:
        raise Exception(f"Erro na análise de sentimento: {str(e)}")
