# clt_vs_pj.py

# ══════════════════════════════════════════════════════════════════
# TABELAS OFICIAIS 2026
# ══════════════════════════════════════════════════════════════════

INSS_FAIXAS = [
    (1621.00, 0.075),
    (2902.85, 0.090),
    (4354.27, 0.120),
    (8475.55, 0.140),
]

TETO_INSS = 8475.55

IRRF_FAIXAS = [
    (2428.80, 0.000, 0.00),
    (2826.65, 0.075, 182.16),
    (3751.05, 0.150, 394.16),
    (4664.68, 0.225, 675.49),
    (float("inf"), 0.275, 908.73),
]

DESCONTO_SIMPLIFICADO = 607.20
DEDUCAO_DEPENDENTE = 189.59

LIMITE_ISENCAO_MENSAL = 5000.00
LIMITE_REDUCAO_MENSAL = 7350.00
REDUTOR_FIXO = 312.89
REDUTOR_A = 978.62
REDUTOR_B = 0.133145

# Tabelas do Simples para simulação do app
# Fórmula da alíquota efetiva:
# ((RBT12 * aliquota_nominal) - parcela_deduzir) / RBT12

ANEXO_III = [
    (180000.00, 0.06, 0.00),
    (360000.00, 0.112, 9360.00),
    (720000.00, 0.135, 17640.00),
    (1800000.00, 0.16, 35640.00),
    (3600000.00, 0.21, 125640.00),
    (4800000.00, 0.33, 648000.00),
]

ANEXO_V = [
    (180000.00, 0.155, 0.00),
    (360000.00, 0.18, 4500.00),
    (720000.00, 0.195, 9900.00),
    (1800000.00, 0.205, 17100.00),
    (3600000.00, 0.23, 62100.00),
    (4800000.00, 0.305, 540000.00),
]


def brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(valor: float) -> str:
    return f"{valor * 100:.2f}%".replace(".", ",")


def calcular_inss_clt(salario: float) -> float:
    inss = 0.0
    teto_anterior = 0.0
    base = min(salario, TETO_INSS)

    for teto, aliquota in INSS_FAIXAS:
        if base <= teto_anterior:
            break
        faixa = min(base, teto) - teto_anterior
        inss += faixa * aliquota
        teto_anterior = teto
        if base <= teto:
            break

    return round(inss, 2)


def calcular_base_irrf(salario: float, inss: float, num_dependentes: int) -> float:
    deducao_dep = num_dependentes * DEDUCAO_DEPENDENTE
    deducao_total = inss + deducao_dep

    if num_dependentes == 0 and deducao_total < DESCONTO_SIMPLIFICADO:
        base = max(0.0, salario - DESCONTO_SIMPLIFICADO)
    else:
        base = max(0.0, salario - deducao_total)

    return round(base, 2)


def calcular_irrf(base_calculo: float, renda_bruta: float) -> float:
    if base_calculo <= 0:
        return 0.0

    irrf_bruto = 0.0
    for limite, aliquota, deducao in IRRF_FAIXAS:
        if base_calculo <= limite:
            irrf_bruto = max(0.0, base_calculo * aliquota - deducao)
            break

    if renda_bruta <= LIMITE_ISENCAO_MENSAL:
        redutor = min(irrf_bruto, REDUTOR_FIXO)
    elif renda_bruta <= LIMITE_REDUCAO_MENSAL:
        redutor = max(0.0, REDUTOR_A - REDUTOR_B * renda_bruta)
        redutor = min(redutor, irrf_bruto)
    else:
        redutor = 0.0

    return round(max(0.0, irrf_bruto - redutor), 2)


def calcular_clt(
    salario: float,
    bonus_mensal: float = 0,
    vale_refeicao: float = 0,
    ajuda_internet: float = 0,
    desconto_saude: float = 0,
    desconto_vt: float = 0,
    num_dependentes: int = 0,
) -> dict:
    fgts_emp = round(salario * 0.08, 2)
    dec_terceiro = round(salario / 12, 2)
    ferias_1_3 = round((salario / 12) * (4 / 3), 2)

    total_pacote = round(
        salario
        + bonus_mensal
        + vale_refeicao
        + ajuda_internet
        + fgts_emp
        + dec_terceiro
        + ferias_1_3,
        2,
    )

    inss = calcular_inss_clt(salario)
    base_irrf = calcular_base_irrf(salario, inss, num_dependentes)
    irrf = calcular_irrf(base_irrf, salario)

    total_desc = round(inss + irrf + desconto_saude + desconto_vt, 2)

    liquido = round(
        salario + bonus_mensal - inss - irrf - desconto_saude - desconto_vt,
        2,
    )

    poder_compra = round(liquido + vale_refeicao + ajuda_internet, 2)

    return {
        "fgts_emp": fgts_emp,
        "dec_terceiro": dec_terceiro,
        "ferias_1_3": ferias_1_3,
        "total_pacote": total_pacote,
        "inss": inss,
        "base_irrf": base_irrf,
        "irrf": irrf,
        "total_desc": total_desc,
        "liquido": liquido,
        "poder_compra": poder_compra,
        "liquido_anual": round(liquido * 12, 2),
    }


def obter_faixa_simples(rbt12: float, tabela: list) -> tuple:
    for limite, aliquota, deducao in tabela:
        if rbt12 <= limite:
            return limite, aliquota, deducao
    return tabela[-1]


