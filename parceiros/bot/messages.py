import os
from typing import Optional


def carregar_template(caminho: str) -> str:
    """Lê o arquivo de template."""
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


def montar_mensagem(template: str, nome_buffet: str, **kwargs) -> str:
    """Substitui variáveis no template."""
    variaveis = {"nome_buffet": nome_buffet, **kwargs}
    try:
        return template.format(**variaveis)
    except KeyError as e:
        raise ValueError(f"Variável não encontrada no template: {e}")


def preview_mensagem(template: str, nome_buffet: str = "Buffet Exemplo") -> str:
    """Retorna preview da mensagem com nome de exemplo."""
    return montar_mensagem(template, nome_buffet)
