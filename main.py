"""Processa solicitacoes.json e gera aprovados.csv + processamento.log.

Uso:
    python main.py
    python main.py --entrada outro.json --saida saida.csv --log execucao.log
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from processamento.configuracao import Configuracao
from processamento.processador_solicitacoes import ProcessadorSolicitacoes

PASTA_BASE = Path(__file__).resolve().parent


def criar_configuracao(argumentos: Optional[List[str]] = None) -> Configuracao:
    """Monta a configuração a partir dos argumentos de linha de comando.

    Args:
        argumentos (Optional[List[str]]): Argumentos a interpretar. Se ``None``,
            usa os argumentos do processo (``sys.argv``).

    Returns:
        Configuracao: Configuração com os caminhos informados ou, na ausência
        deles, os arquivos padrão ao lado do ``main.py``.
    """
    parser = argparse.ArgumentParser(description="Gera o CSV de solicitações aprovadas.")
    parser.add_argument(
        "--entrada", default=PASTA_BASE / "solicitacoes.json", help="JSON de entrada"
    )
    parser.add_argument(
        "--saida", default=PASTA_BASE / "aprovados.csv", help="CSV de saída"
    )
    parser.add_argument(
        "--log", default=PASTA_BASE / "processamento.log", help="arquivo de log"
    )
    args = parser.parse_args(argumentos)
    return Configuracao(
        arquivo_entrada=Path(args.entrada),
        arquivo_saida=Path(args.saida),
        arquivo_log=Path(args.log),
    )


def main(argumentos: Optional[List[str]] = None) -> int:
    """Ponto de entrada da aplicação.

    Args:
        argumentos (Optional[List[str]]): Argumentos de linha de comando.
            Se ``None``, usa ``sys.argv``.

    Returns:
        int: Código de saída: ``0`` em caso de sucesso, ``1`` em caso de erro.
    """
    configuracao = criar_configuracao(argumentos)
    return ProcessadorSolicitacoes(configuracao).executar()


if __name__ == "__main__":
    sys.exit(main())
