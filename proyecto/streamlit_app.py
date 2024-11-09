import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Cargar datos
datos_completos = pd.read_excel('proyecto/datos_completos.xlsx')

# Convertir la columna 'Fecha' a formato datetime y establecerla como índice
datos_completos['Fecha'] = pd.to_datetime(datos_completos['Fecha'])
datos_completos.set_index('Fecha', inplace=True)

# Configuración de la página
st.set_page_config(page_title="Dashboard de Producción de Petróleo", layout="wide")

# Título del dashboard
st.title("📊 Dashboard de Producción de Petróleo con Pronósticos ARIMA")

# Filtrar por rango de años
min_year = datos_completos.index.year.min()
max_year = datos_completos.index.year.max()
selected_years = st.sidebar.slider("Selecciona el Rango de Años", min_value=min_year, max_value=max_year, value=(min_year, max_year))
datos_filtrados = datos_completos[(datos_completos.index.year >= selected_years[0]) & (datos_completos.index.year <= selected_years[1])]

# Indicadores clave
st.markdown("### 📌 Indicadores Clave")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Producción Promedio (Petróleo)", f"{datos_filtrados['OilVol'].mean():,.2f}")
col2.metric("Producción Máxima (Petróleo)", f"{datos_filtrados['OilVol'].max():,.2f}")
col3.metric("Producción Mínima (Petróleo)", f"{datos_filtrados['OilVol'].min():,.2f}")
col4.metric("Producción Promedio (Gas)", f"{datos_filtrados['GasVol'].mean():,.2f}")
col5.metric("Producción Promedio (Agua)", f"{datos_filtrados['WaterVol'].mean():,.2f}")
col6.metric("Horas de Operación Promedio", f"{datos_filtrados['WorkHours'].mean():,.2f}")

st.markdown("---")  

# Gráfico de Volumen de Petróleo
st.subheader("🛢️ Volumen de Petróleo Producido")
fig = go.Figure()
fig.add_trace(go.Scatter(x=datos_filtrados.index, y=datos_filtrados['OilVol'], mode='lines', name='OilVol'))
fig.add_trace(go.Scatter(x=datos_filtrados.index, y=datos_filtrados['PronosticosOilVol'], mode='lines', name='Pronóstico ARIMA OilVol', line=dict(dash='dash')))
fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2), margin=dict(t=10))
st.plotly_chart(fig, use_container_width=True)

# Gráfico de Proporción de Agua
st.subheader("💧 Proporción de Agua en el Líquido Extraído")
fig_watercut = go.Figure()
fig_watercut.add_trace(go.Scatter(x=datos_filtrados.index, y=datos_filtrados['WaterCut'], mode='lines', name='WaterCut'))
fig_watercut.add_trace(go.Scatter(x=datos_filtrados.index, y=datos_filtrados['PronosticosWaterCut'], mode='lines', name='Pronóstico ARIMA WaterCut', line=dict(dash='dash')))
fig_watercut.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2), margin=dict(t=10))
st.plotly_chart(fig_watercut, use_container_width=True)

# Gráfico de Volumen de Agua
st.subheader("💧 Volumen de Agua Extraída")
fig_watervol = go.Figure()
fig_watervol.add_trace(go.Scatter(x=datos_filtrados.index, y=datos_filtrados['WaterVol'], mode='lines', name='WaterVol'))
fig_watervol.add_trace(go.Scatter(x=datos_filtrados.index, y=datos_filtrados['PronosticosWaterVol'], mode='lines', name='Pronóstico ARIMA WaterVol', line=dict(dash='dash')))
fig_watervol.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2), margin=dict(t=10))
st.plotly_chart(fig_watervol, use_container_width=True)

# Gráfico de Volumen de Gas
st.subheader("⛽ Volumen de Gas Producido")
fig_gasvol = go.Figure()
fig_gasvol.add_trace(go.Scatter(x=datos_filtrados.index, y=datos_filtrados['GasVol'], mode='lines', name='GasVol'))
fig_gasvol.add_trace(go.Scatter(x=datos_filtrados.index, y=datos_filtrados['PronosticosGasVol'], mode='lines', name='Pronóstico ARIMA GasVol', line=dict(dash='dash')))
fig_gasvol.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2), margin=dict(t=10))
st.plotly_chart(fig_gasvol, use_container_width=True)

st.markdown("---") 

# Comparativo de Producción por Año
st.markdown("### Comparativo de Producción por Año")

# Calcular los promedios anuales de los datos reales
datos_por_anio = datos_completos.resample('YE').mean()

# Crear los datos de pronóstico para los años 2019 y 2020
pronosticos = pd.DataFrame({
    'Fecha': [pd.Timestamp("2019-01-01"), pd.Timestamp("2020-01-01")],
    'OilVol': [datos_completos['PronosticosOilVol'].loc['2019'].mean(), datos_completos['PronosticosOilVol'].loc['2020'].mean()],
    'WaterVol': [datos_completos['PronosticosWaterVol'].loc['2019'].mean(), datos_completos['PronosticosWaterVol'].loc['2020'].mean()],
    'GasVol': [datos_completos['PronosticosGasVol'].loc['2019'].mean(), datos_completos['PronosticosGasVol'].loc['2020'].mean()]
})
pronosticos.set_index('Fecha', inplace=True)

# Concatenar los datos reales con los pronósticos
datos_completos_anual = pd.concat([datos_por_anio, pronosticos])

# Crear el gráfico de barras
fig = go.Figure()

# Agregar los datos reales
for col in ['OilVol', 'WaterVol', 'GasVol']:
    fig.add_trace(go.Bar(
        x=datos_por_anio.index.year,
        y=datos_por_anio[col],
        name=col
    ))

# Agregar los pronósticos para 2019 y 2020
for col in ['OilVol', 'WaterVol', 'GasVol']:
    fig.add_trace(go.Bar(
        x=pronosticos.index.year,
        y=pronosticos[col],
        name=f"Pronóstico {col}",
        marker=dict(pattern_shape="\\")  # Agregar patrón para distinguir
    ))

fig.update_layout(
    barmode='group',
    xaxis_title="Año",
    yaxis_title="Volumen Promedio",
    legend=dict(orientation="h", yanchor="top", y=-0.2),
    margin=dict(t=10)
)

st.plotly_chart(fig, use_container_width=True)

# Sidebar para descripción de variables
st.sidebar.markdown("### Guía de Variables")
st.sidebar.markdown("""
1. **OilVol**: m³/día - Volumen de petróleo producido.
2. **VolLiq**: m³/día - Cantidad total de líquido (mezcla de petróleo, gas y agua) producida por el pozo.
3. **GasVol**: m³/día - Cantidad de gas producido por el pozo.
4. **WaterVol**: m³/día - Cantidad de agua extraída.
5. **WaterCut**: % - Proporción de agua en el líquido extraído.
6. **WorkHours**: Horas de operación al día.
7. **DnmcLvl**: m - Altura del fluido en el pozo durante la operación.
8. **Pressure**: atm - Presión del reservorio medida en atmósferas.
""")
