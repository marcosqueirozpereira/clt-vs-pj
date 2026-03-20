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


def calcular_inss_clt(salario: float) -> float:
    """Calcula INSS progressivo 2026."""
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
    """Calcula base do IRRF."""
    deducao_dep = num_dependentes * DEDUCAO_DEPENDENTE
    deducao_total = inss + deducao_dep

    if num_dependentes == 0 and deducao_total < DESCONTO_SIMPLIFICADO:
        base = max(0.0, salario - DESCONTO_SIMPLIFICADO)
    else:
        base = max(0.0, salario - deducao_total)

    return round(base, 2)


def calcular_irrf(base_calculo: float, renda_bruta: float) -> float:
    """Calcula IRRF 2026 com redutor."""
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
    """Calcula CLT."""
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

    aliq_efetiva_irrf = round((irrf / salario) * 100, 2) if salario else 0.0
    carga_total = round((total_desc / salario) * 100, 2) if salario else 0.0

    return {
        "fgts_emp": fgts_emp,
        "dec_terceiro": dec_terceiro,
        "ferias_1_3": ferias_1_3,
        "total_pacote": total_pacote,
        "inss": inss,
        "base_irrf": base_irrf,
        "irrf": irrf,
        "aliq_efetiva_irrf": aliq_efetiva_irrf,
        "carga_total": carga_total,
        "desconto_saude": desconto_saude,
        "desconto_vt": desconto_vt,
        "total_desc": total_desc,
        "liquido": liquido,
        "poder_compra": poder_compra,
        "vale_refeicao": vale_refeicao,
        "ajuda_internet": ajuda_internet,
        "liquido_anual": round(liquido * 12, 2),
        "fgts_anual": round(fgts_emp * 12 * 1.4, 2),
        "decimo_bruto": salario,
        "ferias_brutas": round(salario * 4 / 3, 2),
    }


def calcular_pj(
    prolabore: float,
    bonus_mensal: float = 0,
    aliquota_simples: float = 0.09,
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
    """Calcula PJ."""
    total_pacote = round(prolabore + bonus_mensal, 2)

    imposto_pj = round(prolabore * aliquota_simples, 2)

    inss_pj = calcular_inss_clt(prolabore)
    base_irrf = calcular_base_irrf(prolabore, inss_pj, num_dependentes)
    irrf_pj = calcular_irrf(base_irrf, prolabore)

    total_gastos = round(
        plano_saude
        + honorarios_contador
        + aluguel_coworking
        + equipamentos
        + internet_telefone
        + outros_gastos,
        2,
    )

    res_ferias = round(prolabore * 0.0833, 2) if provisionar_ferias else 0.0
    res_decimo = round(prolabore * 0.0833, 2) if provisionar_decimo else 0.0
    res_fgts = round(prolabore * 0.08, 2) if provisionar_fgts else 0.0
    total_res = round(res_ferias + res_decimo + res_fgts, 2)

    liquido = round(
        prolabore
        + bonus_mensal
        - imposto_pj
        - inss_pj
        - irrf_pj
        - total_gastos
        - total_res,
        2,
    )

    aliq_efetiva_irrf = round((irrf_pj / prolabore) * 100, 2) if prolabore else 0.0
    carga_total = round(((imposto_pj + inss_pj + irrf_pj) / prolabore) * 100, 2) if prolabore else 0.0

    return {
        "total_pacote": total_pacote,
        "imposto_pj": imposto_pj,
        "inss_pj": inss_pj,
        "base_irrf": base_irrf,
        "irrf_pj": irrf_pj,
        "aliq_efetiva_irrf": aliq_efetiva_irrf,
        "carga_total": carga_total,
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
        "liquido": liquido,
        "liquido_anual": round(liquido * 12, 2),
        "reservas_anuais": round(total_res * 12, 2),
    }


def brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


if __name__ == "__main__":
    print("Este arquivo agora é a base de cálculo do app.")
    print("Para abrir a interface visual, rode: streamlit run app.py")
