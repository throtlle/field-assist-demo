
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Field Assist — Portal do Cliente", page_icon="🛠️", layout="wide")

@st.cache_data
def load_data():
    kpis = pd.read_csv("kpis.csv")
    ativos = pd.read_csv("ativos.csv")
    alertas = pd.read_csv("alertas.csv")
    return kpis, ativos, alertas

def render_dashboard(kpis, ativos, alertas):
    logo_zanini = Path("zanini_logo.png")
    logo_cliente = Path("cliente_logo.png")

    left, mid, right = st.columns([1,3,1])
    with left:
        if logo_zanini.exists():
            st.image(str(logo_zanini), use_container_width=True)
    with mid:
        st.title("Portal do Cliente — Field Assist")
        st.caption("KPIs de manutenção, saúde de ativos e alertas — versão demonstrativa")
    with right:
        if logo_cliente.exists():
            st.image(str(logo_cliente), use_container_width=True)

    st.markdown("""
        <style>
            .status-pill { padding:4px 10px; border-radius:999px; font-size:12px; font-weight:600; display:inline-block; }
        </style>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Custo manutenção / 100k t (R$ mil)",
                  f"{kpis['custo_por_100k_t'].iloc[-1]:.1f}",
                  delta=f"{(kpis['custo_por_100k_t'].iloc[-1]-kpis['custo_por_100k_t'].iloc[0]):.1f}")
    with c2:
        st.metric("MTBF (h)",
                  f"{int(kpis['mtbf_h'].iloc[-1])}",
                  delta=f"{int(kpis['mtbf_h'].iloc[-1]-kpis['mtbf_h'].iloc[0])}")
    with c3:
        st.metric("MTTR (h)",
                  f"{kpis['mttr_h'].iloc[-1]:.1f}",
                  delta=f"{kpis['mttr_h'].iloc[-1]-kpis['mttr_h'].iloc[0]:.1f}")
    with c4:
        st.metric("Conformidade óleo (ISO 4406)",
                  f"{int(kpis['iso4406_ok_pct'].iloc[-1])}%",
                  delta=f"{int(kpis['iso4406_ok_pct'].iloc[-1]-kpis['iso4406_ok_pct'].iloc[0])} pp")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("Tendência — Custo / 100k t")
        st.line_chart(kpis.set_index("mes")[["custo_por_100k_t"]])
    with right:
        st.subheader("MTBF x MTTR")
        st.bar_chart(kpis.set_index("mes")[["mtbf_h","mttr_h"]])

    st.divider()
    st.subheader("Saúde dos Ativos (ISM)")

    def render_status(status: str) -> str:
        status = str(status).strip().lower()
        if status == "ok":
            bg, color, txt = "#DEF7EC", "#03543F", "OK"
        elif status.startswith("aten"):
            bg, color, txt = "#FEF3C7", "#92400E", "Atenção"
        else:
            bg, color, txt = "#FDE2E1", "#9B1C1C", "Crítico"
        return f'<span class="status-pill" style="background:{bg};color:{color};">{txt}</span>'

    ativos_html = (
        '<table style="width:100%; font-size:14px">'
        '<thead><tr style="text-align:left;color:#6B7280">'
        '<th>TAG</th><th>Ativo</th><th>Criticidade</th><th>ISM</th><th>Status</th>'
        '</tr></thead><tbody>'
    )
    for _, row in pd.DataFrame(ativos).iterrows():
        ativos_html += "<tr>"
        ativos_html += f"<td>{row['tag']}</td>"
        ativos_html += f"<td>{row['ativo']}</td>"
        ativos_html += f"<td>{row['criticidade']}</td>"
        ativos_html += f"<td>{row['ism']}</td>"
        ativos_html += f"<td>{render_status(row['status'])}</td>"
        ativos_html += "</tr>"
    ativos_html += "</tbody></table>"
    st.markdown(ativos_html, unsafe_allow_html=True)

    st.divider()
    st.subheader("Alertas Recentes")
    for _, row in pd.DataFrame(alertas).iterrows():
        with st.container(border=True):
            cols = st.columns([1,2,2,1,2,1])
            cols[0].write(row['quando'])
            cols[1].write(f"**TAG:** {row['tag']}")
            cols[2].write(f"**Tipo:** {row['tipo']}")
            cols[3].write(f"**Nível:** {row['nivel']}")
            cols[4].write(f"**Ação:** {row['acao']}")
            cols[5].button("Abrir OS", key=f"os_{row['tag']}_{row['quando']}")

    st.caption("© Field Assist — personalize com seu logotipo e cores. Para dados reais, aponte para sua API/CMMS/IoT.")

# --- Splash with clickable logo via query params (?started=1)
if "started" not in st.session_state:
    st.session_state["started"] = st.query_params.get("started", ["0"])[0] == "1"

if not st.session_state["started"]:
    st.markdown(
        '''
        <div style="text-align:center; padding:60px 10px;">
            <h1 style="margin-bottom:6px;">Field Assist</h1>
            <p style="color:#6B7280; font-size:16px; margin-top:0;">
                Clique no logo para entrar no dashboard
            </p>
        </div>
        ''',
        unsafe_allow_html=True
    )

    if Path("zanini_logo.png").exists():
        st.markdown(
            '<div style="text-align:center;">'
            '<a href="?started=1"><img src="zanini_logo.png" width="220"/></a>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.button("🚀 Entrar no Dashboard", type="primary",
                  on_click=lambda: st.query_params.update({"started":"1"}), use_container_width=True)

    st.stop()

kpis, ativos, alertas = load_data()
render_dashboard(kpis, ativos, alertas)
