# ============================================================
# 💓 PULSE FUND — Concurso Analítica Financiera ITM 2026
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

# ── CONFIGURACIÓN ────────────────────────────────────────────
st.set_page_config(
    page_title="Pulse Fund",
    page_icon="💓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ESTILO GLOBAL DARK MODE ─────────────────────────────────
st.markdown("""
<style>

/* ===== Fondo principal ===== */
.stApp {
    background-color: #0B0F19;
    color: #EAECEF;
}

/* ===== Sidebar ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0F172A 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* ===== Headers ===== */
h1, h2, h3, h4 {
    color: #F8FAFC !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

/* ===== Textos ===== */
p, label, div {
    color: #D1D5DB;
}

/* ===== Tabs ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #111827;
    color: #CBD5E1;
    border-radius: 14px;
    padding: 12px 20px;
    border: 1px solid rgba(255,255,255,0.06);
    transition: all 0.25s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #00FF88 0%, #00C2FF 100%);
    color: #0B0F19 !important;
    font-weight: 700;
}

/* ===== Métricas ===== */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #111827, #1E293B);
    border: 1px solid rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.25);
}

[data-testid="metric-container"] label {
    color: #94A3B8 !important;
}

/* ===== Inputs ===== */
.stSelectbox div,
.stMultiSelect div,
.stDateInput div,
.stNumberInput div {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 12px;
}

/* ===== Botones ===== */
.stButton button {
    background: linear-gradient(90deg, #00FF88, #00C2FF);
    color: #0B0F19;
    border: none;
    border-radius: 12px;
    font-weight: 700;
}

.stButton button:hover {
    opacity: 0.92;
    transform: scale(1.01);
}

/* ===== DataFrames ===== */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}

/* ===== Containers ===== */
[data-testid="stVerticalBlock"] > div:has(.element-container) {
    border-radius: 18px;
}

/* ===== Divider ===== */
hr {
    border-color: rgba(255,255,255,0.08);
}

/* ===== Scrollbar ===== */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #0F172A;
}

::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #475569;
}

</style>
""", unsafe_allow_html=True)

# ── IDENTIDAD VISUAL ─────────────────────────────────────────
st.title("💓 Pulse Fund")

st.markdown("""
### Sistema cuantitativo de rotación táctica en criptomonedas

Pulse Fund identifica activos con momentum positivo y evita exposición
durante periodos de volatilidad extrema.
""")

st.divider()

# ── TEMA GLOBAL PLOTLY ───────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#0B0F19",
    plot_bgcolor="#111827",
    font=dict(color="#EAECEF"),
    title_font=dict(size=22),
    hoverlabel=dict(
        bgcolor="#111827",
        font_size=13
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)"
    )
)

# ── COLORES ──────────────────────────────────────────────────
colores = {
    "BTC": "#F59E0B",
    "ETH": "#6366F1",
    "SOL": "#8B5CF6",
    "Pulse Fund": "#00FF88"
}

fill_colors = {
    "BTC": "rgba(245,158,11,0.12)",
    "ETH": "rgba(99,102,241,0.12)",
    "SOL": "rgba(139,92,246,0.12)"
}

# ── SIDEBAR ──────────────────────────────────────────────────
st.sidebar.header("⚙️ Parámetros")

criptos_disponibles = {
    "Bitcoin (BTC)":  "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)":   "SOL-USD"
}

criptos_seleccionadas = st.sidebar.multiselect(
    "Criptomonedas:",
    options=list(criptos_disponibles.keys()),
    default=list(criptos_disponibles.keys())
)

tickers = [criptos_disponibles[c] for c in criptos_seleccionadas]

fecha_inicio = st.sidebar.date_input(
    "Fecha inicio:",
    value=date(2023, 1, 1),
    min_value=date(2018, 1, 1),
    max_value=date.today() - timedelta(days=60)
)

fecha_fin = date.today()

monto_inicial = st.sidebar.number_input(
    "Monto hipotético (USD):",
    min_value=100,
    max_value=1_000_000,
    value=10_000,
    step=500
)

st.sidebar.divider()

st.sidebar.subheader("Parámetros Pulse Fund")

ventana_momentum = st.sidebar.slider(
    "Ventana momentum (días):",
    30, 90, 60
)

umbral_volatilidad = st.sidebar.slider(
    "Umbral volatilidad (% diario):",
    1.0, 10.0, 6.0, 0.5
)

ventana_volatilidad = 21
costo_transaccion = 0.001

# ── VALIDACIÓN ───────────────────────────────────────────────
if len(tickers) == 0:
    st.warning("⚠️ Selecciona al menos una criptomoneda.")
    st.stop()

