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


def test_marcar_um_item_pendente_como_comprado_o_deixa_comprado(tmp_path):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite")

    listas.marcar_como_comprado(lista.id, leite.id)

    assert [(item.nome, item.comprado) for item in listas.obter(lista.id).itens] == [
        ("Leite", True)
    ]
    assert [item.comprado for item in Listas(caminho).obter(lista.id).itens] == [True]


def test_voltar_um_item_comprado_para_pendente_o_deixa_pendente(tmp_path):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite", "2 L")
    listas.marcar_como_comprado(lista.id, leite.id)

    listas.voltar_para_pendente(lista.id, leite.id)

    itens = listas.obter(lista.id).itens
    assert [(item.nome, item.quantidade, item.comprado) for item in itens] == [
        ("Leite", "2 L", False)
    ]
    assert [item.comprado for item in Listas(caminho).obter(lista.id).itens] == [False]


@pytest.mark.parametrize("operacao", ["marcar_como_comprado", "voltar_para_pendente"])
def test_mudar_o_estado_de_um_item_inexistente_da_erro_de_nao_encontrado_e_nada_muda(
    tmp_path, operacao
):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite")
    pao = listas.adicionar_item(lista.id, "Pão")
    listas.marcar_como_comprado(lista.id, pao.id)
    outra = listas.criar("Churrasco de sábado")

    with pytest.raises(ErroNaoEncontrado):
        getattr(listas, operacao)(lista.id, "identificador-que-nao-existe")
    with pytest.raises(ErroNaoEncontrado):
        getattr(listas, operacao)("identificador-que-nao-existe", leite.id)
    # O Item existe, mas pertence a outra Lista.
    with pytest.raises(ErroNaoEncontrado):
        getattr(listas, operacao)(outra.id, leite.id)

    assert [(item.nome, item.comprado) for item in listas.obter(lista.id).itens] == [
        ("Leite", False),
        ("Pão", True),
    ]


def test_a_consulta_da_lista_devolve_os_pendentes_primeiro_e_os_comprados_depois_cada_grupo_na_ordem_de_adicao(
    tmp_path,
):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite")
    listas.adicionar_item(lista.id, "Arroz")
    feijao = listas.adicionar_item(lista.id, "Feijão")
    listas.adicionar_item(lista.id, "Pão")
    ovos = listas.adicionar_item(lista.id, "Ovos")
    # Marcados fora da ordem de adição: o que vale é a ordem de adição.
    listas.marcar_como_comprado(lista.id, ovos.id)
    listas.marcar_como_comprado(lista.id, leite.id)
    listas.marcar_como_comprado(lista.id, feijao.id)

    esperado = [
        ("Arroz", False),
        ("Pão", False),
        ("Leite", True),
        ("Feijão", True),
        ("Ovos", True),
    ]
    assert [
        (item.nome, item.comprado) for item in listas.obter(lista.id).itens
    ] == esperado
    assert [
        (item.nome, item.comprado) for item in Listas(caminho).obter(lista.id).itens
    ] == esperado


