"""Regras das listas: todo o comportamento de Listas e Itens.

Este módulo não conhece Flask, HTTP nem HTML. Quem o usa informa o local do
arquivo de dados ao criar ``Listas``; assim os testes apontam para um arquivo
temporário e a camada web aponta para o arquivo do app.
"""


class Listas:
    """O conjunto de todas as Listas guardadas em um arquivo de dados."""

    def __init__(self, caminho_do_arquivo):
        self._caminho_do_arquivo = caminho_do_arquivo

    def todas(self):
        """Devolve todas as Listas.

        Arquivo de dados inexistente significa nenhuma Lista. Como ainda não
        existe operação que grave o arquivo, não há o que ler dele.
        """
        return []
