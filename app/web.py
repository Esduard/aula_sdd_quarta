"""Camada web: rotas Flask e templates.

É fina de propósito: só traduz requisições em chamadas ao módulo de regras
das listas e renderiza o que ele devolve. Nenhuma regra de negócio mora aqui.
"""

import os

from flask import Flask, redirect, render_template, request, url_for

from listas import ErroDeValidacao, ErroNaoEncontrado, Listas

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

    @app.post("/listas")
    def criar_lista():
        nome = request.form.get("nome", "")
        try:
            listas.criar(nome)
        except ErroDeValidacao as erro:
            return (
                render_template(
                    "inicio.html", listas=listas.todas(), erro=str(erro), nome=nome
                ),
                400,
            )
        return redirect(url_for("inicio"))

    @app.get("/listas/<id_da_lista>")
    def ver_lista(id_da_lista):
        return render_template("lista.html", lista=listas.obter(id_da_lista))

    @app.post("/listas/<id_da_lista>/itens")
    def adicionar_item(id_da_lista):
        nome = request.form.get("nome", "")
        quantidade = request.form.get("quantidade", "")
        try:
            listas.adicionar_item(id_da_lista, nome, quantidade)
        except ErroDeValidacao as erro:
            return (
                render_template(
                    "lista.html",
                    lista=listas.obter(id_da_lista),
                    erro=str(erro),
                    nome=nome,
                    quantidade=quantidade,
                ),
                400,
            )
        return redirect(url_for("ver_lista", id_da_lista=id_da_lista))

    @app.post("/listas/<id_da_lista>/itens/<id_do_item>/comprado")
    def marcar_item_como_comprado(id_da_lista, id_do_item):
        listas.marcar_como_comprado(id_da_lista, id_do_item)
        return redirect(url_for("ver_lista", id_da_lista=id_da_lista))

    @app.post("/listas/<id_da_lista>/itens/<id_do_item>/pendente")
    def voltar_item_para_pendente(id_da_lista, id_do_item):
        listas.voltar_para_pendente(id_da_lista, id_do_item)
        return redirect(url_for("ver_lista", id_da_lista=id_da_lista))

    @app.errorhandler(ErroNaoEncontrado)
    def nao_encontrado(erro):
        return render_template("nao_encontrado.html", mensagem=str(erro)), 404

    return app


app = criar_app()