def test_um_item_devolvido_a_pendente_volta_ao_seu_lugar_na_ordem_de_adicao(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite")
    listas.adicionar_item(lista.id, "Arroz")
    listas.marcar_como_comprado(lista.id, leite.id)

    listas.voltar_para_pendente(lista.id, leite.id)

    assert [(item.nome, item.comprado) for item in listas.obter(lista.id).itens] == [
        ("Leite", False),
        ("Arroz", False),
    ]


def test_a_consulta_da_lista_devolve_o_progresso_quantos_comprados_do_total_de_itens(
    tmp_path,
):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite")
    arroz = listas.adicionar_item(lista.id, "Arroz")
    listas.adicionar_item(lista.id, "Feijão")

    consultada = listas.obter(lista.id)
    assert (consultada.comprados, consultada.total_de_itens) == (0, 3)

    listas.marcar_como_comprado(lista.id, leite.id)
    listas.marcar_como_comprado(lista.id, arroz.id)
    consultada = listas.obter(lista.id)
    assert (consultada.comprados, consultada.total_de_itens) == (2, 3)

    listas.voltar_para_pendente(lista.id, leite.id)
    consultada = Listas(caminho).obter(lista.id)
    assert (consultada.comprados, consultada.total_de_itens) == (1, 3)


def test_uma_lista_sem_itens_tem_progresso_zero_de_zero(tmp_path):
    listas = Listas(tmp_path / "dados.json")

    criada = listas.criar("Mercado da semana")

    assert (criada.comprados, criada.total_de_itens) == (0, 0)
    consultada = listas.obter(criada.id)
    assert (consultada.comprados, consultada.total_de_itens) == (0, 0)


def test_a_consulta_de_todas_as_listas_devolve_o_progresso_de_cada_uma(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    mercado = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(mercado.id, "Leite")
    listas.adicionar_item(mercado.id, "Arroz")
    listas.adicionar_item(mercado.id, "Feijão")
    listas.marcar_como_comprado(mercado.id, leite.id)
    churrasco = listas.criar("Churrasco de sábado")
    carvao = listas.adicionar_item(churrasco.id, "Carvão")
    listas.marcar_como_comprado(churrasco.id, carvao.id)
    listas.criar("Feira de domingo")

    assert [
        (lista.nome, lista.comprados, lista.total_de_itens) for lista in listas.todas()
    ] == [
        ("Feira de domingo", 0, 0),
        ("Churrasco de sábado", 1, 1),
        ("Mercado da semana", 1, 3),
    ]


def test_desmarcar_todos_devolve_todos_os_itens_ao_estado_pendente_e_zera_o_progresso(
    tmp_path,
):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite")
    listas.adicionar_item(lista.id, "Arroz")
    feijao = listas.adicionar_item(lista.id, "Feijão")
    listas.marcar_como_comprado(lista.id, leite.id)
    listas.marcar_como_comprado(lista.id, feijao.id)

    devolvida = listas.desmarcar_todos(lista.id)

    assert (devolvida.comprados, devolvida.total_de_itens) == (0, 3)
    consultada = Listas(caminho).obter(lista.id)
    assert [item.comprado for item in consultada.itens] == [False, False, False]
    assert (consultada.comprados, consultada.total_de_itens) == (0, 3)


def test_desmarcar_todos_nao_remove_itens_nem_altera_nomes_e_quantidades(tmp_path):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite", "2 L")
    arroz = listas.adicionar_item(lista.id, "Arroz")
    ovos = listas.adicionar_item(lista.id, "Ovos", "1 dúzia")
    listas.marcar_como_comprado(lista.id, leite.id)
    listas.marcar_como_comprado(lista.id, ovos.id)

    listas.desmarcar_todos(lista.id)

    assert [
        (item.id, item.nome, item.quantidade)
        for item in Listas(caminho).obter(lista.id).itens
    ] == [
        (leite.id, "Leite", "2 L"),
        (arroz.id, "Arroz", None),
        (ovos.id, "Ovos", "1 dúzia"),
    ]


def test_desmarcar_todos_nao_afeta_itens_de_outras_listas(tmp_path):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    mercado = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(mercado.id, "Leite")
    listas.marcar_como_comprado(mercado.id, leite.id)
    churrasco = listas.criar("Churrasco de sábado")
    carvao = listas.adicionar_item(churrasco.id, "Carvão", "2 sacos")
    listas.adicionar_item(churrasco.id, "Sal grosso")
    listas.marcar_como_comprado(churrasco.id, carvao.id)

    listas.desmarcar_todos(mercado.id)

    outra = Listas(caminho).obter(churrasco.id)
    assert [(item.nome, item.quantidade, item.comprado) for item in outra.itens] == [
        ("Sal grosso", None, False),
        ("Carvão", "2 sacos", True),
    ]
    assert (outra.comprados, outra.total_de_itens) == (1, 2)


def test_desmarcar_todos_em_lista_inexistente_levanta_erro_de_nao_encontrado(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    mercado = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(mercado.id, "Leite")
    listas.marcar_como_comprado(mercado.id, leite.id)

    with pytest.raises(ErroNaoEncontrado):
        listas.desmarcar_todos("id-que-nao-existe")

    assert listas.obter(mercado.id).comprados == 1


def test_desmarcar_todos_em_lista_sem_itens_a_deixa_vazia(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")

    devolvida = listas.desmarcar_todos(lista.id)

    assert (devolvida.itens, devolvida.comprados, devolvida.total_de_itens) == ((), 0, 0)


def test_editar_um_item_troca_seu_nome_e_sua_quantidade(tmp_path):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite", "2 L")
    listas.adicionar_item(lista.id, "Pão")

    editado = listas.editar_item(lista.id, leite.id, "Leite integral", "3 caixas")

    assert (editado.id, editado.nome, editado.quantidade) == (
        leite.id,
        "Leite integral",
        "3 caixas",
    )
    esperado = [(leite.id, "Leite integral", "3 caixas"), ("Pão", None)]
    for itens in (listas.obter(lista.id).itens, Listas(caminho).obter(lista.id).itens):
        assert (itens[0].id, itens[0].nome, itens[0].quantidade) == esperado[0]
        assert (itens[1].nome, itens[1].quantidade) == esperado[1]


def test_editar_um_item_preserva_seu_estado_pendente_ou_comprado(tmp_path):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite")
    pao = listas.adicionar_item(lista.id, "Pão")
    listas.marcar_como_comprado(lista.id, pao.id)

    pendente_editado = listas.editar_item(lista.id, leite.id, "Leite integral", "2 L")
    comprado_editado = listas.editar_item(lista.id, pao.id, "Pão francês", "6")

    assert (pendente_editado.comprado, comprado_editado.comprado) == (False, True)
    consultada = Listas(caminho).obter(lista.id)
    assert [(item.nome, item.comprado) for item in consultada.itens] == [
        ("Leite integral", False),
        ("Pão francês", True),
    ]
    assert (consultada.comprados, consultada.total_de_itens) == (1, 2)


def test_na_edicao_os_espacos_das_pontas_do_nome_e_da_quantidade_sao_removidos(
    tmp_path,
):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")
    ovos = listas.adicionar_item(lista.id, "Ovo")

    editado = listas.editar_item(lista.id, ovos.id, "  Ovos \t", "  1 dúzia ")

    assert (editado.nome, editado.quantidade) == ("Ovos", "1 dúzia")
    itens = listas.obter(lista.id).itens
    assert [(item.nome, item.quantidade) for item in itens] == [("Ovos", "1 dúzia")]


@pytest.mark.parametrize("quantidade_em_branco", [None, "", "   ", " \t\n "])
def test_na_edicao_quantidade_em_branco_conta_como_ausente(
    tmp_path, quantidade_em_branco
):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite", "2 L")

    editado = listas.editar_item(lista.id, leite.id, "Leite", quantidade_em_branco)

    assert editado.quantidade is None
    assert [item.quantidade for item in listas.obter(lista.id).itens] == [None]


@pytest.mark.parametrize("nome_em_branco", ["", "   ", " \t\n "])
def test_editar_um_item_com_nome_vazio_ou_so_com_espacos_e_rejeitado_com_erro_de_validacao_e_nada_e_gravado(
    tmp_path, nome_em_branco
):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite", "2 L")

    with pytest.raises(ErroDeValidacao) as excecao:
        listas.editar_item(lista.id, leite.id, nome_em_branco, "3 L")

    assert str(excecao.value) == "Informe um nome para o Item."
    for itens in (listas.obter(lista.id).itens, Listas(caminho).obter(lista.id).itens):
        assert [(item.nome, item.quantidade) for item in itens] == [("Leite", "2 L")]


def test_editar_um_item_inexistente_da_erro_de_nao_encontrado_e_nada_muda(tmp_path):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite", "2 L")
    outra = listas.criar("Churrasco de sábado")

    with pytest.raises(ErroNaoEncontrado):
        listas.editar_item(lista.id, "identificador-que-nao-existe", "Arroz", "1 kg")
    with pytest.raises(ErroNaoEncontrado):
        listas.editar_item("identificador-que-nao-existe", leite.id, "Arroz", "1 kg")
    # O Item existe, mas pertence a outra Lista.
    with pytest.raises(ErroNaoEncontrado):
        listas.editar_item(outra.id, leite.id, "Arroz", "1 kg")

    itens = Listas(caminho).obter(lista.id).itens
    assert [(item.nome, item.quantidade) for item in itens] == [("Leite", "2 L")]
    assert list(listas.obter(outra.id).itens) == []


def test_remover_um_item_o_tira_da_lista_e_os_demais_continuam(tmp_path):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    listas.adicionar_item(lista.id, "Leite", "2 L")
    arroz = listas.adicionar_item(lista.id, "Arroz")
    feijao = listas.adicionar_item(lista.id, "Feijão")
    listas.marcar_como_comprado(lista.id, feijao.id)

    listas.remover_item(lista.id, arroz.id)

    esperado = [("Leite", "2 L", False), ("Feijão", None, True)]
    for consultada in (listas.obter(lista.id), Listas(caminho).obter(lista.id)):
        assert [
            (item.nome, item.quantidade, item.comprado) for item in consultada.itens
        ] == esperado
        assert (consultada.comprados, consultada.total_de_itens) == (1, 2)


def test_remover_um_item_inexistente_da_erro_de_nao_encontrado_e_nada_e_removido(
    tmp_path,
):
    caminho = tmp_path / "dados.json"
    listas = Listas(caminho)
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite")
    outra = listas.criar("Churrasco de sábado")
    listas.adicionar_item(outra.id, "Carvão")
    vazia = listas.criar("Feira de domingo")

    with pytest.raises(ErroNaoEncontrado):
        listas.remover_item(lista.id, "identificador-que-nao-existe")
    with pytest.raises(ErroNaoEncontrado):
        listas.remover_item("identificador-que-nao-existe", leite.id)
    # O Item existe, mas pertence a outra Lista.
    with pytest.raises(ErroNaoEncontrado):
        listas.remover_item(outra.id, leite.id)
    with pytest.raises(ErroNaoEncontrado):
        listas.remover_item(vazia.id, leite.id)

    reaberto = Listas(caminho)
    assert [item.nome for item in reaberto.obter(lista.id).itens] == ["Leite"]
    assert [item.nome for item in reaberto.obter(outra.id).itens] == ["Carvão"]


def test_remover_um_item_ja_removido_da_erro_de_nao_encontrado(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite")
    listas.remover_item(lista.id, leite.id)

    with pytest.raises(ErroNaoEncontrado):
        listas.remover_item(lista.id, leite.id)
    with pytest.raises(ErroNaoEncontrado):
        listas.editar_item(lista.id, leite.id, "Leite", "2 L")


def test_obter_um_item_devolve_seu_nome_sua_quantidade_e_seu_estado(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")
    listas.adicionar_item(lista.id, "Leite")
    pao = listas.adicionar_item(lista.id, "Pão", "6")
    listas.marcar_como_comprado(lista.id, pao.id)

    item = listas.obter_item(lista.id, pao.id)

    assert (item.id, item.nome, item.quantidade, item.comprado) == (
        pao.id,
        "Pão",
        "6",
        True,
    )


def test_obter_um_item_inexistente_da_erro_de_nao_encontrado(tmp_path):
    listas = Listas(tmp_path / "dados.json")
    lista = listas.criar("Mercado da semana")
    leite = listas.adicionar_item(lista.id, "Leite")
    outra = listas.criar("Churrasco de sábado")

    with pytest.raises(ErroNaoEncontrado):
        listas.obter_item(lista.id, "identificador-que-nao-existe")
    with pytest.raises(ErroNaoEncontrado):
        listas.obter_item("identificador-que-nao-existe", leite.id)
    # O Item existe, mas pertence a outra Lista.
    with pytest.raises(ErroNaoEncontrado):
        listas.obter_item(outra.id, leite.id)
