"""
Módulo 3: Análisis del Valor Facturado
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def show_distribucion_por_paquete(df):
    """3.1 Distribución del valor facturado por paquete"""
    st.markdown("## 3.1 💰 Distribución por Paquete")
    
    # Valor por servicio
    valor_por_servicio = df.groupby('SERVICIO_PAQUETE').agg({
        'VALOR_FACTURADO_O_COBRADO': ['sum', 'mean', 'median', 'count']
    }).round(0)
    valor_por_servicio.columns = ['Total', 'Media', 'Mediana', 'Registros']
    valor_por_servicio = valor_por_servicio.sort_values('Total', ascending=False)
    
    total_facturado = df['VALOR_FACTURADO_O_COBRADO'].sum()
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Valor Total", f"${total_facturado/1e9:.2f}B")
    
    with col2:
        servicio_top = valor_por_servicio.index[0]
        st.metric("Servicio con Mayor Valor", servicio_top[:20] + "...")
    
    with col3:
        valor_top = valor_por_servicio['Total'].iloc[0]
        pct_top = (valor_top / total_facturado * 100)
        st.metric("Participación", f"{pct_top:.1f}%")
    
    # Visualizaciones
    col1, col2 = st.columns(2)
    
    with col1:
        # Valor total por servicio
        fig1 = px.bar(
            x=valor_por_servicio['Total'],
            y=valor_por_servicio.index,
            orientation='h',
            title='Valor Total Facturado por Servicio/Paquete',
            labels={'x': 'Valor Total (COP)', 'y': 'Servicio/Paquete'},
            color=valor_por_servicio['Total'],
            color_continuous_scale='Blues'
        )
        fig1.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Participación en pie chart
        participacion = (valor_por_servicio['Total'] / total_facturado * 100).sort_values(ascending=False)
        fig2 = px.pie(
            values=participacion.values,
            names=[s[:25] for s in participacion.index],
            title='Participación en Valor Total',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        fig2.update_layout(height=500)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Media vs Mediana
    st.markdown("### 📊 Media vs Mediana por Servicio")
    
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        name='Media',
        y=valor_por_servicio.index,
        x=valor_por_servicio['Media'],
        orientation='h',
        marker_color='#2E86AB'
    ))
    fig3.add_trace(go.Bar(
        name='Mediana',
        y=valor_por_servicio.index,
        x=valor_por_servicio['Mediana'],
        orientation='h',
        marker_color='#A23B72'
    ))
    fig3.update_layout(
        title='Media vs Mediana del Valor Facturado',
        barmode='group',
        height=500
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Tabla detallada
    with st.expander("📋 Ver Estadísticas Detalladas"):
        valor_display = valor_por_servicio.copy()
        valor_display['Participación %'] = ((valor_display['Total'] / total_facturado) * 100).round(2)
        st.dataframe(valor_display, use_container_width=True)

def show_distribucion_por_operador(df):
    """3.2 Distribución del valor facturado por operador"""
    st.markdown("## 3.2 🏢 Distribución por Operador")
    
    # Valor por operador
    valor_por_operador = df.groupby('EMPRESA').agg({
        'VALOR_FACTURADO_O_COBRADO': ['sum', 'mean', 'count']
    }).round(0)
    valor_por_operador.columns = ['Total', 'Media', 'Registros']
    valor_por_operador = valor_por_operador.sort_values('Total', ascending=False)
    
    total_facturado = df['VALOR_FACTURADO_O_COBRADO'].sum()
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Operadores", df['EMPRESA'].nunique())
    
    with col2:
        top_5_valor = valor_por_operador.head(5)['Total'].sum()
        concentracion_top5 = (top_5_valor / total_facturado) * 100
        st.metric("Top 5 Concentración", f"{concentracion_top5:.1f}%")
    
    with col3:
        top_10_valor = valor_por_operador.head(10)['Total'].sum()
        concentracion_top10 = (top_10_valor / total_facturado) * 100
        st.metric("Top 10 Concentración", f"{concentracion_top10:.1f}%")
    
    with col4:
        operador_top = valor_por_operador.index[0]
        valor_top = valor_por_operador['Total'].iloc[0]
        pct_top = (valor_top / total_facturado) * 100
        st.metric("Líder de Mercado", f"{pct_top:.1f}%")
    
    # Visualizaciones
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        # Top 15 operadores
        top_15 = valor_por_operador.head(15)
        fig1 = px.bar(
            x=top_15['Total'],
            y=[op[:35] for op in top_15.index],
            orientation='h',
            title='Top 15 Operadores por Valor Facturado',
            labels={'x': 'Valor Total (COP)', 'y': 'Operador'},
            color=top_15['Total'],
            color_continuous_scale='Viridis'
        )
        fig1.update_layout(showlegend=False, height=600)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Pie chart Top 10 + Otros
        top_10 = valor_por_operador.head(10)
        otros_valor = total_facturado - top_10['Total'].sum()
        
        pie_data = pd.DataFrame({
            'Operador': list(top_10.index[:10]) + ['Otros'],
            'Valor': list(top_10['Total'].values) + [otros_valor]
        })
        
        fig2 = px.pie(
            pie_data,
            values='Valor',
            names=['Op' + str(i+1) if i < 10 else 'Otros' for i in range(11)],
            title='Participación: Top 10 + Otros',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig2.update_traces(textposition='inside', textinfo='percent')
        fig2.update_layout(height=600)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Comparación 2023 vs 2024
    st.markdown("### 📊 Comparación por Año")
    
    top_10_empresas = valor_por_operador.head(10).index
    df_top_10 = df[df['EMPRESA'].isin(top_10_empresas)]
    valor_ops_ano = df_top_10.groupby(['EMPRESA', 'ANNO'])['VALOR_FACTURADO_O_COBRADO'].sum().reset_index()
    
    fig3 = px.bar(
        valor_ops_ano,
        x='VALOR_FACTURADO_O_COBRADO',
        y='EMPRESA',
        color='ANNO',
        orientation='h',
        barmode='group',
        title='Top 10 Operadores: 2023 vs 2024',
        labels={'VALOR_FACTURADO_O_COBRADO': 'Valor Facturado'},
        color_discrete_sequence=['#2E86AB', '#A23B72']
    )
    fig3.update_layout(height=500)
    fig3.update_yaxes(ticktext=[op[:25] for op in top_10_empresas], tickvals=list(top_10_empresas))
    st.plotly_chart(fig3, use_container_width=True)
    
    # Tabla completa
    with st.expander("📋 Ver Ranking Completo"):
        ranking_display = valor_por_operador.copy()
        ranking_display['Participación %'] = ((ranking_display['Total'] / total_facturado) * 100).round(2)
        ranking_display.index.name = 'Operador'
        st.dataframe(ranking_display, use_container_width=True, height=400)

def show_comparacion_regiones(df):
    """3.3 Comparaciones entre regiones"""
    st.markdown("## 3.3 🗺️ Comparación por Regiones")
    
    # Valor por región
    valor_por_region = df.groupby('REGION').agg({
        'VALOR_FACTURADO_O_COBRADO': 'sum',
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'DEPARTAMENTO': 'nunique',
        'MUNICIPIO': 'nunique'
    }).round(0)
    valor_por_region['Valor_por_linea'] = (
        valor_por_region['VALOR_FACTURADO_O_COBRADO'] / valor_por_region['CANTIDAD_LINEAS_ACCESOS']
    ).round(0)
    valor_por_region = valor_por_region.sort_values('VALOR_FACTURADO_O_COBRADO', ascending=False)
    
    # Métricas por región
    st.markdown("### 📊 Métricas por Región")
    
    cols = st.columns(len(valor_por_region))
    for idx, (region, row) in enumerate(valor_por_region.iterrows()):
        with cols[idx]:
            st.metric(
                region,
                f"${row['VALOR_FACTURADO_O_COBRADO']/1e9:.2f}B",
                delta=f"{row['CANTIDAD_LINEAS_ACCESOS']:,.0f} líneas"
            )
    
    # Visualizaciones
    col1, col2 = st.columns(2)
    
    with col1:
        # Valor por región
        fig1 = px.bar(
            x=valor_por_region['VALOR_FACTURADO_O_COBRADO'],
            y=valor_por_region.index,
            orientation='h',
            title='Valor Facturado por Región',
            labels={'x': 'Valor Total (COP)', 'y': 'Región'},
            color=valor_por_region['VALOR_FACTURADO_O_COBRADO'],
            color_continuous_scale='Greens'
        )
        fig1.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Valor por línea
        fig2 = px.bar(
            x=valor_por_region['Valor_por_linea'],
            y=valor_por_region.index,
            orientation='h',
            title='Valor Promedio por Línea por Región',
            labels={'x': 'Valor por Línea (COP)', 'y': 'Región'},
            color=valor_por_region['Valor_por_linea'],
            color_continuous_scale='Oranges'
        )
        fig2.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Departamentos por región
    st.markdown("### 🏛️ Top Departamentos por Región")
    
    region_seleccionada = st.selectbox(
        "Seleccione una región:",
        valor_por_region.index.tolist()
    )
    
    df_region = df[df['REGION'] == region_seleccionada]
    valor_deptos_region = df_region.groupby('DEPARTAMENTO')['VALOR_FACTURADO_O_COBRADO'].sum().sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig3 = px.bar(
            x=valor_deptos_region.values,
            y=valor_deptos_region.index,
            orientation='h',
            title=f'Valor por Departamento - {region_seleccionada}',
            labels={'x': 'Valor Facturado', 'y': 'Departamento'},
            color=valor_deptos_region.values,
            color_continuous_scale='Blues'
        )
        fig3.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Top operadores en la región
        top_ops_region = df_region.groupby('EMPRESA')['VALOR_FACTURADO_O_COBRADO'].sum().sort_values(ascending=False).head(10)
        fig4 = px.bar(
            x=top_ops_region.values,
            y=[op[:25] for op in top_ops_region.index],
            orientation='h',
            title=f'Top 10 Operadores - {region_seleccionada}',
            labels={'x': 'Valor Facturado', 'y': 'Operador'},
            color=top_ops_region.values,
            color_continuous_scale='Reds'
        )
        fig4.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Comparación anual por región
    st.markdown("### 📅 Evolución por Región")
    
    valor_region_ano = df.groupby(['REGION', 'ANNO'])['VALOR_FACTURADO_O_COBRADO'].sum().reset_index()
    
    fig5 = px.bar(
        valor_region_ano,
        x='REGION',
        y='VALOR_FACTURADO_O_COBRADO',
        color='ANNO',
        barmode='group',
        title='Valor Facturado por Región y Año',
        color_discrete_sequence=['#2E86AB', '#A23B72']
    )
    st.plotly_chart(fig5, use_container_width=True)

def show_evolucion_trimestral(df):
    """3.4 Evolución mensual del valor facturado"""
    st.markdown("## 3.4 📈 Evolución Trimestral")
    
    # Calcular valor trimestral
    valor_trimestral = df.groupby(['ANNO', 'TRIMESTRE']).agg({
        'VALOR_FACTURADO_O_COBRADO': 'sum',
        'CANTIDAD_LINEAS_ACCESOS': 'sum'
    }).reset_index()
    valor_trimestral['Valor_por_linea'] = (
        valor_trimestral['VALOR_FACTURADO_O_COBRADO'] / valor_trimestral['CANTIDAD_LINEAS_ACCESOS']
    ).round(0)
    
    # Métricas de crecimiento
    st.markdown("### 📊 Crecimiento Trimestral")
    
    cols = st.columns(4)
    for idx, trim in enumerate([1, 2, 3, 4]):
        with cols[idx]:
            trim_data = valor_trimestral[valor_trimestral['TRIMESTRE'] == trim]
            if len(trim_data) > 0:
                valor_total = trim_data['VALOR_FACTURADO_O_COBRADO'].sum()
                st.metric(f"T{trim}", f"${valor_total/1e9:.2f}B")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        # Evolución del valor
        fig1 = px.line(
            valor_trimestral,
            x='TRIMESTRE',
            y='VALOR_FACTURADO_O_COBRADO',
            color='ANNO',
            markers=True,
            title='Evolución Trimestral del Valor Facturado',
            labels={'VALOR_FACTURADO_O_COBRADO': 'Valor Facturado'},
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig1.update_xaxes(tickvals=[1, 2, 3, 4])
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Evolución del valor por línea
        fig2 = px.line(
            valor_trimestral,
            x='TRIMESTRE',
            y='Valor_por_linea',
            color='ANNO',
            markers=True,
            title='Evolución del Valor por Línea',
            labels={'Valor_por_linea': 'Valor por Línea (COP)'},
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig2.update_xaxes(tickvals=[1, 2, 3, 4])
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Valor por servicio - evolución trimestral
    st.markdown("### 📦 Evolución por Servicio (Top 5)")
    
    top_5_servicios = df.groupby('SERVICIO_PAQUETE')['VALOR_FACTURADO_O_COBRADO'].sum().nlargest(5).index
    df_top_5 = df[df['SERVICIO_PAQUETE'].isin(top_5_servicios)]
    valor_serv_trim = df_top_5.groupby(['ANNO', 'TRIMESTRE', 'SERVICIO_PAQUETE'])['VALOR_FACTURADO_O_COBRADO'].sum().reset_index()
    
    fig3 = px.line(
        valor_serv_trim,
        x='TRIMESTRE',
        y='VALOR_FACTURADO_O_COBRADO',
        color='SERVICIO_PAQUETE',
        line_dash='ANNO',
        markers=True,
        title='Evolución por Servicio (Top 5)',
        labels={'VALOR_FACTURADO_O_COBRADO': 'Valor Facturado'}
    )
    fig3.update_xaxes(tickvals=[1, 2, 3, 4])
    st.plotly_chart(fig3, use_container_width=True)
    
    # Composición trimestral
    st.markdown("### 🥧 Composición Trimestral")
    
    año_analisis = st.radio("Seleccione año:", df['ANNO'].unique().tolist(), horizontal=True)
    
    valor_trim_comp = df[df['ANNO'] == año_analisis].groupby(
        ['TRIMESTRE', 'SERVICIO_PAQUETE']
    )['VALOR_FACTURADO_O_COBRADO'].sum().reset_index()
    
    top_5_servicios_año = df[df['ANNO'] == año_analisis].groupby('SERVICIO_PAQUETE')['VALOR_FACTURADO_O_COBRADO'].sum().nlargest(5).index
    valor_trim_comp_top5 = valor_trim_comp[valor_trim_comp['SERVICIO_PAQUETE'].isin(top_5_servicios_año)]
    
    fig4 = px.bar(
        valor_trim_comp_top5,
        x='TRIMESTRE',
        y='VALOR_FACTURADO_O_COBRADO',
        color='SERVICIO_PAQUETE',
        title=f'Composición Trimestral {año_analisis} (Top 5 Servicios)',
        labels={'VALOR_FACTURADO_O_COBRADO': 'Valor Facturado'},
        barmode='stack'
    )
    fig4.update_xaxes(tickvals=[1, 2, 3, 4])
    st.plotly_chart(fig4, use_container_width=True)
    
    # Tabla de datos
    with st.expander("📋 Ver Datos Trimestrales"):
        st.dataframe(
            valor_trimestral.pivot_table(
                index='TRIMESTRE',
                columns='ANNO',
                values='VALOR_FACTURADO_O_COBRADO',
                aggfunc='sum'
            ),
            use_container_width=True
        )