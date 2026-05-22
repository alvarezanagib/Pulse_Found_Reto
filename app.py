# ============================================================
# 💓 PULSE FUND — Concurso Analítica Financiera ITM 2026
# Estrategia: Momentum mensual + filtro de volatilidad
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

# ── Configuración ────────────────────────────────────────────
st.set_page_config(
    page_title="💓 Pulse Fund",
    page_icon="💓",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────────
st.title("💓 Pulse Fund")
st.caption("Invertimos cuando el mercado tiene pulso fuerte. Cuando hay tormenta, esperamos.")
st.divider()

# ============================================================
# SIDEBAR — Controles interactivos
# ============================================================
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
st.sidebar.subheader("🎯 Parámetros Pulse Fund")

ventana_momentum = st.sidebar.slider(
    "Ventana momentum (días):",
    min_value=30, max_value=90, value=60
)
umbral_volatilidad = st.sidebar.slider(
    "Umbral volatilidad (% diario):",
    min_value=1.0, max_value=10.0, value=6.0, step=0.5
)
ventana_volatilidad = 21
costo_transaccion   = 0.001

# ============================================================
# CARGA DE DATOS
# ============================================================
@st.cache_data(ttl=3600)
def cargar_datos(tickers, inicio, fin):
    try:
        # Descargar cada ticker por separado y unir
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
                frames[ticker.replace("-USD", "")] = df["Close"].squeeze()

        if not frames:
            return pd.DataFrame()

        precios = pd.DataFrame(frames)
        return precios.dropna()

    except Exception as e:
        st.error(f"Error descargando datos: {e}")
        return pd.DataFrame()

# ============================================================
# CÁLCULOS BASE
# ============================================================
retornos    = precios.pct_change().dropna()
volatilidad = retornos.std() * np.sqrt(252)
umbral_dec  = umbral_volatilidad / 100

# Rendimiento acumulado
factor_acum = (1 + retornos).cumprod()
portafolio  = factor_acum * monto_inicial

# Maximum Drawdown por cripto
def calcular_drawdown(serie):
    pico = serie.expanding().max()
    return (serie - pico) / pico

# ============================================================
# CÁLCULOS ESTRATEGIA PULSE FUND
# ============================================================
momentum        = precios.pct_change(ventana_momentum)
volatilidad_rod = retornos.rolling(ventana_volatilidad).std()

# Señales mensuales
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

    criptos_pos = fila_mom[fila_mom > 0]
    if criptos_pos.empty:
        señales_mensuales[fecha_real] = "EFECTIVO"
        continue

    mejor = criptos_pos.idxmax()
    if mejor in fila_vol.index and pd.notna(fila_vol[mejor]):
        if fila_vol[mejor] < umbral_dec:
            señales_mensuales[fecha_real] = mejor.replace("-USD", "")
        else:
            señales_mensuales[fecha_real] = "EFECTIVO"
    else:
        señales_mensuales[fecha_real] = "EFECTIVO"

# Expandir señales a días
señal_diaria = pd.Series(index=precios.index, dtype=str)
fechas_ord   = sorted(señales_mensuales.keys())

for i, f_ini in enumerate(fechas_ord):
    f_fin = fechas_ord[i + 1] if i + 1 < len(fechas_ord) else None
    if f_fin:
        mask = (precios.index >= f_ini) & (precios.index < f_fin)
    else:
        mask = precios.index >= f_ini
    señal_diaria[mask] = señales_mensuales[f_ini]

señal_diaria = señal_diaria.fillna("EFECTIVO")

# Retornos con costos
retornos_pulse    = pd.Series(index=retornos.index, dtype=float)
posicion_anterior = "EFECTIVO"

for fecha in retornos.index:
    señal = señal_diaria[fecha]
    costo = costo_transaccion if señal != posicion_anterior else 0.0
    posicion_anterior = señal
    retornos_pulse[fecha] = (0.0 if señal == "EFECTIVO"
                             else retornos.loc[fecha, señal]) - costo

# Portafolios acumulados
acum_pulse = (1 + retornos_pulse).cumprod()
acum_btc   = (1 + retornos["BTC"]).cumprod() if "BTC" in retornos.columns else None
acum_eth   = (1 + retornos["ETH"]).cumprod() if "ETH" in retornos.columns else None

# Métricas Pulse Fund
retorno_total_pulse = (1 + retornos_pulse).prod() - 1
vol_pulse           = retornos_pulse.std() * np.sqrt(252)
dd_pulse_serie      = calcular_drawdown(acum_pulse)
max_dd_pulse        = dd_pulse_serie.min()
sharpe_pulse        = (retornos_pulse.mean() * 252) / (retornos_pulse.std() * np.sqrt(252))
pct_efectivo        = (señal_diaria == "EFECTIVO").mean()

colores = {
    "BTC": "#F7931A",
    "ETH": "#627EEA",
    "SOL": "#9945FF",
    "💓 Pulse Fund": "#00FF88"
}

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Análisis Base",
    "🎯 Estrategia Pulse Fund",
    "📉 Elemento Cripto",
    "👤 Recomendación al Inversor"
])