def calcular_aliquota_efetiva_simples(rbt12: float, tabela: list) -> dict:
    limite, aliquota_nominal, parcela_deduzir = obter_faixa_simples(rbt12, tabela)
    aliquota_efetiva = ((rbt12 * aliquota_nominal) - parcela_deduzir) / rbt12
    aliquota_efetiva = max(0.0, aliquota_efetiva)

    return {
        "limite_faixa": limite,
        "aliquota_nominal": aliquota_nominal,
        "parcela_deduzir": parcela_deduzir,
        "aliquota_efetiva": aliquota_efetiva,
    }


def calcular_fator_r(receita_mensal: float, prolabore_mensal: float) -> dict:
    rbt12 = receita_mensal * 12
    folha12 = prolabore_mensal * 12
    fator_r = (folha12 / rbt12) if rbt12 > 0 else 0.0

    return {
        "rbt12": round(rbt12, 2),
        "folha12": round(folha12, 2),
        "fator_r": round(fator_r, 4),
        "atingiu_fator_r": fator_r >= 0.28,
    }


def calcular_simples_tecnologia(receita_mensal: float, prolabore_mensal: float) -> dict:
    fator = calcular_fator_r(receita_mensal, prolabore_mensal)

    if fator["atingiu_fator_r"]:
        anexo = "III"
        tabela = ANEXO_III
    else:
        anexo = "V"
        tabela = ANEXO_V

    faixa = calcular_aliquota_efetiva_simples(fator["rbt12"], tabela)
    imposto_mensal = round(receita_mensal * faixa["aliquota_efetiva"], 2)

    return {
        **fator,
        **faixa,
        "anexo": anexo,
        "imposto_mensal": imposto_mensal,
        "imposto_anual": round(imposto_mensal * 12, 2),
    }


def calcular_simples_generico(receita_mensal: float, anexo_manual: str = "III") -> dict:
    rbt12 = receita_mensal * 12
    tabela = ANEXO_III if anexo_manual == "III" else ANEXO_V
    faixa = calcular_aliquota_efetiva_simples(rbt12, tabela)
    imposto_mensal = round(receita_mensal * faixa["aliquota_efetiva"], 2)

    return {
        "rbt12": round(rbt12, 2),
        "anexo": anexo_manual,
        **faixa,
        "imposto_mensal": imposto_mensal,
        "imposto_anual": round(imposto_mensal * 12, 2),
    }


def calcular_pj(
    receita_mensal: float,
    prolabore_mensal: float,
    distribuicao_lucros_mensal: float = 0,
    empresa_tecnologia: bool = True,
    anexo_manual: str = "III",
    plano_saude: float = 0,
    honorarios_contador: float = 0,
    aluguel_coworking: float = 0,
    equipamentos: float = 0,
    internet_telefone: float = 0,
    outros_gastos: float = 0,
    provisionar_ferias: bool = True,
    provisionar_decimo: bool = True,
    provisionar_fgts: bool = True,
    num_dependentes: int = 0,
) -> dict:
    if empresa_tecnologia:
        simples = calcular_simples_tecnologia(receita_mensal, prolabore_mensal)
    else:
        simples = calcular_simples_generico(receita_mensal, anexo_manual)

    inss_pj = calcular_inss_clt(prolabore_mensal)
    base_irrf = calcular_base_irrf(prolabore_mensal, inss_pj, num_dependentes)
    irrf_pj = calcular_irrf(base_irrf, prolabore_mensal)

    total_gastos = round(
        plano_saude
        + honorarios_contador
        + aluguel_coworking
        + equipamentos
        + internet_telefone
        + outros_gastos,
        2,
    )

    res_ferias = round(prolabore_mensal * 0.0833, 2) if provisionar_ferias else 0.0
    res_decimo = round(prolabore_mensal * 0.0833, 2) if provisionar_decimo else 0.0
    res_fgts = round(prolabore_mensal * 0.08, 2) if provisionar_fgts else 0.0
    total_res = round(res_ferias + res_decimo + res_fgts, 2)

    liquido_pessoal = round(
        prolabore_mensal
        + distribuicao_lucros_mensal
        - simples["imposto_mensal"]
        - inss_pj
        - irrf_pj
        - total_gastos
        - total_res,
        2,
    )

    return {
        **simples,
        "receita_mensal": round(receita_mensal, 2),
        "prolabore_mensal": round(prolabore_mensal, 2),
        "distribuicao_lucros_mensal": round(distribuicao_lucros_mensal, 2),
        "inss_pj": inss_pj,
        "base_irrf": base_irrf,
        "irrf_pj": irrf_pj,
        "plano_saude": plano_saude,
        "honorarios_contador": honorarios_contador,
        "aluguel_coworking": aluguel_coworking,
        "equipamentos": equipamentos,
        "internet_telefone": internet_telefone,
        "outros_gastos": outros_gastos,
        "total_gastos": total_gastos,
        "res_ferias": res_ferias,
        "res_decimo": res_decimo,
        "res_fgts": res_fgts,
        "total_res": total_res,
        "liquido": liquido_pessoal,
        "liquido_anual": round(liquido_pessoal * 12, 2),
        "reservas_anuais": round(total_res * 12, 2),
    }


if __name__ == "__main__":
    print("Base de cálculo carregada com suporte a Fator R.")
    print("Use: streamlit run app.py")
