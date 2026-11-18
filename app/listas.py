"""Regras das listas: todo o comportamento de Listas e Itens.

Este módulo não conhece Flask, HTTP nem HTML. Quem o usa informa o local do
arquivo de dados ao criar ``Listas``; assim os testes apontam para um arquivo
temporário e a camada web aponta para o arquivo do app.
"""

import json
import os
import uuid
from collections import namedtuple

# Uma Lista como as consultas a devolvem, pronta para exibição. O ``id`` é
# opaco e estável: é ele, e não o nome, que identifica a Lista.
# ``itens`` traz os Itens da Lista na ordem em que foram adicionados.
Lista = namedtuple("Lista", ["id", "nome", "itens"])

# Um Item como as consultas o devolvem. O ``id`` é opaco e estável.
# ``quantidade`` é texto livre ou ``None`` quando ausente. ``comprado`` é
# ``False`` enquanto o Item está pendente.
Item = namedtuple("Item", ["id", "nome", "quantidade", "comprado"])


class ErroDeValidacao(Exception):
    """Dado informado pelo usuário que não pode ser aceito.

    A mensagem da exceção está em português e pode ser exibida ao usuário.
    """


class ErroNaoEncontrado(Exception):
    """A Lista ou o Item pedido não existe. Distinto do erro de validação."""


class Listas:
    """O conjunto de todas as Listas guardadas em um arquivo de dados."""

    def __init__(self, caminho_do_arquivo):
        self._caminho_do_arquivo = caminho_do_arquivo

    def criar(self, nome):
        """Cria uma Lista com o nome dado, grava e a devolve.

        Os espaços das pontas do nome são removidos. Se não sobrar nada,
        levanta ``ErroDeValidacao`` e nada é gravado.
        """
        nome = nome.strip()
        if not nome:
            raise ErroDeValidacao("Informe um nome para a Lista.")
        dados = self._ler()
        registro = {"id": uuid.uuid4().hex, "nome": nome}
        dados["listas"].append(registro)
        self._gravar(dados)
        return _para_lista(registro)

    def todas(self):
        """Devolve todas as Listas, as mais recentes primeiro.

        A ordem de criação é a ordem em que as Listas estão guardadas; o
        relógio não entra na conta.
        """
        return [_para_lista(registro) for registro in reversed(self._ler()["listas"])]

    def obter(self, id_da_lista):
        """Devolve a Lista com o identificador dado, com seus Itens.

        Se a Lista não existir, levanta ``ErroNaoEncontrado``.
        """
        return _para_lista(_achar_lista(self._ler(), id_da_lista))

    def adicionar_item(self, id_da_lista, nome, quantidade=None):
        """Adiciona um Item pendente ao fim da Lista, grava e o devolve.

        Os espaços das pontas do nome e da Quantidade são removidos. A
        Quantidade é opcional: vazia ou só com espaços conta como ausente.
        Se não sobrar nada do nome, levanta ``ErroDeValidacao`` e nada é
        gravado. Se a Lista não existir, levanta ``ErroNaoEncontrado``.
        """
        nome = nome.strip()
        if not nome:
            raise ErroDeValidacao("Informe um nome para o Item.")
        quantidade = (quantidade or "").strip() or None
        dados = self._ler()
        registro_da_lista = _achar_lista(dados, id_da_lista)
        registro = {
            "id": uuid.uuid4().hex,
            "nome": nome,
            "quantidade": quantidade,
            "comprado": False,
        }
        registro_da_lista.setdefault("itens", []).append(registro)
        self._gravar(dados)
        return _para_item(registro)

    def _ler(self):
        """Lê o arquivo de dados; arquivo inexistente significa nenhuma Lista."""
        if not os.path.exists(self._caminho_do_arquivo):
            return {"listas": []}
        with open(self._caminho_do_arquivo, encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def _gravar(self, dados):
        with open(self._caminho_do_arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def _achar_lista(dados, id_da_lista):
    for registro in dados["listas"]:
        if registro["id"] == id_da_lista:
            return registro
    raise ErroNaoEncontrado("Lista não encontrada.")


def _para_lista(registro):
    # Listas gravadas antes de existirem Itens não têm a chave "itens".
    itens = tuple(_para_item(item) for item in registro.get("itens", []))
    return Lista(id=registro["id"], nome=registro["nome"], itens=itens)


def _para_item(registro):
    return Item(
        id=registro["id"],
        nome=registro["nome"],
        quantidade=registro["quantidade"],
        comprado=registro["comprado"],
    )