# ── TAB 1 — ANÁLISIS BASE ────────────────────────────────────
with tab1:
    st.header("📊 Análisis Base")

    # Métricas rápidas
    cols = st.columns(len(precios.columns))
    for i, cripto in enumerate(precios.columns):
        precio_actual  = precios[cripto].iloc[-1]
        retorno_period = precios[cripto].iloc[-1] / precios[cripto].iloc[0] - 1
        cols[i].metric(
            label=cripto,
            value=f"${precio_actual:,.0f}",
            delta=f"{retorno_period:+.1%} en el período"
        )

    st.divider()

    # Precios históricos
    fig1 = px.line(
        precios, x=precios.index, y=precios.columns.tolist(),
        title="Evolución de precios",
        labels={"value": "Precio (USD)", "variable": "Cripto"},
        color_discrete_map=colores
    )
    fig1.update_layout(hovermode="x unified", height=400)
    st.plotly_chart(fig1, use_container_width=True)

    # Precio rebase 100
    precios_reb = (precios / precios.iloc[0]) * 100
    fig2 = px.line(
        precios_reb, x=precios_reb.index, y=precios_reb.columns.tolist(),
        title="Rendimiento comparado (base 100)",
        labels={"value": "Rendimiento", "variable": "Cripto"},
        color_discrete_map=colores
    )
    fig2.add_hline(y=100, line_dash="dash", line_color="gray")
    fig2.update_layout(hovermode="x unified", height=400)
    st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Volatilidad
        vol_df = volatilidad.reset_index()
        vol_df.columns = ["Cripto", "Volatilidad"]
        fig3 = px.bar(
            vol_df, x="Cripto", y="Volatilidad",
            title="⚡ Volatilidad anualizada",
            color="Cripto", color_discrete_map=colores,
            text_auto=".1%"
        )
        fig3.update_layout(yaxis_tickformat=".0%", showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        # % días negativos
        pct_neg = (retornos < 0).mean()
        neg_df  = pct_neg.reset_index()
        neg_df.columns = ["Cripto", "Pct_Neg"]
        fig4 = px.bar(
            neg_df, x="Cripto", y="Pct_Neg",
            title="📊 % días con retorno negativo",
            color="Cripto", color_discrete_map=colores,
            text_auto=".1%"
        )
        fig4.update_layout(yaxis_tickformat=".0%", showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # Rendimiento acumulado
    fig5 = px.line(
        portafolio, x=portafolio.index, y=portafolio.columns.tolist(),
        title=f"💰 Valor de ${monto_inicial:,} invertidos",
        labels={"value": "Valor (USD)", "variable": "Cripto"},
        color_discrete_map=colores
    )
    fig5.add_hline(y=monto_inicial, line_dash="dash", line_color="gray")
    fig5.update_layout(hovermode="x unified", height=400)
    st.plotly_chart(fig5, use_container_width=True)

    # Maximum Drawdown
    fig6 = go.Figure()
    for cripto in precios.columns:
        dd = calcular_drawdown(precios[cripto])
        fig6.add_trace(go.Scatter(
            x=dd.index, y=dd, name=cripto,
            line=dict(color=colores.get(cripto, "#888")),
            fill="tozeroy",
            fillcolor=f"rgba(128,128,128,0.1)"
        ))
    fig6.update_layout(
        title="📉 Maximum Drawdown histórico",
        yaxis_tickformat=".0%",
        hovermode="x unified", height=400
    )
    st.plotly_chart(fig6, use_container_width=True)

    # Tabla resumen
    st.subheader("📋 Resumen de métricas")
    retorno_tot = (precios.iloc[-1] / precios.iloc[0] - 1)
    resumen = pd.DataFrame({
        "Retorno total":     retorno_tot.map("{:+.1%}".format),
        "Volatilidad anual": volatilidad.map("{:.1%}".format),
        "Max Drawdown":      {c: f"{calcular_drawdown(precios[c]).min():.1%}"
                              for c in precios.columns},
        "% Días negativos":  (retornos < 0).mean().map("{:.1%}".format)
    })
    st.dataframe(resumen, use_container_width=True)

# ── TAB 2 — ESTRATEGIA ───────────────────────────────────────
with tab2:
    st.header("🎯 Estrategia Pulse Fund")

    # Métricas principales
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Retorno Pulse Fund", f"{retorno_total_pulse:+.1%}")
    c2.metric("Max Drawdown",       f"{max_dd_pulse:.1%}")
    c3.metric("Sharpe Ratio",       f"{sharpe_pulse:.2f}")
    c4.metric("Tiempo en efectivo", f"{pct_efectivo:.1%}")

    st.divider()

    # Backtesting
    bt_df = pd.DataFrame({
        "💓 Pulse Fund":     acum_pulse * monto_inicial,
    })
    if acum_btc is not None:
        bt_df["🟠 Buy & Hold BTC"] = acum_btc * monto_inicial
    if acum_eth is not None:
        bt_df["🔵 Buy & Hold ETH"] = acum_eth * monto_inicial

    bt_df = bt_df.dropna()
    fig7  = px.line(
        bt_df, x=bt_df.index, y=bt_df.columns.tolist(),
        title=f"🎯 Backtesting — ${monto_inicial:,} iniciales",
        labels={"value": "Valor (USD)", "variable": "Estrategia"},
        color_discrete_map={
            "💓 Pulse Fund":     "#00FF88",
            "🟠 Buy & Hold BTC": "#F7931A",
            "🔵 Buy & Hold ETH": "#627EEA"
        }
    )
    fig7.add_hline(y=monto_inicial, line_dash="dash", line_color="gray")
    fig7.update_layout(hovermode="x unified", height=450)
    st.plotly_chart(fig7, use_container_width=True)

    # Tabla comparativa
    def metricas_serie(serie, nombre):
        ret   = (1 + serie).prod() - 1
        vol   = serie.std() * np.sqrt(252)
        acum  = (1 + serie).cumprod()
        dd    = ((acum - acum.expanding().max()) / acum.expanding().max()).min()
        sh    = (serie.mean() * 252) / (serie.std() * np.sqrt(252))
        return {"Estrategia": nombre,
                "Retorno total": f"{ret:+.1%}",
                "Volatilidad":   f"{vol:.1%}",
                "Max Drawdown":  f"{dd:.1%}",
                "Sharpe Ratio":  f"{sh:.2f}"}

    rows = [metricas_serie(retornos_pulse, "💓 Pulse Fund")]
    if "BTC" in retornos.columns:
        rows.append(metricas_serie(retornos["BTC"], "🟠 Buy & Hold BTC"))
    if "ETH" in retornos.columns:
        rows.append(metricas_serie(retornos["ETH"], "🔵 Buy & Hold ETH"))

    st.dataframe(
        pd.DataFrame(rows).set_index("Estrategia"),
        use_container_width=True
    )

    # Distribución de señales
    conteo = señal_diaria.value_counts()
    fig8   = px.bar(
        x=conteo.index, y=conteo.values,
        title="📊 Días en cada posición",
        labels={"x": "Posición", "y": "Días"},
        color=conteo.index,
        color_discrete_map={
            "BTC": "#F7931A", "ETH": "#627EEA",
            "SOL": "#9945FF", "EFECTIVO": "#444444"
        },
        text_auto=True
    )
    fig8.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig8, use_container_width=True)

# ── TAB 3 — ELEMENTO CRIPTO ──────────────────────────────────
with tab3:
    st.header("📉 Caídas Extremas y Recuperación Post-Crash")
    st.caption("Análisis específico del ecosistema cripto — mercado 24/7 con crashes frecuentes")

    UMBRAL_CRASH = 0.20
    crashes_list = []

    for cripto in precios.columns:
        p      = precios[cripto]
        pico_h = p.expanding().max()
        dd_s   = (p - pico_h) / pico_h
        en_crash   = dd_s <= -UMBRAL_CRASH
        ini_crash  = en_crash & ~en_crash.shift(1).fillna(False)

        for f_ini in p.index[ini_crash]:
            precio_pico  = pico_h[f_ini]
            post         = p[f_ini:]
            f_valle      = post.idxmin()
            caida        = (post.min() - precio_pico) / precio_pico
            recuperacion = p[f_valle:]
            rec          = recuperacion[recuperacion >= precio_pico]
            dias_rec     = (rec.index[0] - f_valle).days if len(rec) > 0 else None
            crashes_list.append({
                "Cripto":       cripto,
                "Inicio crash": f_ini.date(),
                "Valle":        f_valle.date(),
                "Caída máxima": f"{caida:.1%}",
                "Días recuperación": f"{dias_rec} días" if dias_rec else "Aún no recuperado"
            })

    crashes_df = pd.DataFrame(crashes_list)
    if not crashes_df.empty:
        st.dataframe(crashes_df, use_container_width=True)

    # Drawdown con umbral
    fig9 = go.Figure()
    fill_colors = {
        "BTC": "rgba(247,147,26,0.15)",
        "ETH": "rgba(98,126,234,0.15)",
        "SOL": "rgba(153,69,255,0.15)"
    }
    for cripto in precios.columns:
        dd = calcular_drawdown(precios[cripto])
        fig9.add_trace(go.Scatter(
            x=dd.index, y=dd, name=cripto,
            line=dict(color=colores.get(cripto, "#888"), width=2),
            fill="tozeroy",
            fillcolor=fill_colors.get(cripto, "rgba(128,128,128,0.1)")
        ))
    fig9.add_hline(
        y=-UMBRAL_CRASH, line_dash="dash", line_color="red",
        annotation_text="Umbral crash -20%"
    )
    fig9.update_layout(
        title="Drawdown histórico y zonas de crash",
        yaxis_tickformat=".0%",
        hovermode="x unified", height=430
    )
    st.plotly_chart(fig9, use_container_width=True)

    # Correlación
    st.subheader("🔗 Correlación entre criptomonedas")
    corr = retornos.corr()
    fig10 = px.imshow(
        corr, title="Correlación de retornos diarios",
        color_continuous_scale="RdYlGn",
        zmin=-1, zmax=1, text_auto=".2f"
    )
    fig10.update_layout(height=380)
    st.plotly_chart(fig10, use_container_width=True)

    st.info("💡 Alta correlación entre criptos justifica la rotación de Pulse Fund — "
            "si todas se mueven igual, elegir la más fuerte en cada momento es la estrategia óptima.")

# ── TAB 4 — RECOMENDACIÓN ────────────────────────────────────
with tab4:
    st.header("👤 Recomendación al Inversor")

    perfil = st.radio(
        "Selecciona tu perfil:",
        ["🛡️ Conservador", "⚖️ Moderado", "🚀 Agresivo"],
        horizontal=True
    )

    st.divider()

    if "Conservador" in perfil:
        st.subheader("🛡️ Perfil Conservador — Protección del capital")
        col1, col2 = st.columns(2)
        col1.metric("Max Drawdown Pulse Fund", f"{max_dd_pulse:.1%}")
        if acum_btc is not None:
            dd_btc_val = calcular_drawdown(acum_btc).min()
            col2.metric("Max Drawdown BTC",        f"{dd_btc_val:.1%}",
                        delta=f"{max_dd_pulse - dd_btc_val:+.1%} vs BTC",
                        delta_color="inverse")
        st.info(f"💡 En el peor momento, Pulse Fund perdió **{abs(max_dd_pulse):.1%}** "
                f"vs **{abs(dd_btc_val):.1%}** del Buy & Hold BTC. "
                f"El filtro de volatilidad protegió el capital.")

        fig_c = go.Figure()
        fig_c.add_trace(go.Scatter(
            x=dd_pulse_serie.index, y=dd_pulse_serie,
            name="💓 Pulse Fund", line=dict(color="#00FF88", width=2),
            fill="tozeroy", fillcolor="rgba(0,255,136,0.1)"
        ))
        if acum_btc is not None:
            dd_btc_s = calcular_drawdown(acum_btc)
            fig_c.add_trace(go.Scatter(
                x=dd_btc_s.index, y=dd_btc_s,
                name="🟠 BTC", line=dict(color="#F7931A", width=2),
                fill="tozeroy", fillcolor="rgba(247,147,26,0.1)"
            ))
        fig_c.update_layout(
            title="Comparación de pérdidas máximas",
            yaxis_tickformat=".0%", hovermode="x unified", height=400
        )
        st.plotly_chart(fig_c, use_container_width=True)

    elif "Moderado" in perfil:
        st.subheader("⚖️ Perfil Moderado — Balance riesgo-retorno")
        col1, col2, col3 = st.columns(3)
        col1.metric("Retorno Pulse Fund",  f"{retorno_total_pulse:+.1%}")
        col2.metric("Sharpe Ratio",        f"{sharpe_pulse:.2f}")
        col3.metric("Volatilidad",         f"{vol_pulse:.1%}")
        st.info(f"💡 Pulse Fund creció **{retorno_total_pulse:+.1%}** desde {fecha_inicio} "
                f"con un Sharpe Ratio de **{sharpe_pulse:.2f}** — "
                f"buena calidad de retorno ajustado por riesgo.")

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
        fig_m.add_hline(y=monto_inicial, line_dash="dot", line_color="gray")
        fig_m.update_layout(
            title=f"Crecimiento de ${monto_inicial:,}",
            yaxis_tickprefix="$", yaxis_tickformat=",.0f",
            hovermode="x unified", height=400
        )
        st.plotly_chart(fig_m, use_container_width=True)

    else:
        st.subheader("🚀 Perfil Agresivo — Máximo momentum")
        col1, col2 = st.columns(2)
        col1.metric("Retorno Pulse Fund", f"{retorno_total_pulse:+.1%}")
        col2.metric("Tiempo invertido",   f"{1-pct_efectivo:.1%}")
        st.info("💡 Pulse Fund rota cada mes hacia la cripto con mayor momentum. "
                "Siempre estás en la más fuerte — no en una sola.")

        conteo_agr = señal_diaria.value_counts()
        fig_a = px.pie(
            values=conteo_agr.values,
            names=conteo_agr.index,
            title="Distribución de tiempo por posición",
            color=conteo_agr.index,
            color_discrete_map={
                "BTC": "#F7931A", "ETH": "#627EEA",
                "SOL": "#9945FF", "EFECTIVO": "#444444"
            }
        )
        fig_a.update_traces(textinfo="label+percent")
        fig_a.update_layout(height=400)
        st.plotly_chart(fig_a, use_container_width=True)

# ============================================================
# DISCLAIMER IA
# ============================================================
st.divider()
st.caption(
    "🤖 **Disclaimer IA:** Claude Sonnet (Anthropic) — asistencia en estructura del código, "
    "lógica de backtesting y visualizaciones | "
    "El equipo Pulse Fund definió la estrategia de inversión, validó todos los cálculos "
    "y tomó las decisiones analíticas."
)