# ── CARGA DE DATOS ───────────────────────────────────────────
@st.cache_data(ttl=3600)
def cargar_datos(tickers, inicio, fin):

    frames = {}

    for ticker in tickers:

        df = yf.download(
            ticker,
            start=inicio,
            end=fin,
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if not df.empty:

            serie = df["Close"]

            if hasattr(serie, "squeeze"):
                serie = serie.squeeze()

            frames[ticker.replace("-USD", "")] = serie

    if not frames:
        return pd.DataFrame()

    return pd.DataFrame(frames).dropna()

with st.spinner("Descargando datos desde Yahoo Finance..."):
    precios = cargar_datos(tickers, fecha_inicio, fecha_fin)

if precios.empty:
    st.error("❌ No se pudieron cargar datos.")
    st.stop()

# ── CÁLCULOS ─────────────────────────────────────────────────
retornos = precios.pct_change().dropna()

volatilidad = retornos.std() * np.sqrt(252)

portafolio = (1 + retornos).cumprod() * monto_inicial

# ── FUNCIÓN DRAWDOWN ─────────────────────────────────────────
def calcular_drawdown(serie):
    pico = serie.expanding().max()
    return (serie - pico) / pico

# ── TABS ─────────────────────────────────────────────────────
tab1, tab2 = st.tabs([
    "📊 Análisis Base",
    "💓 Estrategia Pulse Fund"
])

# ============================================================
# TAB 1
# ============================================================
with tab1:

    st.header("Análisis Base")

    cols = st.columns(len(precios.columns))

    for i, cripto in enumerate(precios.columns):

        precio_actual = float(precios[cripto].iloc[-1])

        ret_period = float(
            precios[cripto].iloc[-1] /
            precios[cripto].iloc[0] - 1
        )

        cols[i].metric(
            cripto,
            f"${precio_actual:,.0f}",
            f"{ret_period:+.1%}"
        )

    st.divider()

    # ── PRECIOS ──────────────────────────────────────────────
    with st.container(border=True):

        fig1 = px.line(
            precios,
            x=precios.index,
            y=precios.columns.tolist(),
            title="Evolución de precios",
            labels={
                "value": "Precio (USD)",
                "variable": "Cripto"
            },
            color_discrete_map=colores
        )

        fig1.update_layout(
            hovermode="x unified",
            height=450,
            **PLOTLY_LAYOUT
        )

        st.plotly_chart(fig1, use_container_width=True)

    # ── BASE 100 ─────────────────────────────────────────────
    with st.container(border=True):

        precios_reb = (precios / precios.iloc[0]) * 100

        fig2 = px.line(
            precios_reb,
            x=precios_reb.index,
            y=precios_reb.columns.tolist(),
            title="Rendimiento comparado (Base 100)",
            labels={
                "value": "Rendimiento",
                "variable": "Cripto"
            },
            color_discrete_map=colores
        )

        fig2.add_hline(
            y=100,
            line_dash="dash",
            line_color="gray"
        )

        fig2.update_layout(
            hovermode="x unified",
            height=450,
            **PLOTLY_LAYOUT
        )

        st.plotly_chart(fig2, use_container_width=True)

    # ── VOLATILIDAD ──────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            vol_df = volatilidad.reset_index()
            vol_df.columns = ["Cripto", "Volatilidad"]

            fig3 = px.bar(
                vol_df,
                x="Cripto",
                y="Volatilidad",
                title="Volatilidad anualizada",
                color="Cripto",
                color_discrete_map=colores,
                text_auto=".1%"
            )

            fig3.update_layout(
                yaxis_tickformat=".0%",
                showlegend=False,
                height=400,
                **PLOTLY_LAYOUT
            )

            st.plotly_chart(fig3, use_container_width=True)

    with col2:

        with st.container(border=True):

            pct_neg = (retornos < 0).mean().reset_index()
            pct_neg.columns = ["Cripto", "Pct_Neg"]

            fig4 = px.bar(
                pct_neg,
                x="Cripto",
                y="Pct_Neg",
                title="Días con retorno negativo",
                color="Cripto",
                color_discrete_map=colores,
                text_auto=".1%"
            )

            fig4.update_layout(
                yaxis_tickformat=".0%",
                showlegend=False,
                height=400,
                **PLOTLY_LAYOUT
            )

            st.plotly_chart(fig4, use_container_width=True)

    # ── PORTAFOLIO ───────────────────────────────────────────
    with st.container(border=True):

        fig5 = px.line(
            portafolio,
            x=portafolio.index,
            y=portafolio.columns.tolist(),
            title=f"Valor de ${monto_inicial:,} invertidos",
            labels={
                "value": "Valor (USD)",
                "variable": "Cripto"
            },
            color_discrete_map=colores
        )

        fig5.add_hline(
            y=monto_inicial,
            line_dash="dash",
            line_color="gray"
        )

        fig5.update_layout(
            hovermode="x unified",
            height=450,
            **PLOTLY_LAYOUT
        )

        st.plotly_chart(fig5, use_container_width=True)

    # ── DRAWDOWN ─────────────────────────────────────────────
    with st.container(border=True):

        fig6 = go.Figure()

        for cripto in precios.columns:

            dd = calcular_drawdown(precios[cripto])

            fig6.add_trace(
                go.Scatter(
                    x=dd.index,
                    y=dd,
                    name=cripto,
                    line=dict(
                        color=colores.get(cripto, "#888")
                    ),
                    fill="tozeroy",
                    fillcolor=fill_colors.get(
                        cripto,
                        "rgba(128,128,128,0.1)"
                    )
                )
            )

        fig6.update_layout(
            title="Maximum Drawdown",
            yaxis_tickformat=".0%",
            hovermode="x unified",
            height=450,
            **PLOTLY_LAYOUT
        )

        st.plotly_chart(fig6, use_container_width=True)

# ============================================================
# TAB 2
# ============================================================
with tab2:

    st.header("💓 Estrategia Pulse Fund")

    st.info(
        "La estrategia rota mensualmente hacia la criptomoneda "
        "con mayor momentum y evita exposición en escenarios "
        "de alta volatilidad."
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Momentum Window",
        f"{ventana_momentum} días"
    )

    c2.metric(
        "Filtro Volatilidad",
        f"{umbral_volatilidad:.1f}%"
    )

    c3.metric(
        "Capital Inicial",
        f"${monto_inicial:,.0f}"
    )

# ── DISCLAIMER ───────────────────────────────────────────────
st.divider()

st.caption("""
🤖 Disclaimer IA:
Claude Sonnet (Anthropic) — asistencia en estructura del código,
lógica de backtesting y visualizaciones.

El equipo Pulse Fund definió la estrategia,
validó los cálculos y tomó todas las decisiones analíticas.
""")
