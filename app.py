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
import base64

# ── DARK CRYPTO THEME CONFIG ─────────────────────────────────
st.set_page_config(
    page_title="Pulse Fund",
    page_icon="💓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL CSS — Dark Crypto Aesthetic ───────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

/* ── ROOT PALETTE (extraída del logo Pulse Fund) ── */
:root {
    --bg-deep:      #05040D;
    --bg-card:      #0D0B1A;
    --bg-surface:   #120F22;
    --border:       rgba(255,45,120,0.18);
    --border-glow:  rgba(255,45,120,0.45);
    --pink:         #FF2D78;
    --violet:       #7B2FBE;
    --indigo:       #4A3FD4;
    --blue-elec:    #4A6CF7;
    --silver:       #C8C8E8;
    --text-primary: #F0EEF8;
    --text-muted:   #7A7890;
    --green-neon:   #00FF88;
    --pulse-grad:   linear-gradient(135deg, #FF2D78 0%, #7B2FBE 50%, #4A3FD4 100%);
}

/* ── GLOBAL BACKGROUND ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
}

[data-testid="stMain"] {
    background-color: var(--bg-deep) !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] .stSlider > div > div > div {
    background: var(--pink) !important;
}

/* ── HEADERS ── */
h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: var(--text-primary) !important;
}
h2, h3 { color: var(--silver) !important; font-size: 1.1rem !important; }

/* ── TABS ── */
[data-testid="stTabs"] > div > div {
    border-bottom: 1px solid var(--border) !important;
}
button[data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.05em !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border-radius: 0 !important;
    padding: 0.5rem 1.2rem !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.25s ease !important;
}
button[data-baseweb="tab"]:hover {
    color: var(--pink) !important;
    border-bottom-color: var(--pink) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--pink) !important;
    border-bottom: 2px solid var(--pink) !important;
    background: rgba(255,45,120,0.07) !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--pulse-grad);
}
[data-testid="stMetricLabel"] > div {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── DATAFRAMES ── */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* ── SELECT / MULTISELECT / INPUTS ── */
[data-testid="stMultiSelect"] > div,
[data-testid="stSelectbox"] > div,
[data-testid="stNumberInput"] > div {
    background: var(--bg-surface) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}

/* ── DIVIDER ── */
hr {
    border-color: var(--border) !important;
}

/* ── INFO / WARNING / ERROR boxes ── */
[data-testid="stAlert"] {
    background: rgba(74,63,212,0.12) !important;
    border: 1px solid rgba(74,63,212,0.3) !important;
    border-radius: 10px !important;
    color: var(--silver) !important;
}

/* ── RADIO BUTTONS ── */
[data-testid="stRadio"] label {
    color: var(--text-primary) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] { color: var(--pink) !important; }

/* ── CAPTION / small text ── */
[data-testid="stCaptionContainer"], small, .stCaption {
    color: var(--text-muted) !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── SIDEBAR SUBHEADER ── */
[data-testid="stSidebar"] h2 {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.12em !important;
    color: var(--pink) !important;
}

/* ── PULSE TAGS ── */
.pulse-tag {
    display: inline-block;
    background: rgba(255,45,120,0.1);
    border: 1px solid rgba(255,45,120,0.35);
    color: #FF7AAD;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    padding: 3px 10px;
    border-radius: 20px;
    margin-right: 6px;
    margin-top: 4px;
}

/* ── PLOTLY CHART backgrounds ── */
.js-plotly-plot .plotly .bg {
    fill: transparent !important;
}

/* ── Success badge in sidebar ── */
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(0,255,136,0.08) !important;
    border-color: rgba(0,255,136,0.25) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--violet); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--pink); }
