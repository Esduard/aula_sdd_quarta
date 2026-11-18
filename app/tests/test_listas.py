"""Testes do módulo de regras das listas, sempre pela interface pública."""

from listas import Listas


def test_sem_arquivo_de_dados_a_consulta_de_todas_as_listas_devolve_nenhuma_lista(
    tmp_path,
):
    listas = Listas(tmp_path / "dados.json")

    assert listas.todas() == []
