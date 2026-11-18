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
# ``itens`` traz os Itens já ordenados para exibição: primeiro os pendentes,
# depois os comprados, cada grupo na ordem em que os Itens foram adicionados.
# ``total_de_itens`` e ``comprados`` são o progresso da Lista, já contado.
Lista = namedtuple("Lista", ["id", "nome", "itens", "total_de_itens", "comprados"])

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

    def obter_item(self, id_da_lista, id_do_item):
        """Devolve o Item com o identificador dado, da Lista dada.

        Se a Lista não existir, ou o Item não existir nela, levanta
        ``ErroNaoEncontrado``.
        """
        return _para_item(_achar_item(_achar_lista(self._ler(), id_da_lista), id_do_item))

    def editar_item(self, id_da_lista, id_do_item, nome, quantidade=None):
        """Troca o nome e a Quantidade do Item, grava e o devolve.

        Valem as regras da adição: os espaços das pontas do nome e da
        Quantidade são removidos, e a Quantidade vazia ou só com espaços conta
        como ausente. O estado do Item (pendente ou comprado) não muda.
        Se não sobrar nada do nome, levanta ``ErroDeValidacao`` e nada é
        gravado. Se a Lista não existir, ou o Item não existir nela, levanta
        ``ErroNaoEncontrado`` e nada é gravado.
        """
        nome = nome.strip()
        if not nome:
            raise ErroDeValidacao("Informe um nome para o Item.")
        dados = self._ler()
        registro = _achar_item(_achar_lista(dados, id_da_lista), id_do_item)
        registro["nome"] = nome
        registro["quantidade"] = (quantidade or "").strip() or None
        self._gravar(dados)
        return _para_item(registro)

    def remover_item(self, id_da_lista, id_do_item):
        """Tira o Item da Lista e grava. Não devolve nada.

        Se a Lista não existir, ou o Item não existir nela, levanta
        ``ErroNaoEncontrado`` e nada é gravado.
        """
        dados = self._ler()
        registro_da_lista = _achar_lista(dados, id_da_lista)
        registro = _achar_item(registro_da_lista, id_do_item)
        registro_da_lista["itens"].remove(registro)
        self._gravar(dados)

    def marcar_como_comprado(self, id_da_lista, id_do_item):
        """Marca o Item como comprado, grava e o devolve.

        Se a Lista não existir, ou o Item não existir nela, levanta
        ``ErroNaoEncontrado`` e nada é gravado.
        """
        return self._mudar_estado(id_da_lista, id_do_item, comprado=True)

    def voltar_para_pendente(self, id_da_lista, id_do_item):
        """Devolve o Item ao estado pendente, grava e o devolve.

        Se a Lista não existir, ou o Item não existir nela, levanta
        ``ErroNaoEncontrado`` e nada é gravado.
        """
        return self._mudar_estado(id_da_lista, id_do_item, comprado=False)

    def desmarcar_todos(self, id_da_lista):
        """Devolve todos os Itens da Lista ao estado pendente, grava e a devolve.

        Nenhum Item é removido, e nomes e Quantidades não mudam. Se a Lista
        não existir, levanta ``ErroNaoEncontrado`` e nada é gravado.
        """
        dados = self._ler()
        registro_da_lista = _achar_lista(dados, id_da_lista)
        for registro in registro_da_lista.get("itens", []):
            registro["comprado"] = False
        self._gravar(dados)
        return _para_lista(registro_da_lista)

    def _mudar_estado(self, id_da_lista, id_do_item, comprado):
        dados = self._ler()
        registro = _achar_item(_achar_lista(dados, id_da_lista), id_do_item)
        registro["comprado"] = comprado
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


def _achar_item(registro_da_lista, id_do_item):
    for registro in registro_da_lista.get("itens", []):
        if registro["id"] == id_do_item:
            return registro
    raise ErroNaoEncontrado("Item não encontrado.")


def _para_lista(registro):
    # Listas gravadas antes de existirem Itens não têm a chave "itens".
    # A ordenação é estável: dentro de cada grupo vale a ordem de adição,
    # que é a ordem em que os Itens estão guardados.
    itens = tuple(
        sorted(
            (_para_item(item) for item in registro.get("itens", [])),
            key=lambda item: item.comprado,
        )
    )
    return Lista(
        id=registro["id"],
        nome=registro["nome"],
        itens=itens,
        total_de_itens=len(itens),
        comprados=sum(1 for item in itens if item.comprado),
    )


def _para_item(registro):
    return Item(
        id=registro["id"],
        nome=registro["nome"],
        quantidade=registro["quantidade"],
        comprado=registro["comprado"],
    )
