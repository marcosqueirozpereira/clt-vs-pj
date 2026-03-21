# app.py

import streamlit as st
from clt_vs_pj import calcular_clt, calcular_pj, brl, pct

st.set_page_config(page_title="Comparador CLT x PJ", page_icon="⚖️", layout="wide")

st.title("⚖️ Comparador CLT x PJ")
st.caption("Simule CLT e PJ com Fator R, anexo do Simples e distribuição de lucros.")

st.subheader("1) Tipo da empresa")
empresa_tecnologia = st.toggle("A empresa é de tecnologia / serviço sujeito a Fator R?", value=True)

st.divider()

c1, c2 = st.columns(2)

with c1:
    st.subheader("CLT")
    salario_clt = st.number_input("Salário bruto mensal (CLT)", min_value=0.0, value=9600.0, step=100.0)
    bonus_clt = st.number_input("Bônus mensal (CLT)", min_value=0.0, value=0.0, step=100.0)
    vale_refeicao = st.number_input("Vale refeição/alimentação", min_value=0.0, value=770.0, step=50.0)
    ajuda_internet_clt = st.number_input("Ajuda internet (CLT)", min_value=0.0, value=0.0, step=50.0)
    desconto_saude_clt = st.number_input("Desconto plano de saúde (CLT)", min_value=0.0, value=0.0, step=50.0)
    desconto_vt = st.number_input("Desconto VT (CLT)", min_value=0.0, value=0.0, step=50.0)
    dependentes_clt = st.number_input("Dependentes (CLT)", min_value=0, value=0, step=1)

with c2:
    st.subheader("PJ")
    receita_mensal = st.number_input("Receita mensal da empresa", min_value=0.0, value=16000.0, step=100.0)
    prolabore_mensal = st.number_input("Pró-labore mensal", min_value=0.0, value=5000.0, step=100.0)
    distribuicao_lucros_mensal = st.number_input("Distribuição de lucros mensal", min_value=0.0, value=11000.0, step=100.0)
    dependentes_pj = st.number_input("Dependentes (PJ)", min_value=0, value=0, step=1)

    if not empresa_tecnologia:
        anexo_manual = st.selectbox("Anexo do Simples", ["III", "V"], index=0)
    else:
        anexo_manual = "III"

    plano_saude_pj = st.number_input("Plano de saúde (PJ)", min_value=0.0, value=0.0, step=50.0)
    honorarios_contador = st.number_input("Honorários do contador", min_value=0.0, value=350.0, step=50.0)
    aluguel_coworking = st.number_input("Coworking / escritório", min_value=0.0, value=0.0, step=50.0)
    equipamentos = st.number_input("Equipamentos", min_value=0.0, value=0.0, step=50.0)
    internet_telefone = st.number_input("Internet / telefone", min_value=0.0, value=0.0, step=50.0)
    outros_gastos = st.number_input("Outros gastos", min_value=0.0, value=0.0, step=50.0)

st.divider()

r1, r2, r3 = st.columns(3)
with r1:
    provisionar_ferias = st.checkbox("Reservar férias no PJ", value=True)
with r2:
    provisionar_decimo = st.checkbox("Reservar 13º no PJ", value=True)
with r3:
    provisionar_fgts = st.checkbox("Reservar FGTS no PJ", value=True)

