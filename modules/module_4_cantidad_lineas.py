"""
Módulo 4: Análisis de Cantidad de Líneas
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_distribucion_por_segmento(df):
    """4.1 Distribución por segmento"""
    st.markdown("## 4.1 👥 Distribución por Segmento")
    
    # Líneas por segmento
    lineas_por_segmento = df.groupby('SEGMENTO').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    }).round(0)
    lineas_por_segmento['Valor_por_linea'] = (
        lineas_por_segmento['VALOR_FACTURADO_O_COBRADO'] / lineas_por_segmento['CANTIDAD_LINEAS_ACCESOS']
    ).round(0)
    lineas_por_segmento = lineas_por_segmento.sort_values('CANTIDAD_LINEAS_ACCESOS', ascending=False)
    
    total_lineas = df['CANTIDAD_LINEAS_ACCESOS'].sum()
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Líneas", f"{total_lineas:,.0f}")
    
    with col2:
        segmento_top = lineas_por_segmento.index[0]
        st.metric("Segmento Principal", segmento_top[:20])
    
    with col3:
        pct_top = (lineas_por_segmento.iloc[0]['CANTIDAD_LINEAS_ACCESOS'] / total_lineas * 100)
        st.metric("Participación", f"{pct_top:.1f}%")
    
    # Visualizaciones
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 segmentos
        top_10_seg = lineas_por_segmento.head(10)
        fig1 = px.bar(
            x=top_10_seg['CANTIDAD_LINEAS_ACCESOS'],
            y=top_10_seg.index,
            orientation='h',
            title='Top 10 Segmentos por Número de Líneas',
            labels={'x': 'Número de Líneas', 'y': 'Segmento'},
            color=top_10_seg['CANTIDAD_LINEAS_ACCESOS'],
            color_continuous_scale='Blues'
        )
        fig1.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Valor por línea
        top_10_valor = lineas_por_segmento.head(10).sort_values('Valor_por_linea', ascending=True)
        fig2 = px.bar(
            x=top_10_valor['Valor_por_linea'],
            y=top_10_valor.index,
            orientation='h',
            title='Valor por Línea - Top 10 Segmentos',
            labels={'x': 'Valor por Línea (COP)', 'y': 'Segmento'},
            color=top_10_valor['Valor_por_linea'],
            color_continuous_scale='Oranges'
        )
        fig2.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Residencial vs Corporativo
    st.markdown("### 🏢 Residencial vs Corporativo")
    
    tipo_cliente_lineas = df.groupby('TIPO_CLIENTE').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    })
    tipo_cliente_lineas['Valor_por_linea'] = (
        tipo_cliente_lineas['VALOR_FACTURADO_O_COBRADO'] / tipo_cliente_lineas['CANTIDAD_LINEAS_ACCESOS']
    ).round(0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart líneas
        fig3 = px.pie(
            values=tipo_cliente_lineas['CANTIDAD_LINEAS_ACCESOS'],
            names=tipo_cliente_lineas.index,
            title='Distribución de Líneas',
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Comparación 2023 vs 2024
        lineas_tipo_ano = df.groupby(['TIPO_CLIENTE', 'ANNO'])['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
        fig4 = px.bar(
            lineas_tipo_ano,
            x='TIPO_CLIENTE',
            y='CANTIDAD_LINEAS_ACCESOS',
            color='ANNO',
            barmode='group',
            title='Líneas por Tipo de Cliente: 2023 vs 2024',
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    # Métricas detalladas
    st.markdown("### 📊 Métricas por Tipo de Cliente")
    
    for tipo in tipo_cliente_lineas.index:
        with st.expander(f"📌 {tipo}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Líneas", f"{tipo_cliente_lineas.loc[tipo, 'CANTIDAD_LINEAS_ACCESOS']:,.0f}")
            with col2:
                st.metric("Valor Total", f"${tipo_cliente_lineas.loc[tipo, 'VALOR_FACTURADO_O_COBRADO']/1e9:.2f}B")
            with col3:
                st.metric("Valor/Línea", f"${tipo_cliente_lineas.loc[tipo, 'Valor_por_linea']:,.0f}")
    
    # Tabla resumen
    with st.expander("📋 Ver Todos los Segmentos"):
        display_df = lineas_por_segmento.copy()
        display_df['Participación %'] = ((display_df['CANTIDAD_LINEAS_ACCESOS'] / total_lineas) * 100).round(2)
        st.dataframe(display_df, use_container_width=True, height=400)

def show_relacion_lineas_paquete(df):
    """4.2 Relación entre cantidad de líneas y tipo de paquete"""
    st.markdown("## 4.2 📦 Relación Líneas - Paquete")
    
    # Líneas por servicio
    lineas_por_servicio = df.groupby('SERVICIO_PAQUETE').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    }).round(0)
    lineas_por_servicio['Valor_por_linea'] = (
        lineas_por_servicio['VALOR_FACTURADO_O_COBRADO'] / lineas_por_servicio['CANTIDAD_LINEAS_ACCESOS']
    ).round(0)
    lineas_por_servicio = lineas_por_servicio.sort_values('CANTIDAD_LINEAS_ACCESOS', ascending=False)
    
    total_lineas = df['CANTIDAD_LINEAS_ACCESOS'].sum()
    
    # Métricas
    st.markdown("### 📊 Distribución por Servicio/Paquete")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Líneas por servicio
        fig1 = px.bar(
            x=lineas_por_servicio['CANTIDAD_LINEAS_ACCESOS'],
            y=lineas_por_servicio.index,
            orientation='h',
            title='Líneas por Servicio/Paquete',
            labels={'x': 'Número de Líneas', 'y': 'Servicio/Paquete'},
            color=lineas_por_servicio['CANTIDAD_LINEAS_ACCESOS'],
            color_continuous_scale='Greens'
        )
        fig1.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Valor por línea
        fig2 = px.bar(
            x=lineas_por_servicio['Valor_por_linea'],
            y=lineas_por_servicio.index,
            orientation='h',
            title='Valor por Línea por Servicio',
            labels={'x': 'Valor por Línea (COP)', 'y': 'Servicio/Paquete'},
            color=lineas_por_servicio['Valor_por_linea'],
            color_continuous_scale='Reds'
        )
        fig2.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Individual vs Empaquetado
    st.markdown("### 📦 Individual vs Empaquetado")
    
    lineas_tipo_serv = df.groupby('TIPO_SERVICIO').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    })
    lineas_tipo_serv['Valor_por_linea'] = (
        lineas_tipo_serv['VALOR_FACTURADO_O_COBRADO'] / lineas_tipo_serv['CANTIDAD_LINEAS_ACCESOS']
    ).round(0)
    
    col1, col2, col3 = st.columns(3)
    
    for idx, tipo in enumerate(lineas_tipo_serv.index):
        with [col1, col2, col3][idx]:
            st.metric(tipo, f"{lineas_tipo_serv.loc[tipo, 'CANTIDAD_LINEAS_ACCESOS']:,.0f}")
            st.caption(f"Valor/línea: ${lineas_tipo_serv.loc[tipo, 'Valor_por_linea']:,.0f}")
    
    # Scatter plot: Líneas vs Valor
    st.markdown("### 📈 Análisis de Correlación")
    
    scatter_data = df.groupby('SERVICIO_PAQUETE').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    }).reset_index()
    
    fig3 = px.scatter(
        scatter_data,
        x='CANTIDAD_LINEAS_ACCESOS',
        y='VALOR_FACTURADO_O_COBRADO',
        size='CANTIDAD_LINEAS_ACCESOS',
        hover_data=['SERVICIO_PAQUETE'],
        title='Correlación: Líneas vs Valor Facturado',
        labels={
            'CANTIDAD_LINEAS_ACCESOS': 'Número de Líneas',
            'VALOR_FACTURADO_O_COBRADO': 'Valor Facturado'
        },
        color='SERVICIO_PAQUETE'
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Tabla comparativa
    with st.expander("📋 Ver Tabla Comparativa"):
        display_df = lineas_por_servicio.copy()
        display_df['Participación %'] = ((display_df['CANTIDAD_LINEAS_ACCESOS'] / total_lineas) * 100).round(2)
        st.dataframe(display_df, use_container_width=True)

def show_tendencias_años(df):
    """4.3 Tendencias entre años"""
    st.markdown("## 4.3 📈 Tendencias entre Años")
    
    # Líneas por año
    lineas_ano = df.groupby('ANNO').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    }).round(0)
    lineas_ano['Valor_por_linea'] = (
        lineas_ano['VALOR_FACTURADO_O_COBRADO'] / lineas_ano['CANTIDAD_LINEAS_ACCESOS']
    ).round(0)
    
    # Métricas de variación
    if len(lineas_ano) >= 2:
        st.markdown("### 📊 Variación 2023-2024")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            diff_lineas = lineas_ano.loc[2024, 'CANTIDAD_LINEAS_ACCESOS'] - lineas_ano.loc[2023, 'CANTIDAD_LINEAS_ACCESOS']
            diff_pct = (diff_lineas / lineas_ano.loc[2023, 'CANTIDAD_LINEAS_ACCESOS'] * 100)
            st.metric(
                "Variación de Líneas",
                f"{diff_lineas:+,.0f}",
                delta=f"{diff_pct:+.2f}%"
            )
        
        with col2:
            diff_valor = lineas_ano.loc[2024, 'VALOR_FACTURADO_O_COBRADO'] - lineas_ano.loc[2023, 'VALOR_FACTURADO_O_COBRADO']
            diff_valor_pct = (diff_valor / lineas_ano.loc[2023, 'VALOR_FACTURADO_O_COBRADO'] * 100)
            st.metric(
                "Variación de Valor",
                f"${diff_valor/1e9:+.2f}B",
                delta=f"{diff_valor_pct:+.2f}%"
            )
        
        with col3:
            diff_vpl = lineas_ano.loc[2024, 'Valor_por_linea'] - lineas_ano.loc[2023, 'Valor_por_linea']
            diff_vpl_pct = (diff_vpl / lineas_ano.loc[2023, 'Valor_por_linea'] * 100)
            st.metric(
                "Variación Valor/Línea",
                f"${diff_vpl:+,.0f}",
                delta=f"{diff_vpl_pct:+.2f}%"
            )
    
    # Gráficos comparativos
    col1, col2 = st.columns(2)
    
    with col1:
        # Evolución trimestral de líneas
        lineas_trim = df.groupby(['ANNO', 'TRIMESTRE'])['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
        fig1 = px.line(
            lineas_trim,
            x='TRIMESTRE',
            y='CANTIDAD_LINEAS_ACCESOS',
            color='ANNO',
            markers=True,
            title='Evolución Trimestral de Líneas',
            labels={'CANTIDAD_LINEAS_ACCESOS': 'Número de Líneas'},
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig1.update_xaxes(tickvals=[1, 2, 3, 4])
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Evolución del valor por línea
        valor_linea_trim = df.groupby(['ANNO', 'TRIMESTRE']).agg({
            'VALOR_FACTURADO_O_COBRADO': 'sum',
            'CANTIDAD_LINEAS_ACCESOS': 'sum'
        }).reset_index()
        valor_linea_trim['VPL'] = valor_linea_trim['VALOR_FACTURADO_O_COBRADO'] / valor_linea_trim['CANTIDAD_LINEAS_ACCESOS']
        
        fig2 = px.line(
            valor_linea_trim,
            x='TRIMESTRE',
            y='VPL',
            color='ANNO',
            markers=True,
            title='Evolución del Valor por Línea',
            labels={'VPL': 'Valor por Línea (COP)'},
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig2.update_xaxes(tickvals=[1, 2, 3, 4])
        st.plotly_chart(fig2, use_container_width=True)
    
    # Análisis por segmento
    st.markdown("### 👥 Variación por Segmento")
    
    lineas_seg_ano = df.groupby(['ANNO', 'SEGMENTO'])['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
    pivot_seg = lineas_seg_ano.pivot(index='SEGMENTO', columns='ANNO', values='CANTIDAD_LINEAS_ACCESOS').fillna(0)
    
    if 2023 in pivot_seg.columns and 2024 in pivot_seg.columns:
        pivot_seg['Variacion'] = pivot_seg[2024] - pivot_seg[2023]
        pivot_seg['Var_pct'] = ((pivot_seg['Variacion'] / pivot_seg[2023]) * 100).round(2)
        pivot_seg = pivot_seg.sort_values('Variacion', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 con mayor crecimiento
            top_10_crec = pivot_seg.head(10).sort_values('Variacion', ascending=True)
            fig3 = px.bar(
                x=top_10_crec['Variacion'],
                y=top_10_crec.index,
                orientation='h',
                title='Top 10 Segmentos con Mayor Crecimiento',
                labels={'x': 'Variación de Líneas', 'y': 'Segmento'},
                color=top_10_crec['Variacion'],
                color_continuous_scale='Greens'
            )
            fig3.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Comparación 2023 vs 2024
            top_10_seg_names = pivot_seg.head(10).index
            seg_comp = lineas_seg_ano[lineas_seg_ano['SEGMENTO'].isin(top_10_seg_names)]
            
            fig4 = px.bar(
                seg_comp,
                x='CANTIDAD_LINEAS_ACCESOS',
                y='SEGMENTO',
                color='ANNO',
                orientation='h',
                barmode='group',
                title='Top 10 Segmentos: 2023 vs 2024',
                color_discrete_sequence=['#2E86AB', '#A23B72']
            )
            fig4.update_layout(height=500)
            st.plotly_chart(fig4, use_container_width=True)
    
    # Evolución por tipo de servicio
    st.markdown("### 📦 Evolución por Tipo de Servicio")
    
    lineas_tipo_trim = df.groupby(['ANNO', 'TRIMESTRE', 'TIPO_SERVICIO'])['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
    
    fig5 = px.line(
        lineas_tipo_trim,
        x='TRIMESTRE',
        y='CANTIDAD_LINEAS_ACCESOS',
        color='TIPO_SERVICIO',
        line_dash='ANNO',
        markers=True,
        title='Evolución por Tipo de Servicio',
        labels={'CANTIDAD_LINEAS_ACCESOS': 'Número de Líneas'}
    )
    fig5.update_xaxes(tickvals=[1, 2, 3, 4])
    st.plotly_chart(fig5, use_container_width=True)
    
    # Tabla de variaciones
    with st.expander("📋 Ver Variaciones Detalladas por Segmento"):
        if 'Variacion' in pivot_seg.columns:
            display_df = pivot_seg[['2023', '2024', 'Variacion', 'Var_pct']].copy()
            display_df.columns = ['Líneas 2023', 'Líneas 2024', 'Variación', 'Variación %']
            st.dataframe(display_df, use_container_width=True, height=400)