import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

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
