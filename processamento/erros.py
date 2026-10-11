class ErroProcessamento(Exception):
    """Erro que impede a continuação do processamento.

    É levantado quando ocorre uma falha que inviabiliza a geração do arquivo
    de saída, como arquivo de entrada ausente, JSON inválido ou falha na
    escrita do CSV. Registros individuais inválidos não usam esta exceção,
    pois são apenas ignorados e registrados no log.
    """
