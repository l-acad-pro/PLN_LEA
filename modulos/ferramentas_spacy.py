import spacy
import nltk
from nltk.corpus import stopwords

def tokenizar_texto(texto, nlp):
    """
    Tokeniza o texto usando um modelo spaCy.
    
    Args:
        texto: String contendo o texto a ser tokenizado
        nlp: Modelo spaCy carregado
        
    Returns:
        Lista de tokens (palavras)
    """
    if nlp is None:
        raise Exception("Nenhum modelo spaCy foi selecionado. Configure em Configurações > Selecionar Modelo SpaCy")
    
    doc = nlp(texto)
    tokens = [token.text for token in doc]
    return tokens

def remover_stopwords(tokens, idioma='english'):
    """
    Remove stopwords da lista de tokens usando as stopwords do NLTK.
    
    Args:
        tokens: Lista de tokens
        idioma: 'english' ou 'portuguese' para selecionar o idioma das stopwords
        
    Returns:
        Lista de tokens sem stopwords
    """
    try:
        stop_words = set(stopwords.words(idioma))
        return [token for token in tokens if token.lower() not in stop_words]
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
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

def analisar_sentimento(texto, nlp):
    """
    Realiza análise de sentimento usando spacytextblob integrado ao spaCy.
    
    Args:
        texto: String contendo o texto a analisar
        nlp: Modelo spaCy carregado
        
    Returns:
        Dicionário com 'polaridade' e 'subjetividade' (valores entre 0 e 1)
    """
    if not texto or not texto.strip():
        raise Exception("Texto vazio para análise de sentimento")
    
    if nlp is None:
        raise Exception("Nenhum modelo spaCy foi selecionado. Configure em Configurações > Selecionar Modelo SpaCy")
    
    try:
        # Adiciona o pipeline spacytextblob se não estiver presente
        if "spacytextblob" not in nlp.pipe_names:
            from spacytextblob.spacytextblob import SpacyTextBlob
            nlp.add_pipe("spacytextblob")
        
        doc = nlp(texto)
        polarity = doc._.blob.polarity
        subjectivity = doc._.blob.subjectivity
        
        return {
            'polaridade': round(polarity, 1),
            'subjetividade': round(subjectivity, 1)
        }
    except Exception as e:
        raise Exception(f"Erro na análise de sentimento: {str(e)}")
