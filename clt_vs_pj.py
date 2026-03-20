"""
╔══════════════════════════════════════════════════════════════════╗
║        ⚖  COMPARATIVO CLT × PJ — Calculadora de Remuneração     ║
║                   Tabelas IRPF / INSS 2026                       ║
╚══════════════════════════════════════════════════════════════════╝

Lei nº 15.270/2025 (Reforma da Renda) — vigente a partir de jan/2026:
  • Isenção total de IRPF para renda mensal até R$ 5.000
  • Redução gradual para rendas entre R$ 5.000,01 e R$ 7.350
  • Acima de R$ 7.350: tabela progressiva normal (7,5% a 27,5%)

Como usar:
  1. Preencha os valores na seção INSIRA SEUS DADOS abaixo
  2. Execute: python clt_vs_pj.py
  3. Analise o relatório impresso no terminal

Campos marcados com (você) precisam ser preenchidos por você.
Campos marcados com (auto) são calculados automaticamente.
"""

# ══════════════════════════════════════════════════════════════════
# INSIRA SEUS DADOS — edite apenas esta seção
# ══════════════════════════════════════════════════════════════════

# ── CLT ───────────────────────────────────────────────────────────
SALARIO_CLT         = None   # (você) Salário bruto mensal — ex: 8000
BONUS_CLT           = 0      # (você) Bônus / comissões mensais médios
VALE_REFEICAO       = 0      # (você) Vale refeição / alimentação — ex: 800
AJUDA_INTERNET_CLT  = 0      # (você) Ajuda de custo internet — ex: 100
DESCONTO_SAUDE_CLT  = 0      # (você) Desconto plano saúde (parte do funcionário) — ex: 400
DESCONTO_VT         = 0      # (você) Desconto vale-transporte (max 6% salário; 0 se home office)
NUM_DEPENDENTES_CLT = 0      # (você) Número de dependentes (reduz base IRRF em R$189,59 cada)

# ── PJ ────────────────────────────────────────────────────────────
PROLABORE_PJ         = None  # (você) Faturamento / pró-labore bruto mensal — ex: 15000
BONUS_PJ             = 0     # (você) Bônus / comissões mensais médios
ALIQUOTA_SIMPLES     = 0.09  # (você) Alíquota DAS / Simples Nacional (padrão 9%)

# Gastos operacionais mensais — o que o PJ paga do próprio bolso
PLANO_SAUDE_PJ       = 0     # (você) Plano de saúde — ex: 1200
HONORARIOS_CONTADOR  = 0     # (você) Honorários do contador — ex: 350
ALUGUEL_COWORKING    = 0     # (você) Aluguel escritório / coworking — ex: 600
EQUIPAMENTOS         = 0     # (você) Depreciação mensal de equipamentos — ex: 200
INTERNET_TELEFONE    = 0     # (você) Internet / telefone profissional — ex: 120
OUTROS_GASTOS        = 0     # (você) Outros gastos operacionais

# Provisões voluntárias — deixe True para comparação justa com CLT
PROVISIONAR_FERIAS   = True  # (você) Provisionar férias (8,33% do pró-labore)?
PROVISIONAR_DECIMO   = True  # (você) Provisionar 13º salário (8,33%)?
PROVISIONAR_FGTS     = True  # (você) Provisionar FGTS voluntário (8%)?


# ══════════════════════════════════════════════════════════════════
# TABELAS OFICIAIS 2026 — não altere abaixo desta linha
# ══════════════════════════════════════════════════════════════════

# Tabela INSS 2026 — progressiva (empregado CLT)
# (teto_da_faixa, aliquota)
INSS_FAIXAS = [
    (1_621.00, 0.075),
    (2_902.85, 0.090),
    (4_354.27, 0.120),
    (8_475.55, 0.140),
]
TETO_INSS = 8_475.55  # acima disso não há desconto adicional

