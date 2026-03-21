# app.py

import streamlit as st
from clt_vs_pj import calcular_clt, calcular_pj, brl

st.set_page_config(
    page_title="Comparador CLT x PJ",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Comparador CLT x PJ")
st.write("Preencha os campos abaixo e veja qual opção faz mais sentido para você.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("CLT")
    salario_clt = st.number_input("Salário bruto mensal (CLT)", min_value=0.0, value=9600.0, step=100.0)
    bonus_clt = st.number_input("Bônus/comissões mensais (CLT)", min_value=0.0, value=0.0, step=100.0)
    vale_refeicao = st.number_input("Vale refeição/alimentação", min_value=0.0, value=770.0, step=50.0)
    ajuda_internet_clt = st.number_input("Ajuda internet (CLT)", min_value=0.0, value=0.0, step=50.0)
    desconto_saude_clt = st.number_input("Desconto plano de saúde (CLT)", min_value=0.0, value=0.0, step=50.0)
    desconto_vt = st.number_input("Desconto VT (CLT)", min_value=0.0, value=0.0, step=50.0)
    dependentes_clt = st.number_input("Dependentes (CLT)", min_value=0, value=0, step=1)

with col2:
    st.subheader("PJ")
    prolabore_pj = st.number_input("Faturamento / pró-labore mensal (PJ)", min_value=0.0, value=16000.0, step=100.0)
    bonus_pj = st.number_input("Bônus/comissões mensais (PJ)", min_value=0.0, value=0.0, step=100.0)
    aliquota_simples = st.number_input("Alíquota Simples Nacional", min_value=0.0, max_value=1.0, value=0.09, step=0.01)
    plano_saude_pj = st.number_input("Plano de saúde (PJ)", min_value=0.0, value=0.0, step=50.0)
    honorarios_contador = st.number_input("Honorários do contador", min_value=0.0, value=350.0, step=50.0)
    aluguel_coworking = st.number_input("Coworking / escritório", min_value=0.0, value=0.0, step=50.0)
    equipamentos = st.number_input("Equipamentos / depreciação", min_value=0.0, value=0.0, step=50.0)
    internet_telefone = st.number_input("Internet / telefone (PJ)", min_value=0.0, value=0.0, step=50.0)
    outros_gastos = st.number_input("Outros gastos (PJ)", min_value=0.0, value=0.0, step=50.0)
    dependentes_pj = st.number_input("Dependentes (PJ)", min_value=0, value=0, step=1)

st.divider()
st.subheader("Reservas do PJ")
col3, col4, col5 = st.columns(3)
with col3:
    provisionar_ferias = st.checkbox("Reservar férias", value=True)
with col4:
    provisionar_decimo = st.checkbox("Reservar 13º", value=True)
with col5:
    provisionar_fgts = st.checkbox("Reservar FGTS", value=True)

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
        prolabore=prolabore_pj,
        bonus_mensal=bonus_pj,
        aliquota_simples=aliquota_simples,
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
    st.subheader("Resultado")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("CLT - Líquido mensal", brl(clt["liquido"]))
        st.metric("CLT - Poder de compra", brl(clt["poder_compra"]))
        st.metric("CLT - Líquido anual", brl(clt["liquido_anual"]))

    with r2:
        st.metric("PJ - Líquido mensal", brl(pj["liquido"]))
        st.metric("PJ - Líquido anual", brl(pj["liquido_anual"]))
        st.metric("PJ - Reservas anuais", brl(pj["reservas_anuais"]))

    with r3:
        st.metric("Diferença mensal real", brl(diferenca_mensal))
        st.metric("Diferença anual", brl(diferenca_anual))
        if diferenca_mensal > 0:
            st.success("Neste cenário, PJ está melhor.")
        elif diferenca_mensal < 0:
            st.warning("Neste cenário, CLT está melhor.")
        else:
            st.info("Empate técnico neste cenário.")

    st.divider()
    st.subheader("Detalhes")

    d1, d2 = st.columns(2)

    with d1:
        st.markdown("### CLT")
        st.write(f"INSS: {brl(clt['inss'])}")
        st.write(f"IRRF: {brl(clt['irrf'])}")
        st.write(f"Descontos totais: {brl(clt['total_desc'])}")
        st.write(f"FGTS mensal: {brl(clt['fgts_emp'])}")
        st.write(f"13º provisionado no pacote: {brl(clt['dec_terceiro'])}")
        st.write(f"Férias provisionadas no pacote: {brl(clt['ferias_1_3'])}")
        st.write(f"Custo/pacote total: {brl(clt['total_pacote'])}")

    with d2:
        st.markdown("### PJ")
        st.write(f"DAS / Simples: {brl(pj['imposto_pj'])}")
        st.write(f"INSS: {brl(pj['inss_pj'])}")
        st.write(f"IRRF: {brl(pj['irrf_pj'])}")
        st.write(f"Gastos operacionais: {brl(pj['total_gastos'])}")
        st.write(f"Reservas mensais: {brl(pj['total_res'])}")
        st.write(f"Custo/pacote total: {brl(pj['total_pacote'])}")
else:
    st.info("Preencha os valores e clique em 'Calcular comparação'.")