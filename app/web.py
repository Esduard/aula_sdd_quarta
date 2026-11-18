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

    @app.get("/listas/<id_da_lista>/renomear")
    def formulario_de_renomear_lista(id_da_lista):
        lista = listas.obter(id_da_lista)
        return render_template("renomear_lista.html", lista=lista, nome=lista.nome)

    @app.post("/listas/<id_da_lista>/renomear")
    def renomear_lista(id_da_lista):
        nome = request.form.get("nome", "")
        try:
            listas.renomear(id_da_lista, nome)
        except ErroDeValidacao as erro:
            return (
                render_template(
                    "renomear_lista.html",
                    lista=listas.obter(id_da_lista),
                    erro=str(erro),
                    nome=nome,
                ),
                400,
            )
        return redirect(url_for("ver_lista", id_da_lista=id_da_lista))

    @app.get("/listas/<id_da_lista>/excluir")
    def confirmar_exclusao_da_lista(id_da_lista):
        # Tela de confirmação: só mostra a Lista; quem exclui é o POST.
        return render_template("excluir_lista.html", lista=listas.obter(id_da_lista))

    @app.post("/listas/<id_da_lista>/excluir")
    def excluir_lista(id_da_lista):
        listas.excluir(id_da_lista)
        return redirect(url_for("inicio"))

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

    @app.get("/listas/<id_da_lista>/itens/<id_do_item>/editar")
    def formulario_de_editar_item(id_da_lista, id_do_item):
        item = listas.obter_item(id_da_lista, id_do_item)
        return render_template(
            "editar_item.html",
            lista=listas.obter(id_da_lista),
            item=item,
            nome=item.nome,
            quantidade=item.quantidade or "",
        )

    @app.post("/listas/<id_da_lista>/itens/<id_do_item>/editar")
    def editar_item(id_da_lista, id_do_item):
        nome = request.form.get("nome", "")
        quantidade = request.form.get("quantidade", "")
        try:
            listas.editar_item(id_da_lista, id_do_item, nome, quantidade)
        except ErroDeValidacao as erro:
            return (
                render_template(
                    "editar_item.html",
                    lista=listas.obter(id_da_lista),
                    item=listas.obter_item(id_da_lista, id_do_item),
                    erro=str(erro),
                    nome=nome,
                    quantidade=quantidade,
                ),
                400,
            )
        return redirect(url_for("ver_lista", id_da_lista=id_da_lista))

    @app.post("/listas/<id_da_lista>/itens/<id_do_item>/remover")
    def remover_item(id_da_lista, id_do_item):
        listas.remover_item(id_da_lista, id_do_item)
        return redirect(url_for("ver_lista", id_da_lista=id_da_lista))

    @app.post("/listas/<id_da_lista>/desmarcar-todos")
    def desmarcar_todos(id_da_lista):
        listas.desmarcar_todos(id_da_lista)
        return redirect(url_for("ver_lista", id_da_lista=id_da_lista))

    @app.errorhandler(ErroNaoEncontrado)
    def nao_encontrado(erro):
        return render_template("nao_encontrado.html", mensagem=str(erro)), 404

    return app


app = criar_app()