if st.button("Calcular comparação", use_container_width=True):
    clt = calcular_clt(
        salario=salario_clt,
        bonus_mensal=bonus_clt,
        vale_refeicao=vale_refeicao,
        ajuda_internet=ajuda_internet_clt,
        desconto_saude=desconto_saude_clt,
        desconto_vt=desconto_vt,
        num_dependentes=dependentes_clt,
    )

    pj = calcular_pj(
        receita_mensal=receita_mensal,
        prolabore_mensal=prolabore_mensal,
        distribuicao_lucros_mensal=distribuicao_lucros_mensal,
        empresa_tecnologia=empresa_tecnologia,
        anexo_manual=anexo_manual,
        plano_saude=plano_saude_pj,
        honorarios_contador=honorarios_contador,
        aluguel_coworking=aluguel_coworking,
        equipamentos=equipamentos,
        internet_telefone=internet_telefone,
        outros_gastos=outros_gastos,
        provisionar_ferias=provisionar_ferias,
        provisionar_decimo=provisionar_decimo,
        provisionar_fgts=provisionar_fgts,
        num_dependentes=dependentes_pj,
    )

    diferenca_mensal = round(pj["liquido"] - clt["poder_compra"], 2)
    diferenca_anual = round(pj["liquido_anual"] - clt["liquido_anual"], 2)

    st.divider()
    st.subheader("Resumo principal")

    a, b, c = st.columns(3)
    with a:
        st.metric("CLT - Poder de compra", brl(clt["poder_compra"]))
        st.metric("CLT - Líquido anual", brl(clt["liquido_anual"]))
    with b:
        st.metric("PJ - Líquido mensal", brl(pj["liquido"]))
        st.metric("PJ - Líquido anual", brl(pj["liquido_anual"]))
    with c:
        st.metric("Diferença mensal", brl(diferenca_mensal))
        st.metric("Diferença anual", brl(diferenca_anual))

    st.divider()
    st.subheader("Simples Nacional / Fator R")

    x, y, z = st.columns(3)

    with x:
        st.metric("Anexo usado", pj["anexo"])
        st.metric("Imposto mensal do Simples", brl(pj["imposto_mensal"]))

    with y:
        st.metric("Alíquota nominal", pct(pj["aliquota_nominal"]))
        st.metric("Alíquota efetiva", pct(pj["aliquota_efetiva"]))

    with z:
        if empresa_tecnologia:
            st.metric("Fator R", pct(pj["fator_r"]))
            st.metric("Folha 12 meses", brl(pj["folha12"]))
        else:
            st.metric("RBT12", brl(pj["rbt12"]))
            st.metric("Parcela a deduzir", brl(pj["parcela_deduzir"]))

    if empresa_tecnologia:
        if pj["atingiu_fator_r"]:
            st.success("A empresa atingiu 28% ou mais no Fator R. O app aplicou o Anexo III.")
        else:
            st.warning("A empresa ficou abaixo de 28% no Fator R. O app aplicou o Anexo V.")

    st.divider()
    st.subheader("Detalhamento CLT x PJ")

    d1, d2 = st.columns(2)

    with d1:
        st.markdown("### CLT")
        st.write(f"INSS: {brl(clt['inss'])}")
        st.write(f"IRRF: {brl(clt['irrf'])}")
        st.write(f"Descontos totais: {brl(clt['total_desc'])}")
        st.write(f"Líquido mensal: {brl(clt['liquido'])}")
        st.write(f"Poder de compra: {brl(clt['poder_compra'])}")

    with d2:
        st.markdown("### PJ")
        st.write(f"Receita mensal: {brl(pj['receita_mensal'])}")
        st.write(f"Pró-labore: {brl(pj['prolabore_mensal'])}")
        st.write(f"Distribuição de lucros: {brl(pj['distribuicao_lucros_mensal'])}")
        st.write(f"INSS sobre pró-labore: {brl(pj['inss_pj'])}")
        st.write(f"IRRF sobre pró-labore: {brl(pj['irrf_pj'])}")
        st.write(f"Gastos operacionais: {brl(pj['total_gastos'])}")
        st.write(f"Reservas mensais: {brl(pj['total_res'])}")
        st.write(f"Líquido final mensal: {brl(pj['liquido'])}")

    st.info(
        "A simulação considera distribuição de lucros como saída separada do pró-labore. "
        "Para uso real, confirme enquadramento, CNAE, pró-labore e escrituração com contador."
    )
else:
    st.info("Preencha os campos e clique em 'Calcular comparação'.")