# Tabela IRRF 2026 — progressiva mensal (sem alteração em relação a mai/2025)
# (limite_superior, aliquota, parcela_a_deduzir)
IRRF_FAIXAS = [
    (2_428.80,      0.000,   0.00),
    (2_826.65,      0.075, 182.16),
    (3_751.05,      0.150, 394.16),
    (4_664.68,      0.225, 675.49),
    (float("inf"), 0.275, 908.73),
]

DESCONTO_SIMPLIFICADO = 607.20   # desconto simplificado mensal IRRF
DEDUCAO_DEPENDENTE    = 189.59   # dedução por dependente por mês

# Redutor Lei 15.270/2025 — isenção/redução IRPF a partir de jan/2026
LIMITE_ISENCAO_MENSAL = 5_000.00
LIMITE_REDUCAO_MENSAL = 7_350.00
REDUTOR_FIXO          = 312.89    # zera o IR para renda <= R$ 5.000
REDUTOR_A             = 978.62    # coeficientes faixa intermediária
REDUTOR_B             = 0.133145  # redutor = 978.62 - 0.133145 * renda_bruta


# ══════════════════════════════════════════════════════════════════
# FUNÇÕES DE CÁLCULO
# ══════════════════════════════════════════════════════════════════

def calcular_inss_clt(salario: float) -> float:
    """
    INSS progressivo 2026 — empregado CLT.
    Cada faixa é tributada apenas sobre o valor que cai nela.
    Salários acima do teto (R$ 8.475,55) não geram desconto adicional.
    """
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
    """
    Base de cálculo do IRRF = salário − deduções.
    Usa o desconto simplificado (R$ 607,20) quando for maior que INSS sem dependentes.
    """
    deducao_dep = num_dependentes * DEDUCAO_DEPENDENTE
    deducao_total = inss + deducao_dep
    if num_dependentes == 0 and deducao_total < DESCONTO_SIMPLIFICADO:
        base = max(0.0, salario - DESCONTO_SIMPLIFICADO)
    else:
        base = max(0.0, salario - deducao_total)
    return round(base, 2)


