import spacy

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
