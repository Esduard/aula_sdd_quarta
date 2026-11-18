"""Camada web: rotas Flask e templates.

É fina de propósito: só traduz requisições em chamadas ao módulo de regras
das listas e renderiza o que ele devolve. Nenhuma regra de negócio mora aqui.
"""

import os

from flask import Flask, render_template

from listas import Listas

CAMINHO_PADRAO_DOS_DADOS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "dados.json"
)


def criar_app(caminho_dos_dados=CAMINHO_PADRAO_DOS_DADOS):
    """Monta o app Flask apontando o módulo de regras para o arquivo de dados."""
    app = Flask(__name__)
    listas = Listas(caminho_dos_dados)

    @app.get("/")
    def inicio():
        return render_template("inicio.html", listas=listas.todas())

    return app


app = criar_app()
