
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Field Assist — Portal do Cliente", layout="wide")

@st.cache_data
def load_data():
    kpis = pd.read_csv("kpis.csv")
    ativos = pd.read_csv("ativos.csv")
    alertas = pd.read_csv("alertas.csv")
    return kpis, ativos, alertas

kpis, ativos, alertas = load_data()

st.title("Portal do Cliente — Field Assist")
st.caption("Versão simples para demonstração. Edite os arquivos CSV para atualizar os dados.")

# KPIs cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Custo manutenção / 100k t (R$ mil)", f"{kpis['custo_por_100k_t'].iloc[-1]:.1f}", 
              delta=f"{(kpis['custo_por_100k_t'].iloc[-1]-kpis['custo_por_100k_t'].iloc[0]):.1f}")
with c2:
    st.metric("MTBF (h)", f"{int(kpis['mtbf_h'].iloc[-1])}", 
              delta=f"{int(kpis['mtbf_h'].iloc[-1]-kpis['mtbf_h'].iloc[0])}")
with c3:
    st.metric("MTTR (h)", f"{kpis['mttr_h'].iloc[-1]:.1f}", 
              delta=f"{kpis['mttr_h'].iloc[-1]-kpis['mttr_h'].iloc[0]:.1f}")
with c4:
    st.metric("Conformidade óleo (ISO 4406)", f"{int(kpis['iso4406_ok_pct'].iloc[-1])}%",
              delta=f"{int(kpis['iso4406_ok_pct'].iloc[-1]-kpis['iso4406_ok_pct'].iloc[0])} pp")

st.divider()

# Charts
left, right = st.columns(2)
with left:
    st.subheader("Tendência — Custo / 100k t")
    chart_df = kpis.set_index("mes")[["custo_por_100k_t"]]
    st.line_chart(chart_df)
with right:
    st.subheader("MTBF x MTTR")
    chart_df2 = kpis.set_index("mes")[["mtbf_h","mttr_h"]]
    st.bar_chart(chart_df2)

st.divider()

# Ativos ISM
st.subheader("Saúde dos Ativos (ISM)")
st.dataframe(ativos, use_container_width=True)

st.subheader("Alertas")
for _, row in alertas.iterrows():
    with st.container(border=True):
        cols = st.columns([1,2,2,1,2,1])
        cols[0].write(row['quando'])
        cols[1].write(f"**TAG:** {row['tag']}")
        cols[2].write(f"**Tipo:** {row['tipo']}")
        cols[3].write(f"**Nível:** {row['nivel']}")
        cols[4].write(f"**Ação:** {row['acao']}")
        cols[5].button("Abrir OS", key=f"os_{row['tag']}_{row['quando']}")

st.caption("© Field Assist — demo simples. Para dados reais, apontar para API/CMMS/IoT.")