def calcular_irrf(base_calculo: float, renda_bruta: float) -> float:
    """
    IRRF 2026 com redutor da Lei 15.270/2025 (Reforma da Renda).

    Passo 1: imposto pela tabela progressiva tradicional.
    Passo 2: aplica redutor conforme a renda bruta mensal:
      - renda <= R$5.000 → redutor zera o imposto
      - R$5.000 < renda <= R$7.350 → redutor = 978,62 − (0,133145 × renda)
      - renda > R$7.350 → sem redutor
    """
    if base_calculo <= 0:
        return 0.0

    # Passo 1: tabela progressiva
    irrf_bruto = 0.0
    for limite, aliquota, deducao in IRRF_FAIXAS:
        if base_calculo <= limite:
            irrf_bruto = max(0.0, base_calculo * aliquota - deducao)
            break

    # Passo 2: redutor
    if renda_bruta <= LIMITE_ISENCAO_MENSAL:
        redutor = min(irrf_bruto, REDUTOR_FIXO)  # limitado ao imposto apurado
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
    """Calcula remuneração líquida no regime CLT — 2026."""

    # 1. Pacote / custo total para o empregador
    fgts_emp      = round(salario * 0.08, 2)
    dec_terceiro  = round(salario / 12, 2)
    ferias_1_3    = round(salario / 12 * (4 / 3), 2)
    total_pacote  = round(
        salario + bonus_mensal + vale_refeicao + ajuda_internet
        + fgts_emp + dec_terceiro + ferias_1_3, 2
    )

    # 2. Descontos
    inss      = calcular_inss_clt(salario)
    base_irrf = calcular_base_irrf(salario, inss, num_dependentes)
    irrf      = calcular_irrf(base_irrf, salario)
    total_desc = round(inss + irrf + desconto_saude + desconto_vt, 2)

    # 3. Líquido mensal em conta
    liquido   = round(salario + bonus_mensal - inss - irrf - desconto_saude - desconto_vt, 2)
    poder_compra = round(liquido + vale_refeicao + ajuda_internet, 2)

    # 4. Projeção anual
    aliq_efetiva_irrf = round(irrf / salario * 100, 2) if salario else 0.0
    carga_total       = round(total_desc / salario * 100, 2) if salario else 0.0

    return {
        "fgts_emp": fgts_emp, "dec_terceiro": dec_terceiro, "ferias_1_3": ferias_1_3,
        "total_pacote": total_pacote,
        "inss": inss, "base_irrf": base_irrf, "irrf": irrf,
        "aliq_efetiva_irrf": aliq_efetiva_irrf, "carga_total": carga_total,
        "desconto_saude": desconto_saude, "desconto_vt": desconto_vt,
        "total_desc": total_desc,
        "liquido": liquido, "poder_compra": poder_compra,
        "vale_refeicao": vale_refeicao, "ajuda_internet": ajuda_internet,
        "liquido_anual": round(liquido * 12, 2),
        "fgts_anual": round(fgts_emp * 12 * 1.4, 2),  # 8% + multa rescisória 40%
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
    """
    Calcula remuneração líquida no regime PJ / Simples Nacional — 2026.

    O pró-labore está sujeito a INSS (sócio) e IRRF, assim como CLT.
    O DAS/Simples incide sobre o faturamento bruto da empresa.
    Distribuição de lucros não é modelada aqui (isenta de IR até os
    limites da Lei 15.270/2025, mas depende do lucro real contábil).
    """
    total_pacote = round(prolabore + bonus_mensal, 2)

    # Imposto empresa (DAS)
    imposto_pj = round(prolabore * aliquota_simples, 2)

    # INSS + IRRF sobre o pró-labore (obrigação do sócio)
    inss_pj   = calcular_inss_clt(prolabore)
    base_irrf = calcular_base_irrf(prolabore, inss_pj, num_dependentes)
    irrf_pj   = calcular_irrf(base_irrf, prolabore)

    # Gastos operacionais
    total_gastos = round(
        plano_saude + honorarios_contador + aluguel_coworking
        + equipamentos + internet_telefone + outros_gastos, 2
    )

    # Reservas voluntárias
    res_ferias = round(prolabore * 0.0833, 2) if provisionar_ferias else 0.0
    res_decimo = round(prolabore * 0.0833, 2) if provisionar_decimo else 0.0
    res_fgts   = round(prolabore * 0.08,   2) if provisionar_fgts   else 0.0
    total_res  = round(res_ferias + res_decimo + res_fgts, 2)

    # Líquido
    liquido = round(
        prolabore + bonus_mensal
        - imposto_pj - inss_pj - irrf_pj
        - total_gastos - total_res, 2
    )

    aliq_efetiva_irrf = round(irrf_pj / prolabore * 100, 2) if prolabore else 0.0
    carga_total = round((imposto_pj + inss_pj + irrf_pj) / prolabore * 100, 2) if prolabore else 0.0

    return {
        "total_pacote": total_pacote,
        "imposto_pj": imposto_pj, "inss_pj": inss_pj,
        "base_irrf": base_irrf, "irrf_pj": irrf_pj,
        "aliq_efetiva_irrf": aliq_efetiva_irrf, "carga_total": carga_total,
        "plano_saude": plano_saude, "honorarios_contador": honorarios_contador,
        "aluguel_coworking": aluguel_coworking, "equipamentos": equipamentos,
        "internet_telefone": internet_telefone, "outros_gastos": outros_gastos,
        "total_gastos": total_gastos,
        "res_ferias": res_ferias, "res_decimo": res_decimo, "res_fgts": res_fgts,
        "total_res": total_res,
        "liquido": liquido,
        "liquido_anual": round(liquido * 12, 2),
        "reservas_anuais": round(total_res * 12, 2),
    }


# ══════════════════════════════════════════════════════════════════
# RELATÓRIO
# ══════════════════════════════════════════════════════════════════

def brl(v) -> str:
    if isinstance(v, (int, float)):
        return f"R$ {v:>12,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(v)

def pct(v: float) -> str:
    return f"{v:.2f}%"

def sinal_brl(v: float) -> str:
    s = "+" if v >= 0 else ""
    return f"{s}{brl(v).strip()}"


def relatorio(clt: dict, pj: dict, sal: float, pro: float) -> None:
    sep = "─" * 70
    d_bruto = pj["liquido"] - clt["liquido"]
    d_real  = pj["liquido"] - clt["poder_compra"]  # descontando VR/VA CLT
    d_anual = pj["liquido_anual"] - clt["liquido_anual"]

    print()
    print("=" * 70)
    print("  ⚖  COMPARATIVO CLT × PJ — Calculadora de Remuneração 2026")
    print("=" * 70)
    print(f"\n{'':40s} {'CLT':>13}   {'PJ':>13}")
    print(sep)

    print("\n  1. REMUNERAÇÃO BRUTA (pacote / custo total para o empregador/empresa)")
    print(f"  {'Salário / Pró-labore bruto':<38} {brl(sal):>13}   {brl(pro):>13}")
    print(f"  {'FGTS empregador (8%)':<38} {brl(clt['fgts_emp']):>13}   {'—':>13}")
    print(f"  {'13º provisionado (1/12 salário)':<38} {brl(clt['dec_terceiro']):>13}   {'—':>13}")
    print(f"  {'Férias + 1/3 provisionadas':<38} {brl(clt['ferias_1_3']):>13}   {'—':>13}")
    print(f"  {'VR / VA / Ajuda internet':<38} {brl(clt['vale_refeicao']+clt['ajuda_internet']):>13}   {'—':>13}")
    print(f"  {'TOTAL PACOTE / CUSTO EMPRESA':<38} {brl(clt['total_pacote']):>13}   {brl(pj['total_pacote']):>13}")

    print(f"\n  2. IMPOSTOS E DESCONTOS")
    print(f"  {'INSS (progressivo 2026)':<38} {brl(clt['inss']):>13}   {brl(pj['inss_pj']):>13}")
    print(f"  {'Base de cálculo IRRF':<38} {brl(clt['base_irrf']):>13}   {brl(pj['base_irrf']):>13}")
    print(f"  {'IRRF  (com redutor Lei 15.270/2025)':<38} {brl(clt['irrf']):>13}   {brl(pj['irrf_pj']):>13}")
    print(f"  {'Alíquota efetiva de IRRF':<38} {pct(clt['aliq_efetiva_irrf']):>13}   {pct(pj['aliq_efetiva_irrf']):>13}")
    print(f"  {'Plano saúde (desc. funcionário CLT)':<38} {brl(clt['desconto_saude']):>13}   {'—':>13}")
    print(f"  {'Vale-transporte (desc.)':<38} {brl(clt['desconto_vt']):>13}   {'—':>13}")
    print(f"  {'Imposto PJ — DAS / Simples Nacional':<38} {'—':>13}   {brl(pj['imposto_pj']):>13}")
    carga_clt = clt['total_desc']/sal*100 if sal else 0
    print(f"  {'Carga tributária total sobre bruto':<38} {pct(carga_clt):>13}   {pct(pj['carga_total']):>13}")

    print(f"\n  3. GASTOS OPERACIONAIS (CLT não tem — a empresa paga por você)")
    print(f"  {'Plano de saúde (custo total PJ)':<38} {'—':>13}   {brl(pj['plano_saude']):>13}")
    print(f"  {'Honorários contador':<38} {'—':>13}   {brl(pj['honorarios_contador']):>13}")
    print(f"  {'Escritório / Coworking':<38} {'—':>13}   {brl(pj['aluguel_coworking']):>13}")
    print(f"  {'Equipamentos / Depreciação':<38} {'—':>13}   {brl(pj['equipamentos']):>13}")
    print(f"  {'Internet / Telefone profissional':<38} {'—':>13}   {brl(pj['internet_telefone']):>13}")
    print(f"  {'Outros gastos':<38} {'—':>13}   {brl(pj['outros_gastos']):>13}")
    print(f"  {'TOTAL GASTOS OPERACIONAIS':<38} {'—':>13}   {brl(pj['total_gastos']):>13}")

    print(f"\n  4. RESERVAS SUGERIDAS PJ (equivalem a benefícios garantidos no CLT)")
    print(f"  {'Férias (8,33% pró-labore)':<38} {'—':>13}   {brl(pj['res_ferias']):>13}")
    print(f"  {'13º salário (8,33%)':<38} {'—':>13}   {brl(pj['res_decimo']):>13}")
    print(f"  {'FGTS voluntário (8%)':<38} {'—':>13}   {brl(pj['res_fgts']):>13}")
    print(f"  {'TOTAL RESERVAS':<38} {'—':>13}   {brl(pj['total_res']):>13}")

    print(f"\n{sep}")
    print(f"\n  5. RESULTADO LIQUIDO MENSAL (o que entra na conta)")
    print(f"  {'CLT — líquido em conta':<38} {brl(clt['liquido']):>13}")
    print(f"  {'CLT — poder de compra (+ VR/VA)':<38} {brl(clt['poder_compra']):>13}")
    print(f"  {'PJ  — líquido disponível':<38} {brl(pj['liquido']):>13}")
    print(f"\n  {'Diferença bruta   (PJ - CLT líquido)':<38} {sinal_brl(d_bruto):>13}")
    print(f"  {'Diferença real    (PJ - CLT c/ VR/VA)':<38} {sinal_brl(d_real):>13}")

    print(f"\n  6. PROJECAO ANUAL")
    print(f"  {'Líquido anual CLT (× 12)':<38} {brl(clt['liquido_anual']):>13}")
    print(f"  {'FGTS acum. + multa 40% (rescisão)':<38} {brl(clt['fgts_anual']):>13}")
    print(f"  {'13º bruto':<38} {brl(clt['decimo_bruto']):>13}")
    print(f"  {'Férias + 1/3 brutas':<38} {brl(clt['ferias_brutas']):>13}")
    print(f"  {'Líquido anual PJ (× 12)':<38} {brl(pj['liquido_anual']):>13}")
    print(f"  {'Reservas anuais constituídas PJ':<38} {brl(pj['reservas_anuais']):>13}")
    print(f"\n  {'Diferença anual (PJ - CLT líquido)':<38} {sinal_brl(d_anual):>13}")

    print(f"\n{sep}")
    print(f"\n  VEREDITO")
    print()

    ref = d_real  # usa diferença real (com benefícios CLT)
    if ref > 0:
        print(f"  >> PJ rende {brl(ref).strip()}/mês a MAIS (considerando VR/VA e benefícios CLT)")
        print(f"     = {brl(ref * 12).strip()} extras por ano")
        print(f"     = {ref/pro*100:.1f}% do pró-labore PJ")
    elif ref < 0:
        print(f"  >> CLT rende {brl(abs(ref)).strip()}/mês a MAIS (considerando VR/VA e benefícios CLT)")
        print(f"     = {brl(abs(ref) * 12).strip()} a mais por ano")
        print(f"     Para o PJ empatar, precisaria receber +{brl(abs(ref)).strip()}/mês a mais de pró-labore")
    else:
        print("  >> CLT e PJ têm resultado líquido equivalente.")

    if pj["total_res"] > 0:
        liq_sem_res = pj["liquido"] + pj["total_res"]
        print(f"\n  ATENCAO: sem as reservas ({brl(pj['total_res']).strip()}/mês), o PJ teria")
        print(f"  {brl(liq_sem_res).strip()}/mês — mas ficaria sem cobertura para férias, 13º e rescisão.")

    print(f"\n{sep}")
    print(f"\n  NOTAS E PREMISSAS (2026)")
    print(f"  > INSS progressivo 2026:")
    print(f"    7,5% ate R$1.621 | 9% ate R$2.902,85 | 12% ate R$4.354,27 | 14% ate R$8.475,55")
    print(f"  > IRRF 2026 — tabela progressiva + redutor Lei 15.270/2025:")
    print(f"    Isento ate R$5.000/mes | reducao gradual ate R$7.350 | normal acima disso")
    print(f"    Redutor intermediario: R$978,62 - (0,133145 x renda bruta)")
    print(f"  > Desconto simplificado mensal IRRF: R${DESCONTO_SIMPLIFICADO:.2f}")
    print(f"  > Deducao por dependente: R${DEDUCAO_DEPENDENTE:.2f}/mes")
    print(f"  > Imposto PJ = DAS Simples Nacional ({ALIQUOTA_SIMPLES*100:.0f}%). Ajuste conforme seu anexo.")
    print(f"  > FGTS CLT: 8% empregador + multa rescisoria 40% na projecao anual.")
    print(f"  > Distribuicao de lucros PJ: isenta de IR (ate o limite da lei) — nao modelada aqui.")
    print(f"  > VR/VA e ajuda internet CLT: carater indenizatorio, sem INSS/IRRF.")
    print(f"  > Reservas PJ sao voluntarias — você decide se provisiona ou nao.")
    print()


# ══════════════════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════

def validar():
    erros = []
    if SALARIO_CLT is None:
        erros.append("  SALARIO_CLT nao preenchido  ->  ex: SALARIO_CLT = 8000")
    if PROLABORE_PJ is None:
        erros.append("  PROLABORE_PJ nao preenchido ->  ex: PROLABORE_PJ = 15000")
    if erros:
        print("\n  Preencha os campos obrigatórios antes de executar:\n")
        for e in erros:
            print(e)
        print("\n  Edite a secao 'INSIRA SEUS DADOS' no inicio do arquivo.\n")
        return False
    if SALARIO_CLT <= 0 or PROLABORE_PJ <= 0:
        print("\n  Salário e Pró-labore devem ser maiores que zero.\n")
        return False
    return True


if __name__ == "__main__":
    if not validar():
        exit(1)

    clt = calcular_clt(
        salario        = SALARIO_CLT,
        bonus_mensal   = BONUS_CLT,
        vale_refeicao  = VALE_REFEICAO,
        ajuda_internet = AJUDA_INTERNET_CLT,
        desconto_saude = DESCONTO_SAUDE_CLT,
        desconto_vt    = DESCONTO_VT,
        num_dependentes= NUM_DEPENDENTES_CLT,
    )

    pj = calcular_pj(
        prolabore           = PROLABORE_PJ,
        bonus_mensal        = BONUS_PJ,
        aliquota_simples    = ALIQUOTA_SIMPLES,
        plano_saude         = PLANO_SAUDE_PJ,
        honorarios_contador = HONORARIOS_CONTADOR,
        aluguel_coworking   = ALUGUEL_COWORKING,
        equipamentos        = EQUIPAMENTOS,
        internet_telefone   = INTERNET_TELEFONE,
        outros_gastos       = OUTROS_GASTOS,
        provisionar_ferias  = PROVISIONAR_FERIAS,
        provisionar_decimo  = PROVISIONAR_DECIMO,
        provisionar_fgts    = PROVISIONAR_FGTS,
        num_dependentes     = NUM_DEPENDENTES_CLT,
    )

    relatorio(clt, pj, SALARIO_CLT, PROLABORE_PJ)
