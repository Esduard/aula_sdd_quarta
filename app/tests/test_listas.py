"""Testes do módulo de regras das listas, sempre pela interface pública."""

import pytest

from listas import ErroDeValidacao, ErroNaoEncontrado, Listas


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


def test_obter_uma_lista_recem_criada_devolve_seu_nome_e_nenhum_item(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    criada = listas.criar("Mercado da semana")

    lista = listas.obter(criada.id)

    assert lista.id == criada.id
    assert lista.nome == "Mercado da semana"
    assert list(lista.itens) == []


def test_obter_uma_lista_inexistente_da_erro_de_nao_encontrado(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    listas.criar("Mercado da semana")

    with pytest.raises(ErroNaoEncontrado):
        listas.obter("identificador-que-nao-existe")


def test_adicionar_um_item_so_com_nome_o_faz_aparecer_na_lista_pendente_e_sem_quantidade(
    tmp_path,
):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")

    listas.adicionar_item(lista.id, "Leite")

    itens = listas.obter(lista.id).itens
    assert [(item.nome, item.quantidade, item.comprado) for item in itens] == [
        ("Leite", None, False)
    ]


def test_a_quantidade_informada_acompanha_o_item(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")

    listas.adicionar_item(lista.id, "Leite", "2 L")

    itens = listas.obter(lista.id).itens
    assert [(item.nome, item.quantidade) for item in itens] == [("Leite", "2 L")]


def test_espacos_das_pontas_do_nome_e_da_quantidade_do_item_sao_removidos(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")

    adicionado = listas.adicionar_item(lista.id, "  Ovos \t", "  1 dúzia ")

    assert (adicionado.nome, adicionado.quantidade) == ("Ovos", "1 dúzia")
    itens = listas.obter(lista.id).itens
    assert [(item.nome, item.quantidade) for item in itens] == [("Ovos", "1 dúzia")]


@pytest.mark.parametrize("quantidade_em_branco", ["", "   ", " \t\n "])
def test_quantidade_vazia_ou_so_com_espacos_conta_como_ausente(
    tmp_path, quantidade_em_branco
):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")

    listas.adicionar_item(lista.id, "Pão", quantidade_em_branco)

    assert [item.quantidade for item in listas.obter(lista.id).itens] == [None]


@pytest.mark.parametrize("nome_em_branco", ["", "   ", " \t\n "])
def test_nome_de_item_vazio_ou_so_com_espacos_e_rejeitado_com_erro_de_validacao_e_nada_e_gravado(
    tmp_path, nome_em_branco
):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    listas.adicionar_item(lista.id, "Leite")

    with pytest.raises(ErroDeValidacao) as excecao:
        listas.adicionar_item(lista.id, nome_em_branco, "2 L")

    assert str(excecao.value) == "Informe um nome para o Item."
    assert [item.nome for item in listas.obter(lista.id).itens] == ["Leite"]
    assert [item.nome for item in Listas(caminho).obter(lista.id).itens] == ["Leite"]


def test_dois_itens_podem_ter_o_mesmo_nome_na_mesma_lista_e_cada_um_tem_seu_identificador(
    tmp_path,
):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")

    primeiro = listas.adicionar_item(lista.id, "Leite")
    segundo = listas.adicionar_item(lista.id, "Leite")

    assert primeiro.id != segundo.id
    assert [(item.id, item.nome) for item in listas.obter(lista.id).itens] == [
        (primeiro.id, "Leite"),
        (segundo.id, "Leite"),
    ]
    # O identificador é estável: continua o mesmo ao reabrir o módulo.
    assert [item.id for item in Listas(caminho).obter(lista.id).itens] == [
        primeiro.id,
        segundo.id,
    ]


def test_os_itens_aparecem_na_ordem_em_que_foram_adicionados(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")
    listas.adicionar_item(lista.id, "Leite")
    listas.adicionar_item(lista.id, "Arroz")
    listas.adicionar_item(lista.id, "Feijão")

    assert [item.nome for item in listas.obter(lista.id).itens] == [
        "Leite",
        "Arroz",
        "Feijão",
    ]


def test_cada_item_pertence_somente_a_lista_em_que_foi_adicionado(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    mercado = listas.criar("Mercado da semana")
    churrasco = listas.criar("Churrasco de sábado")

    listas.adicionar_item(churrasco.id, "Carvão")

    assert [item.nome for item in listas.obter(mercado.id).itens] == []
    assert [item.nome for item in listas.obter(churrasco.id).itens] == ["Carvão"]


def test_adicionar_item_a_uma_lista_inexistente_da_erro_de_nao_encontrado_e_nada_e_gravado(
    tmp_path,
):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")

    with pytest.raises(ErroNaoEncontrado):
        listas.adicionar_item("identificador-que-nao-existe", "Leite")

    assert list(listas.obter(lista.id).itens) == []


def test_os_itens_sobrevivem_a_reabrir_o_modulo_sobre_o_mesmo_arquivo_de_dados(
    tmp_path,
):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    listas.adicionar_item(lista.id, "Leite", "2 L")
    listas.adicionar_item(lista.id, "Pão")

    itens = Listas(caminho).obter(lista.id).itens

    assert [(item.nome, item.quantidade, item.comprado) for item in itens] == [
        ("Leite", "2 L", False),
        ("Pão", None, False),
    ]