</style>
""", unsafe_allow_html=True)

# ── PLOTLY DARK TEMPLATE ──────────────────────────────────────
PLOTLY_DARK = dict(
    paper_bgcolor="rgba(13,11,26,0.0)",
    plot_bgcolor="rgba(13,11,26,0.0)",
    font=dict(family="Rajdhani, sans-serif", color="#C8C8E8", size=13),
    xaxis=dict(
        gridcolor="rgba(255,45,120,0.08)",
        linecolor="rgba(255,45,120,0.2)",
        tickcolor="rgba(255,45,120,0.3)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,45,120,0.08)",
        linecolor="rgba(255,45,120,0.2)",
        tickcolor="rgba(255,45,120,0.3)",
    ),
    legend=dict(
        bgcolor="rgba(13,11,26,0.7)",
        bordercolor="rgba(255,45,120,0.2)",
        borderwidth=1,
    ),
    title=dict(font=dict(family="Orbitron, monospace", size=14, color="#F0EEF8")),
    colorway=["#FF2D78", "#4A6CF7", "#9945FF", "#00FF88", "#F7931A"],
)

def apply_dark(fig, height=400):
    fig.update_layout(height=height, **PLOTLY_DARK)
    return fig

# ── HEADER ───────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0D0B1A 0%, #120F22 60%);
    border: 1px solid rgba(255,45,120,0.22);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 48px rgba(255,45,120,0.12), 0 0 0 1px rgba(74,63,212,0.15) inset;
    position: relative;
    overflow: hidden;
">
    <!-- neon glow strip top -->
    <div style="
        position:absolute; top:0; left:0; right:0; height:2px;
        background: linear-gradient(90deg, #FF2D78, #7B2FBE, #4A3FD4, #4A6CF7);
    "></div>
    <!-- decorative grid -->
    <div style="
        position:absolute; inset:0; opacity:0.03;
        background-image: linear-gradient(rgba(255,45,120,1) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,45,120,1) 1px, transparent 1px);
        background-size: 40px 40px;
    "></div>

    <div style="display:flex; align-items:center; gap:1rem; margin-bottom:0.5rem; position:relative;">
        <span style="font-size:2.8rem; filter:drop-shadow(0 0 12px #FF2D78);">💓</span>
        <h1 style="
            font-family: 'Orbitron', monospace;
            background: linear-gradient(90deg, #FF2D78 0%, #C060F0 50%, #4A6CF7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.8rem;
            font-weight: 900;
            margin: 0;
            letter-spacing: 2px;
        ">PULSE FUND</h1>
    </div>
    <p style="
        color: #A09CB8;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.05rem;
        margin: 0 0 1rem 0;
        font-weight: 400;
        letter-spacing: 0.03em;
        position:relative;
    ">
        Invertimos cuando el mercado tiene pulso fuerte.
        <span style="color:#FF2D78; font-weight:700;">Cuando hay tormenta, esperamos.</span>
    </p>
    <div style="position:relative;">
        <span class="pulse-tag">⚡ Momentum</span>
        <span class="pulse-tag">🛡 Filtro Volatilidad</span>
        <span class="pulse-tag">🔄 Rebalanceo Mensual</span>
        <span class="pulse-tag">₿ BTC · ETH · SOL</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    def cargar_logo(path):
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None

    logo_b64 = cargar_logo("logo.png")
    if logo_b64:
        st.markdown(f"""
        <div style="text-align:center; padding:1rem 0 0.5rem 0;">
            <img src="data:image/png;base64,{logo_b64}"
                 style="width:150px; border-radius:16px;
                        box-shadow: 0 0 24px rgba(255,45,120,0.35);">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            text-align:center; padding:1.5rem 0 1rem 0;
            font-family:'Orbitron',monospace;
            background: linear-gradient(90deg,#FF2D78,#4A6CF7);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            font-size:1.2rem; font-weight:900; letter-spacing:3px;
        ">💓 PULSE FUND</div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        border-bottom: 1px solid rgba(255,45,120,0.2);
        margin-bottom:1rem;
    "></div>
    """, unsafe_allow_html=True)

# ── SIDEBAR PARAMS ────────────────────────────────────────────
st.sidebar.header("⚙️ Parámetros")

criptos_disponibles = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD"
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
    min_value=100, max_value=1_000_000, value=10_000, step=500
)
st.sidebar.divider()
st.sidebar.subheader("Parámetros Pulse Fund")
ventana_momentum   = st.sidebar.slider("Ventana momentum (días):", 30, 90, 60)
umbral_volatilidad = st.sidebar.slider("Umbral volatilidad (% diario):", 1.0, 10.0, 6.0, 0.5)
ventana_volatilidad = 21
costo_transaccion  = 0.001

# ── VALIDACIÓN ────────────────────────────────────────────────
if len(tickers) == 0:
    st.warning("⚠️ Selecciona al menos una criptomoneda.")
    st.stop()

# ── CARGA DE DATOS ────────────────────────────────────────────
@st.cache_data(ttl=3600)
def cargar_datos(tickers, inicio, fin):
    try:
        frames = {}
        for ticker in tickers:
            df = yf.download(
                ticker, start=inicio, end=fin,
                interval="1d", auto_adjust=True, progress=False
            )
            if not df.empty:
                serie = df["Close"]
                if hasattr(serie, "squeeze"):
                    serie = serie.squeeze()
                frames[ticker.replace("-USD", "")] = serie
        if not frames:
            return pd.DataFrame()
        resultado = pd.DataFrame(frames)
        return resultado.dropna()
    except Exception as e:
        return pd.DataFrame()

with st.spinner("⚡ Descargando datos desde Yahoo Finance..."):
    precios = cargar_datos(tickers, fecha_inicio, fecha_fin)

if precios is None or precios.empty:
    st.error("❌ No se pudieron cargar datos. Verifica la conexión.")
    st.stop()

if isinstance(precios, pd.Series):
    precios = precios.to_frame()

st.sidebar.success(f"✅ {len(precios)} días cargados")

# ── CÁLCULOS BASE ──────────────────────────────────────────────
retornos   = precios.pct_change().dropna()
volatilidad = retornos.std() * np.sqrt(252)
umbral_dec  = umbral_volatilidad / 100
portafolio  = (1 + retornos).cumprod() * monto_inicial

def calcular_drawdown(serie):
    pico = serie.expanding().max()
    return (serie - pico) / pico

colores = {
    "BTC": "#F7931A", "ETH": "#4A6CF7",
    "SOL": "#9945FF", "Pulse Fund": "#00FF88"
}
fill_colors = {
    "BTC": "rgba(247,147,26,0.12)",
    "ETH": "rgba(74,108,247,0.12)",
    "SOL": "rgba(153,69,255,0.12)"
}

# ── ESTRATEGIA PULSE FUND ──────────────────────────────────────
momentum       = precios.pct_change(ventana_momentum)
volatilidad_rod = retornos.rolling(ventana_volatilidad).std()
dias_rebalanceo = precios.resample('MS').first().index

señales_mensuales = {}
for fecha_mes in dias_rebalanceo:
    dias_disp = precios.index[precios.index >= fecha_mes]
    if len(dias_disp) == 0:
        continue
    fecha_real = dias_disp[0]
    try:
        fila_mom = momentum.loc[fecha_real]
        fila_vol = volatilidad_rod.loc[fecha_real]
    except KeyError:
        señales_mensuales[fecha_real] = "EFECTIVO"
        continue
    if isinstance(fila_mom, pd.Series):
        criptos_pos = fila_mom[fila_mom > 0]
    else:
        señales_mensuales[fecha_real] = "EFECTIVO"
        continue
    if criptos_pos.empty:
        señales_mensuales[fecha_real] = "EFECTIVO"
        continue
    mejor    = criptos_pos.idxmax()
    vol_mejor = fila_vol[mejor] if mejor in fila_vol.index else None
    if vol_mejor is not None and pd.notna(vol_mejor) and vol_mejor < umbral_dec:
        señales_mensuales[fecha_real] = str(mejor).replace("-USD", "")
    else:
        señales_mensuales[fecha_real] = "EFECTIVO"

señal_diaria = pd.Series("EFECTIVO", index=precios.index, dtype=str)
fechas_ord = sorted(señales_mensuales.keys())
for i, f_ini in enumerate(fechas_ord):
    f_fin = fechas_ord[i + 1] if i + 1 < len(fechas_ord) else None
    mask = (precios.index >= f_ini) & (precios.index < f_fin) if f_fin else (precios.index >= f_ini)
    señal_diaria[mask] = señales_mensuales[f_ini]

retornos_pulse = pd.Series(0.0, index=retornos.index)
posicion_anterior = "EFECTIVO"
for fecha in retornos.index:
    señal = señal_diaria.get(fecha, "EFECTIVO")
    costo = costo_transaccion if señal != posicion_anterior else 0.0
    posicion_anterior = señal
    if señal == "EFECTIVO" or señal not in retornos.columns:
        retornos_pulse[fecha] = -costo
    else:
        retornos_pulse[fecha] = retornos.loc[fecha, señal] - costo

acum_pulse = (1 + retornos_pulse).cumprod()
acum_btc   = (1 + retornos["BTC"]).cumprod() if "BTC" in retornos.columns else None
acum_eth   = (1 + retornos["ETH"]).cumprod() if "ETH" in retornos.columns else None

retorno_total_pulse = (1 + retornos_pulse).prod() - 1
vol_pulse    = retornos_pulse.std() * np.sqrt(252)
dd_pulse_serie = calcular_drawdown(acum_pulse)
max_dd_pulse   = dd_pulse_serie.min()
sharpe_pulse   = (retornos_pulse.mean() * 252) / (retornos_pulse.std() * np.sqrt(252))
pct_efectivo   = (señal_diaria == "EFECTIVO").mean()

def metricas_serie(serie, nombre):
    ret = (1 + serie).prod() - 1
    vol = serie.std() * np.sqrt(252)
    acum = (1 + serie).cumprod()
    dd  = calcular_drawdown(acum).min()
    sh  = (serie.mean() * 252) / (serie.std() * np.sqrt(252))
    return {"Estrategia": nombre,
            "Retorno total": f"{ret:+.1%}",
            "Volatilidad":   f"{vol:.1%}",
            "Max Drawdown":  f"{dd:.1%}",
            "Sharpe Ratio":  f"{sh:.2f}"}

# ── TABS ───────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Análisis Base",
    "💓 Estrategia Pulse Fund",
    "⚡ Elemento Cripto",
    "🎯 Recomendación al Inversor"
])

# ── TAB 1 ──────────────────────────────────────────────────────
with tab1:
    st.header("Análisis Base")

    cols = st.columns(len(precios.columns))
    for i, cripto in enumerate(precios.columns):
        precio_actual = float(precios[cripto].iloc[-1])
        ret_period    = float(precios[cripto].iloc[-1] / precios[cripto].iloc[0] - 1)
        cols[i].metric(cripto, f"${precio_actual:,.0f}", f"{ret_period:+.1%}")

    st.divider()

    fig1 = px.line(precios, x=precios.index, y=precios.columns.tolist(),
                   title="Evolución de Precios",
                   labels={"value": "Precio (USD)", "variable": "Cripto"},
                   color_discrete_map=colores)
    fig1.update_layout(hovermode="x unified")
    apply_dark(fig1)
    st.plotly_chart(fig1, use_container_width=True)

    precios_reb = (precios / precios.iloc[0]) * 100
    fig2 = px.line(precios_reb, x=precios_reb.index, y=precios_reb.columns.tolist(),
                   title="Rendimiento Comparado (base 100)",
                   labels={"value": "Rendimiento", "variable": "Cripto"},
                   color_discrete_map=colores)
    fig2.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig2.update_layout(hovermode="x unified")
    apply_dark(fig2)
    st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        vol_df = volatilidad.reset_index()
        vol_df.columns = ["Cripto", "Volatilidad"]
        fig3 = px.bar(vol_df, x="Cripto", y="Volatilidad",
                      title="Volatilidad Anualizada",
                      color="Cripto", color_discrete_map=colores, text_auto=".1%")
        fig3.update_layout(yaxis_tickformat=".0%", showlegend=False)
        apply_dark(fig3, height=350)
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        pct_neg = (retornos < 0).mean().reset_index()
        pct_neg.columns = ["Cripto", "Pct_Neg"]
        fig4 = px.bar(pct_neg, x="Cripto", y="Pct_Neg",
                      title="% Días con Retorno Negativo",
                      color="Cripto", color_discrete_map=colores, text_auto=".1%")
        fig4.update_layout(yaxis_tickformat=".0%", showlegend=False)
        apply_dark(fig4, height=350)
        st.plotly_chart(fig4, use_container_width=True)

    fig5 = px.line(portafolio, x=portafolio.index, y=portafolio.columns.tolist(),
                   title=f"Valor de ${monto_inicial:,} Invertidos",
                   labels={"value": "Valor (USD)", "variable": "Cripto"},
                   color_discrete_map=colores)
    fig5.add_hline(y=monto_inicial, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig5.update_layout(hovermode="x unified")
    apply_dark(fig5)
    st.plotly_chart(fig5, use_container_width=True)

    fig6 = go.Figure()
    for cripto in precios.columns:
        dd = calcular_drawdown(precios[cripto])
        fig6.add_trace(go.Scatter(
            x=dd.index, y=dd, name=cripto,
            line=dict(color=colores.get(cripto, "#888")),
            fill="tozeroy",
            fillcolor=fill_colors.get(cripto, "rgba(128,128,128,0.1)")
        ))
    fig6.update_layout(title="Maximum Drawdown",
                       yaxis_tickformat=".0%", hovermode="x unified")
    apply_dark(fig6)
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("📋 Resumen de Métricas")
    resumen = pd.DataFrame({
        "Retorno total":    (precios.iloc[-1]/precios.iloc[0]-1).map("{:+.1%}".format),
        "Volatilidad anual": volatilidad.map("{:.1%}".format),
        "Max Drawdown":     {c: f"{calcular_drawdown(precios[c]).min():.1%}" for c in precios.columns},
        "% Días negativos": (retornos < 0).mean().map("{:.1%}".format)
    })
    st.dataframe(resumen, use_container_width=True)

# ── TAB 2 ──────────────────────────────────────────────────────
with tab2:
    st.header("Estrategia Pulse Fund")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Retorno Pulse Fund",  f"{retorno_total_pulse:+.1%}")
    c2.metric("Max Drawdown",        f"{max_dd_pulse:.1%}")
    c3.metric("Sharpe Ratio",        f"{sharpe_pulse:.2f}")
    c4.metric("Tiempo en efectivo",  f"{pct_efectivo:.1%}")

    st.divider()

    bt_df = pd.DataFrame({"💓 Pulse Fund": acum_pulse * monto_inicial})
    if acum_btc is not None:
        bt_df["🟠 Buy & Hold BTC"] = acum_btc * monto_inicial
    if acum_eth is not None:
        bt_df["🔵 Buy & Hold ETH"] = acum_eth * monto_inicial
    bt_df = bt_df.dropna()

    fig7 = px.line(bt_df, x=bt_df.index, y=bt_df.columns.tolist(),
                   title=f"Backtesting — ${monto_inicial:,} Iniciales",
                   labels={"value": "Valor (USD)", "variable": "Estrategia"},
                   color_discrete_map={
                       "💓 Pulse Fund":    "#00FF88",
                       "🟠 Buy & Hold BTC": "#F7931A",
                       "🔵 Buy & Hold ETH": "#4A6CF7"
                   })
    fig7.add_hline(y=monto_inicial, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    fig7.update_layout(hovermode="x unified")
    apply_dark(fig7, height=450)
    st.plotly_chart(fig7, use_container_width=True)

    rows = [metricas_serie(retornos_pulse, "💓 Pulse Fund")]
    if "BTC" in retornos.columns:
        rows.append(metricas_serie(retornos["BTC"], "🟠 Buy & Hold BTC"))
    if "ETH" in retornos.columns:
        rows.append(metricas_serie(retornos["ETH"], "🔵 Buy & Hold ETH"))
    st.dataframe(pd.DataFrame(rows).set_index("Estrategia"), use_container_width=True)

    conteo = señal_diaria.value_counts()
    fig8 = px.bar(x=conteo.index, y=conteo.values,
                  title="Días en Cada Posición",
                  labels={"x": "Posición", "y": "Días"},
                  color=conteo.index,
                  color_discrete_map={"BTC": "#F7931A", "ETH": "#4A6CF7",
                                      "SOL": "#9945FF", "EFECTIVO": "#2A2840"},
                  text_auto=True)
    fig8.update_layout(showlegend=False)
    apply_dark(fig8, height=350)
    st.plotly_chart(fig8, use_container_width=True)

# ── TAB 3 ──────────────────────────────────────────────────────
with tab3:
    st.header("Caídas Extremas y Recuperación Post-Crash")
    st.caption("Análisis específico del ecosistema cripto — mercado 24/7 con crashes frecuentes")

    UMBRAL_CRASH = 0.20
    crashes_list = []
    for cripto in precios.columns:
        p = precios[cripto]
        pico_h = p.expanding().max()
        dd_s   = (p - pico_h) / pico_h
        en_crash = dd_s <= -UMBRAL_CRASH
        ini_crash = en_crash & ~en_crash.shift(1).fillna(False)
        for f_ini in p.index[ini_crash]:
            precio_pico = float(pico_h[f_ini])
            post   = p[f_ini:]
            f_valle = post.idxmin()
            caida  = float((post.min() - precio_pico) / precio_pico)
            rec    = p[f_valle:]
            rec_ok = rec[rec >= precio_pico]
            dias_rec = (rec_ok.index[0] - f_valle).days if len(rec_ok) > 0 else None
            crashes_list.append({
                "Cripto":          cripto,
                "Inicio crash":    f_ini.date(),
                "Valle":           f_valle.date(),
                "Caída máxima":    f"{caida:.1%}",
                "Días recuperación": f"{dias_rec} días" if dias_rec else "Aún no recuperado"
            })

    if crashes_list:
        st.dataframe(pd.DataFrame(crashes_list), use_container_width=True)

    fig9 = go.Figure()
    for cripto in precios.columns:
        dd = calcular_drawdown(precios[cripto])
        fig9.add_trace(go.Scatter(
            x=dd.index, y=dd, name=cripto,
            line=dict(color=colores.get(cripto, "#888"), width=2),
            fill="tozeroy",
            fillcolor=fill_colors.get(cripto, "rgba(128,128,128,0.1)")
        ))
    fig9.add_hline(y=-UMBRAL_CRASH, line_dash="dash", line_color="#FF2D78",
                   annotation_text="Umbral crash -20%",
                   annotation_font_color="#FF2D78")
    fig9.update_layout(title="Drawdown Histórico y Zonas de Crash",
                       yaxis_tickformat=".0%", hovermode="x unified")
    apply_dark(fig9, height=430)
    st.plotly_chart(fig9, use_container_width=True)

    st.subheader("🔗 Correlación entre Criptomonedas")
    corr = retornos.corr()
    fig10 = px.imshow(corr, title="Correlación de Retornos Diarios",
                      color_continuous_scale=["#4A3FD4", "#120F22", "#FF2D78"],
                      zmin=-1, zmax=1, text_auto=".2f")
    apply_dark(fig10, height=380)
    st.plotly_chart(fig10, use_container_width=True)

    st.info("⚡ Alta correlación justifica la rotación — elegir la más fuerte cada mes "
            "es más eficiente que diversificar entre activos que se mueven igual.")

# ── TAB 4 ──────────────────────────────────────────────────────
with tab4:
    st.header("Recomendación al Inversor")

    perfil = st.radio("Selecciona tu perfil:",
                      ["🛡 Conservador", "⚖️ Moderado", "🚀 Agresivo"],
                      horizontal=True)
    st.divider()

    if "Conservador" in perfil:
        st.subheader("Perfil Conservador — Protección del Capital")
        dd_btc_val = calcular_drawdown(acum_btc).min() if acum_btc is not None else 0
        col1, col2 = st.columns(2)
        col1.metric("Max Drawdown Pulse Fund", f"{max_dd_pulse:.1%}")
        col2.metric("Max Drawdown BTC", f"{dd_btc_val:.1%}",
                    delta=f"{max_dd_pulse - dd_btc_val:+.1%} vs BTC",
                    delta_color="inverse")
        st.info(f"En el peor momento Pulse Fund perdió **{abs(max_dd_pulse):.1%}** "
                f"vs **{abs(dd_btc_val):.1%}** de BTC. El filtro de volatilidad protegió el capital.")
        fig_c = go.Figure()
        fig_c.add_trace(go.Scatter(
            x=dd_pulse_serie.index, y=dd_pulse_serie,
            name="💓 Pulse Fund", line=dict(color="#00FF88", width=2),
            fill="tozeroy", fillcolor="rgba(0,255,136,0.08)"
        ))
        if acum_btc is not None:
            dd_btc_s = calcular_drawdown(acum_btc)
            fig_c.add_trace(go.Scatter(
                x=dd_btc_s.index, y=dd_btc_s,
                name="🟠 BTC", line=dict(color="#F7931A", width=2),
                fill="tozeroy", fillcolor="rgba(247,147,26,0.08)"
            ))
        fig_c.update_layout(title="Comparación de Pérdidas Máximas",
                            yaxis_tickformat=".0%", hovermode="x unified")
        apply_dark(fig_c)
        st.plotly_chart(fig_c, use_container_width=True)

    elif "Moderado" in perfil:
        st.subheader("Perfil Moderado — Balance Riesgo-Retorno")
        col1, col2, col3 = st.columns(3)
        col1.metric("Retorno Pulse Fund", f"{retorno_total_pulse:+.1%}")
        col2.metric("Sharpe Ratio",       f"{sharpe_pulse:.2f}")
        col3.metric("Volatilidad",        f"{vol_pulse:.1%}")
        st.info(f"Pulse Fund creció **{retorno_total_pulse:+.1%}** desde {fecha_inicio} "
                f"con Sharpe Ratio de **{sharpe_pulse:.2f}**.")
        fig_m = go.Figure()
        fig_m.add_trace(go.Scatter(
            x=acum_pulse.index, y=acum_pulse * monto_inicial,
            name="💓 Pulse Fund", line=dict(color="#00FF88", width=3)
        ))
        if acum_btc is not None:
            fig_m.add_trace(go.Scatter(
                x=acum_btc.index, y=acum_btc * monto_inicial,
                name="🟠 BTC", line=dict(color="#F7931A", width=2, dash="dash")
            ))
        fig_m.add_hline(y=monto_inicial, line_dash="dot", line_color="rgba(255,255,255,0.15)")
        fig_m.update_layout(title=f"Crecimiento de ${monto_inicial:,}",
                            yaxis_tickprefix="$", yaxis_tickformat=",.0f",
                            hovermode="x unified")
        apply_dark(fig_m)
        st.plotly_chart(fig_m, use_container_width=True)

    else:
        st.subheader("🚀 Perfil Agresivo — Máximo Momentum")
        col1, col2 = st.columns(2)
        col1.metric("Retorno Pulse Fund", f"{retorno_total_pulse:+.1%}")
        col2.metric("Tiempo invertido",   f"{1-pct_efectivo:.1%}")
        st.info("⚡ Pulse Fund rota cada mes hacia la cripto con mayor momentum. "
                "Siempre en la más fuerte — no atado a una sola.")
        conteo_agr = señal_diaria.value_counts()
        fig_a = px.pie(values=conteo_agr.values, names=conteo_agr.index,
                       title="Distribución de Tiempo por Posición",
                       color=conteo_agr.index,
                       color_discrete_map={"BTC": "#F7931A", "ETH": "#4A6CF7",
                                           "SOL": "#9945FF", "EFECTIVO": "#2A2840"})
        fig_a.update_traces(textinfo="label+percent",
                            textfont=dict(family="Rajdhani, sans-serif", size=13))
        apply_dark(fig_a)
        st.plotly_chart(fig_a, use_container_width=True)

# ── DISCLAIMER ────────────────────────────────────────────────
st.divider()
st.caption(
    "🤖 **Disclaimer IA:** Claude Sonnet (Anthropic) — asistencia en estructura del código, "
    "lógica de backtesting y visualizaciones | "
" Grok simulación montecarlo  | "
    "El equipo Pulse Fund definió la estrategia, validó los cálculos "
    "y tomó todas las decisiones analíticas."
)
