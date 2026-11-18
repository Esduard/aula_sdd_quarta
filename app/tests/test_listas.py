"""Testes do módulo de regras das listas, sempre pela interface pública."""

import pytest

from listas import ErroDeValidacao, Listas


def test_sem_arquivo_de_dados_a_consulta_de_todas_as_listas_devolve_nenhuma_lista(
    tmp_path,
):
    listas = Listas(tmp_path / "dados.json")

    assert listas.todas() == []


def test_criar_uma_lista_com_nome_a_faz_aparecer_entre_todas_as_listas(tmp_path):
    listas = Listas(tmp_path / "dados.json")

    listas.criar("Mercado da semana")

    assert [lista.nome for lista in listas.todas()] == ["Mercado da semana"]


def test_as_listas_sobrevivem_a_reabrir_o_modulo_sobre_o_mesmo_arquivo_de_dados(
    tmp_path,
):
    caminho = tmp_path / "dados.json"
    Listas(caminho).criar("Churrasco de sábado")

    reaberto = Listas(caminho)

    assert [lista.nome for lista in reaberto.todas()] == ["Churrasco de sábado"]


def test_as_listas_aparecem_das_mais_recentes_para_as_mais_antigas(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    listas.criar("Primeira")
    listas.criar("Segunda")
    listas.criar("Terceira")

    assert [lista.nome for lista in listas.todas()] == [
        "Terceira",
        "Segunda",
        "Primeira",
    ]


def test_espacos_das_pontas_do_nome_da_lista_sao_removidos(tmp_path):
    listas = Listas(tmp_path / "dados.json")

    criada = listas.criar("  Feira de domingo \t")

    assert criada.nome == "Feira de domingo"
    assert [lista.nome for lista in listas.todas()] == ["Feira de domingo"]


@pytest.mark.parametrize("nome_em_branco", ["", "   ", " \t\n "])
def test_nome_vazio_ou_so_com_espacos_e_rejeitado_com_erro_de_validacao_e_nada_e_gravado(
    tmp_path, nome_em_branco
):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    listas.criar("Mercado da semana")

    with pytest.raises(ErroDeValidacao):
        listas.criar(nome_em_branco)

    assert [lista.nome for lista in listas.todas()] == ["Mercado da semana"]
    assert [lista.nome for lista in Listas(caminho).todas()] == ["Mercado da semana"]


def test_duas_listas_podem_ter_o_mesmo_nome_e_cada_uma_tem_seu_identificador(
    tmp_path,
):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)

    primeira = listas.criar("Mercado")
    segunda = listas.criar("Mercado")

    assert primeira.id != segunda.id
    assert [(lista.id, lista.nome) for lista in listas.todas()] == [
        (segunda.id, "Mercado"),
        (primeira.id, "Mercado"),
    ]
    # O identificador é estável: continua o mesmo ao reabrir o módulo.
    assert [lista.id for lista in Listas(caminho).todas()] == [
        segunda.id,
        primeira.id,
    ]
