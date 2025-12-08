"""
Módulo 4: Análisis de Cantidad de Líneas (Mejorado)
Incluye análisis por segmento, tecnología, departamento y tendencias
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    total_valor = df['VALOR_FACTURADO_O_COBRADO'].sum()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Líneas", f"{total_lineas:,.0f}")
    
    with col2:
        st.metric("Valor Total", f"${total_valor/1e12:.2f}B")
    
    with col3:
        segmento_top = lineas_por_segmento.index[0]
        st.metric("Segmento Principal", segmento_top[:15] + "...")
    
    with col4:
        pct_top = (lineas_por_segmento.iloc[0]['CANTIDAD_LINEAS_ACCESOS'] / total_lineas * 100)
        st.metric("Participación Top", f"{pct_top:.1f}%")
    
    # Visualizaciones principales
    st.markdown("### 📊 Visualización General")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 segmentos por líneas
        top_10_seg = lineas_por_segmento.head(10)
        fig1 = px.bar(
            x=top_10_seg['CANTIDAD_LINEAS_ACCESOS'],
            y=top_10_seg.index,
            orientation='h',
            title='Top 10 Segmentos por Número de Líneas',
            labels={'x': 'Número de Líneas', 'y': 'Segmento'},
            color=top_10_seg['CANTIDAD_LINEAS_ACCESOS'],
            color_continuous_scale='Blues',
            text=top_10_seg['CANTIDAD_LINEAS_ACCESOS']
        )
        fig1.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
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
            color_continuous_scale='Oranges',
            text=top_10_valor['Valor_por_linea']
        )
        fig2.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
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
            title='Distribución de Líneas por Tipo de Cliente',
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
            color_discrete_sequence=['#2E86AB', '#A23B72'],
            text='CANTIDAD_LINEAS_ACCESOS'
        )
        fig4.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig4, use_container_width=True)
    
    # Métricas detalladas por tipo de cliente
    st.markdown("### 📊 Métricas Detalladas por Tipo de Cliente")
    
    for tipo in tipo_cliente_lineas.index:
        with st.expander(f"📌 {tipo}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            lineas = tipo_cliente_lineas.loc[tipo, 'CANTIDAD_LINEAS_ACCESOS']
            valor = tipo_cliente_lineas.loc[tipo, 'VALOR_FACTURADO_O_COBRADO']
            vpl = tipo_cliente_lineas.loc[tipo, 'Valor_por_linea']
            pct_lineas = (lineas / total_lineas * 100)
            
            with col1:
                st.metric("Líneas", f"{lineas:,.0f}", delta=f"{pct_lineas:.1f}%")
            with col2:
                st.metric("Valor Total", f"${valor/1e9:.2f}B")
            with col3:
                st.metric("Valor/Línea", f"${vpl:,.0f}")
            with col4:
                pct_valor = (valor / total_valor * 100)
                st.metric("% del Valor", f"{pct_valor:.2f}%")
    
    # Análisis de estratos residenciales
    st.markdown("### 🏘️ Análisis de Estratos Residenciales")
    
    estratos = [seg for seg in lineas_por_segmento.index if 'Residencial' in seg and 'Estrato' in seg]
    if estratos:
        estratos_data = lineas_por_segmento.loc[estratos].copy()
        estratos_data['Estrato'] = estratos_data.index.str.extract(r'Estrato (\d+)')[0]
        estratos_data = estratos_data.sort_values('Estrato')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución por estrato
            fig5 = px.bar(
                estratos_data,
                x='Estrato',
                y='CANTIDAD_LINEAS_ACCESOS',
                title='Líneas por Estrato Socioeconómico',
                color='CANTIDAD_LINEAS_ACCESOS',
                color_continuous_scale='Viridis',
                text='CANTIDAD_LINEAS_ACCESOS'
            )
            fig5.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig5.update_layout(showlegend=False)
            st.plotly_chart(fig5, use_container_width=True)
        
        with col2:
            # Valor por línea por estrato
            fig6 = px.line(
                estratos_data,
                x='Estrato',
                y='Valor_por_linea',
                title='Evolución del Valor por Línea según Estrato',
                markers=True,
                color_discrete_sequence=['#A23B72']
            )
            fig6.update_traces(marker=dict(size=12), line=dict(width=3))
            st.plotly_chart(fig6, use_container_width=True)
    
    # Tabla resumen completa
    with st.expander("📋 Ver Todos los Segmentos (Tabla Detallada)"):
        display_df = lineas_por_segmento.copy()
        display_df['Participación Líneas %'] = ((display_df['CANTIDAD_LINEAS_ACCESOS'] / total_lineas) * 100).round(2)
        display_df['Participación Valor %'] = ((display_df['VALOR_FACTURADO_O_COBRADO'] / total_valor) * 100).round(2)
        display_df.columns = ['Líneas', 'Valor Facturado', 'Valor/Línea', '% Líneas', '% Valor']
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
    total_valor = df['VALOR_FACTURADO_O_COBRADO'].sum()
    
    # Métricas generales
    st.markdown("### 📊 Métricas Generales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        servicio_top = lineas_por_servicio.index[0]
        lineas_top = lineas_por_servicio.iloc[0]['CANTIDAD_LINEAS_ACCESOS']
        st.metric("Servicio con más líneas", servicio_top[:20] + "...", f"{lineas_top:,.0f}")
    
    with col2:
        idx_max_vpl = lineas_por_servicio['Valor_por_linea'].idxmax()
        max_vpl = lineas_por_servicio.loc[idx_max_vpl, 'Valor_por_linea']
        st.metric("Mayor Valor/Línea", idx_max_vpl[:20] + "...", f"${max_vpl:,.0f}")
    
    with col3:
        arpu_promedio = total_valor / total_lineas
        st.metric("ARPU Promedio", f"${arpu_promedio:,.0f}")
    
    # Visualizaciones principales
    st.markdown("### 📈 Distribución por Servicio/Paquete")
    
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
            color_continuous_scale='Greens',
            text=lineas_por_servicio['CANTIDAD_LINEAS_ACCESOS']
        )
        fig1.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
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
            color_continuous_scale='Reds',
            text=lineas_por_servicio['Valor_por_linea']
        )
        fig2.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
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
        with [col1, col2, col3][idx % 3]:
            lineas = lineas_tipo_serv.loc[tipo, 'CANTIDAD_LINEAS_ACCESOS']
            vpl = lineas_tipo_serv.loc[tipo, 'Valor_por_linea']
            pct = (lineas / total_lineas * 100)
            
            st.metric(tipo, f"{lineas:,.0f}", delta=f"{pct:.1f}%")
            st.caption(f"💰 Valor/línea: ${vpl:,.0f}")
    
    # Gráficos comparativos
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart distribución
        fig3 = px.pie(
            values=lineas_tipo_serv['CANTIDAD_LINEAS_ACCESOS'],
            names=lineas_tipo_serv.index,
            title='Distribución: Individual vs Empaquetado',
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label+value')
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Comparación de valor por línea
        fig4 = px.bar(
            lineas_tipo_serv,
            y=lineas_tipo_serv.index,
            x='Valor_por_linea',
            orientation='h',
            title='Comparación de Valor por Línea',
            color='Valor_por_linea',
            color_continuous_scale='Plasma',
            text='Valor_por_linea'
        )
        fig4.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Scatter plot: Líneas vs Valor
    st.markdown("### 📈 Análisis de Correlación: Líneas vs Valor")
    
    scatter_data = df.groupby('SERVICIO_PAQUETE').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    }).reset_index()
    scatter_data['Valor_por_linea'] = (
        scatter_data['VALOR_FACTURADO_O_COBRADO'] / scatter_data['CANTIDAD_LINEAS_ACCESOS']
    )
    
    fig5 = px.scatter(
        scatter_data,
        x='CANTIDAD_LINEAS_ACCESOS',
        y='VALOR_FACTURADO_O_COBRADO',
        size='CANTIDAD_LINEAS_ACCESOS',
        hover_data=['SERVICIO_PAQUETE', 'Valor_por_linea'],
        title='Correlación: Líneas vs Valor Facturado por Servicio',
        labels={
            'CANTIDAD_LINEAS_ACCESOS': 'Número de Líneas',
            'VALOR_FACTURADO_O_COBRADO': 'Valor Facturado (COP)'
        },
        color='Valor_por_linea',
        color_continuous_scale='Turbo'
    )
    fig5.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
    st.plotly_chart(fig5, use_container_width=True)
    
    # Análisis por año
    st.markdown("### 📅 Evolución 2023 vs 2024")
    
    lineas_serv_ano = df.groupby(['SERVICIO_PAQUETE', 'ANNO'])['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
    
    fig6 = px.bar(
        lineas_serv_ano,
        x='CANTIDAD_LINEAS_ACCESOS',
        y='SERVICIO_PAQUETE',
        color='ANNO',
        orientation='h',
        barmode='group',
        title='Líneas por Servicio: Comparación 2023-2024',
        color_discrete_sequence=['#2E86AB', '#A23B72']
    )
    st.plotly_chart(fig6, use_container_width=True)
    
    # Tabla comparativa detallada
    with st.expander("📋 Ver Tabla Comparativa Completa"):
        display_df = lineas_por_servicio.copy()
        display_df['Participación Líneas %'] = ((display_df['CANTIDAD_LINEAS_ACCESOS'] / total_lineas) * 100).round(2)
        display_df['Participación Valor %'] = ((display_df['VALOR_FACTURADO_O_COBRADO'] / total_valor) * 100).round(2)
        display_df.columns = ['Líneas', 'Valor Facturado', 'Valor/Línea', '% Líneas', '% Valor']
        st.dataframe(display_df, use_container_width=True)

def show_analisis_por_tecnologia(df):
    """4.3 Análisis por Tecnología"""
    st.markdown("## 4.3 🔧 Análisis por Tecnología")
    
    # Filtrar registros con tecnología definida
    df_tech = df[df['TECNOLOGIA'] != 'NA'].copy()
    
    # Métricas generales
    total_lineas_tech = df_tech['CANTIDAD_LINEAS_ACCESOS'].sum()
    total_valor_tech = df_tech['VALOR_FACTURADO_O_COBRADO'].sum()
    n_tecnologias = df_tech['TECNOLOGIA'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Líneas con Tecnología", f"{total_lineas_tech:,.0f}")
    
    with col2:
        st.metric("Valor Total", f"${total_valor_tech/1e12:.2f}B")
    
    with col3:
        st.metric("Tecnologías Diferentes", f"{n_tecnologias}")
    
    with col4:
        arpu_tech = total_valor_tech / total_lineas_tech
        st.metric("ARPU Tecnología", f"${arpu_tech:,.0f}")
    
    # Análisis por tecnología
    lineas_por_tech = df_tech.groupby('TECNOLOGIA').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    }).round(0)
    lineas_por_tech['Valor_por_linea'] = (
        lineas_por_tech['VALOR_FACTURADO_O_COBRADO'] / lineas_por_tech['CANTIDAD_LINEAS_ACCESOS']
    ).round(0)
    lineas_por_tech = lineas_por_tech.sort_values('CANTIDAD_LINEAS_ACCESOS', ascending=False)
    
    # Visualizaciones principales
    st.markdown("### 📊 Top Tecnologías por Líneas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 tecnologías
        top_10_tech = lineas_por_tech.head(10)
        fig1 = px.bar(
            x=top_10_tech['CANTIDAD_LINEAS_ACCESOS'],
            y=top_10_tech.index,
            orientation='h',
            title='Top 10 Tecnologías por Número de Líneas',
            labels={'x': 'Número de Líneas', 'y': 'Tecnología'},
            color=top_10_tech['CANTIDAD_LINEAS_ACCESOS'],
            color_continuous_scale='Blues',
            text=top_10_tech['CANTIDAD_LINEAS_ACCESOS']
        )
        fig1.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig1.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Valor por línea por tecnología
        top_10_vpl_tech = lineas_por_tech.head(10).sort_values('Valor_por_linea', ascending=True)
        fig2 = px.bar(
            x=top_10_vpl_tech['Valor_por_linea'],
            y=top_10_vpl_tech.index,
            orientation='h',
            title='Valor por Línea - Top 10 Tecnologías',
            labels={'x': 'Valor por Línea (COP)', 'y': 'Tecnología'},
            color=top_10_vpl_tech['Valor_por_linea'],
            color_continuous_scale='Oranges',
            text=top_10_vpl_tech['Valor_por_linea']
        )
        fig2.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig2.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Distribución porcentual
    st.markdown("### 📈 Distribución de Mercado por Tecnología")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart Top 5
        top_5_tech = lineas_por_tech.head(5)
        otros_tech = lineas_por_tech.iloc[5:]['CANTIDAD_LINEAS_ACCESOS'].sum()
        
        pie_data = pd.DataFrame({
            'Tecnología': list(top_5_tech.index) + ['Otras'],
            'Líneas': list(top_5_tech['CANTIDAD_LINEAS_ACCESOS']) + [otros_tech]
        })
        
        fig3 = px.pie(
            pie_data,
            values='Líneas',
            names='Tecnología',
            title='Participación de Mercado (Top 5 + Otras)',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Treemap de tecnologías
        treemap_data = lineas_por_tech.head(15).reset_index()
        fig4 = px.treemap(
            treemap_data,
            path=['TECNOLOGIA'],
            values='CANTIDAD_LINEAS_ACCESOS',
            title='Jerarquía de Tecnologías (Top 15)',
            color='Valor_por_linea',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    # Evolución por año
    st.markdown("### 📅 Evolución Tecnológica 2023-2024")
    
    tech_ano = df_tech.groupby(['TECNOLOGIA', 'ANNO'])['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
    top_5_tech_names = lineas_por_tech.head(5).index.tolist()
    tech_ano_top5 = tech_ano[tech_ano['TECNOLOGIA'].isin(top_5_tech_names)]
    
    fig5 = px.bar(
        tech_ano_top5,
        x='CANTIDAD_LINEAS_ACCESOS',
        y='TECNOLOGIA',
        color='ANNO',
        orientation='h',
        barmode='group',
        title='Evolución Top 5 Tecnologías: 2023 vs 2024',
        color_discrete_sequence=['#2E86AB', '#A23B72'],
        text='CANTIDAD_LINEAS_ACCESOS'
    )
    fig5.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig5, use_container_width=True)
    
    # Análisis de crecimiento
    st.markdown("### 📊 Análisis de Crecimiento por Tecnología")
    
    pivot_tech = tech_ano.pivot(index='TECNOLOGIA', columns='ANNO', values='CANTIDAD_LINEAS_ACCESOS').fillna(0)
    
    if 2023 in pivot_tech.columns and 2024 in pivot_tech.columns:
        pivot_tech = pivot_tech[(pivot_tech[2023] > 0) & (pivot_tech[2024] > 0)]
        pivot_tech['Variacion'] = pivot_tech[2024] - pivot_tech[2023]
        pivot_tech['Var_pct'] = ((pivot_tech['Variacion'] / pivot_tech[2023]) * 100).round(2)
        pivot_tech = pivot_tech.sort_values('Var_pct', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 con mayor crecimiento
            top_10_crec = pivot_tech.head(10).sort_values('Var_pct', ascending=True)
            fig6 = px.bar(
                x=top_10_crec['Var_pct'],
                y=top_10_crec.index,
                orientation='h',
                title='Top 10 Tecnologías con Mayor Crecimiento (%)',
                labels={'x': 'Variación Porcentual (%)', 'y': 'Tecnología'},
                color=top_10_crec['Var_pct'],
                color_continuous_scale='Greens',
                text=top_10_crec['Var_pct']
            )
            fig6.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig6.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            # Top 10 con mayor decrecimiento
            top_10_decrec = pivot_tech.tail(10).sort_values('Var_pct', ascending=False)
            fig7 = px.bar(
                x=top_10_decrec['Var_pct'],
                y=top_10_decrec.index,
                orientation='h',
                title='Top 10 Tecnologías con Mayor Decrecimiento (%)',
                labels={'x': 'Variación Porcentual (%)', 'y': 'Tecnología'},
                color=top_10_decrec['Var_pct'],
                color_continuous_scale='Reds',
                text=top_10_decrec['Var_pct']
            )
            fig7.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig7.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig7, use_container_width=True)
    
    # Tabla detallada
    with st.expander("📋 Ver Todas las Tecnologías (Tabla Detallada)"):
        display_df = lineas_por_tech.copy()
        display_df['Participación %'] = ((display_df['CANTIDAD_LINEAS_ACCESOS'] / total_lineas_tech) * 100).round(2)
        display_df.columns = ['Líneas', 'Valor Facturado', 'Valor/Línea', '% Participación']
        st.dataframe(display_df, use_container_width=True, height=400)

def show_analisis_por_departamento(df):
    """4.4 Análisis por Departamento"""
    st.markdown("## 4.4 🗺️ Análisis por Departamento")
    
    # Métricas generales
    total_lineas = df['CANTIDAD_LINEAS_ACCESOS'].sum()
    total_valor = df['VALOR_FACTURADO_O_COBRADO'].sum()
    n_departamentos = df['DEPARTAMENTO'].nunique()
    n_municipios = df['MUNICIPIO'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Departamentos", f"{n_departamentos}")
    
    with col2:
        st.metric("Municipios", f"{n_municipios}")
    
    with col3:
        st.metric("Total Líneas", f"{total_lineas:,.0f}")
    
    with col4:
        arpu_nacional = total_valor / total_lineas
        st.metric("ARPU Nacional", f"${arpu_nacional:,.0f}")
    
    # Análisis por departamento
    lineas_por_depto = df.groupby('DEPARTAMENTO').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum',
        'MUNICIPIO': 'nunique',
        'EMPRESA': 'nunique'
    }).round(0)
    lineas_por_depto.columns = ['Lineas', 'Valor', 'Municipios', 'Operadores']
    lineas_por_depto['Valor_por_linea'] = (lineas_por_depto['Valor'] / lineas_por_depto['Lineas']).round(0)
    lineas_por_depto = lineas_por_depto.sort_values('Lineas', ascending=False)
    
    # Visualizaciones principales
    st.markdown("### 📊 Top Departamentos por Líneas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 15 departamentos
        top_15_depto = lineas_por_depto.head(15)
        fig1 = px.bar(
            x=top_15_depto['Lineas'],
            y=top_15_depto.index,
            orientation='h',
            title='Top 15 Departamentos por Número de Líneas',
            labels={'x': 'Número de Líneas', 'y': 'Departamento'},
            color=top_15_depto['Lineas'],
            color_continuous_scale='Blues',
            text=top_15_depto['Lineas']
        )
        fig1.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig1.update_layout(showlegend=False, height=600)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Valor por línea Top 15
        top_15_vpl = lineas_por_depto.head(15).sort_values('Valor_por_linea', ascending=True)
        fig2 = px.bar(
            x=top_15_vpl['Valor_por_linea'],
            y=top_15_vpl.index,
            orientation='h',
            title='Valor por Línea - Top 15 Departamentos',
            labels={'x': 'Valor por Línea (COP)', 'y': 'Departamento'},
            color=top_15_vpl['Valor_por_linea'],
            color_continuous_scale='Oranges',
            text=top_15_vpl['Valor_por_linea']
        )
        fig2.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig2.update_layout(showlegend=False, height=600)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Análisis de concentración
    st.markdown("### 📈 Concentración de Mercado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Concentración Top 10
        top_10_lineas = lineas_por_depto.head(10)['Lineas'].sum()
        pct_top10 = (top_10_lineas / total_lineas * 100)
        
        concentracion_data = pd.DataFrame({
            'Categoría': ['Top 10', 'Resto'],
            'Líneas': [top_10_lineas, total_lineas - top_10_lineas]
        })
        
        fig3 = px.pie(
            concentracion_data,
            values='Líneas',
            names='Categoría',
            title=f'Concentración: Top 10 ({pct_top10:.1f}%)',
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label+value')
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Municipios por departamento
        top_10_mun = lineas_por_depto.head(10).sort_values('Municipios', ascending=True)
        fig4 = px.bar(
            x=top_10_mun['Municipios'],
            y=top_10_mun.index,
            orientation='h',
            title='Número de Municipios con Servicio (Top 10)',
            labels={'x': 'Número de Municipios', 'y': 'Departamento'},
            color=top_10_mun['Municipios'],
            color_continuous_scale='Greens',
            text=top_10_mun['Municipios']
        )
        fig4.update_traces(texttemplate='%{text}', textposition='outside')
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Evolución por año
    st.markdown("### 📅 Evolución Departamental 2023-2024")
    
    depto_ano = df.groupby(['DEPARTAMENTO', 'ANNO'])['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
    top_10_depto_names = lineas_por_depto.head(10).index.tolist()
    depto_ano_top10 = depto_ano[depto_ano['DEPARTAMENTO'].isin(top_10_depto_names)]
    
    fig5 = px.bar(
        depto_ano_top10,
        x='CANTIDAD_LINEAS_ACCESOS',
        y='DEPARTAMENTO',
        color='ANNO',
        orientation='h',
        barmode='group',
        title='Top 10 Departamentos: 2023 vs 2024',
        color_discrete_sequence=['#2E86AB', '#A23B72'],
        text='CANTIDAD_LINEAS_ACCESOS'
    )
    fig5.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig5.update_layout(height=500)
    st.plotly_chart(fig5, use_container_width=True)
    
    # Análisis de crecimiento
    st.markdown("### 📊 Análisis de Crecimiento Departamental")
    
    pivot_depto = depto_ano.pivot(index='DEPARTAMENTO', columns='ANNO', values='CANTIDAD_LINEAS_ACCESOS').fillna(0)
    
    if 2023 in pivot_depto.columns and 2024 in pivot_depto.columns:
        pivot_depto = pivot_depto[(pivot_depto[2023] > 0) & (pivot_depto[2024] > 0)]
        pivot_depto['Variacion'] = pivot_depto[2024] - pivot_depto[2023]
        pivot_depto['Var_pct'] = ((pivot_depto['Variacion'] / pivot_depto[2023]) * 100).round(2)
        
        # Filtrar departamentos con volumen significativo
        pivot_depto_filtrado = pivot_depto[pivot_depto[2023] >= pivot_depto[2023].quantile(0.3)]
        pivot_depto_filtrado = pivot_depto_filtrado.sort_values('Var_pct', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 con mayor crecimiento
            top_10_crec = pivot_depto_filtrado.head(10).sort_values('Var_pct', ascending=True)
            fig6 = px.bar(
                x=top_10_crec['Var_pct'],
                y=top_10_crec.index,
                orientation='h',
                title='Departamentos con Mayor Crecimiento (%)',
                labels={'x': 'Variación Porcentual (%)', 'y': 'Departamento'},
                color=top_10_crec['Var_pct'],
                color_continuous_scale='Greens',
                text=top_10_crec['Var_pct']
            )
            fig6.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig6.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            # Top 10 con mayor decrecimiento
            top_10_decrec = pivot_depto_filtrado.tail(10).sort_values('Var_pct', ascending=False)
            fig7 = px.bar(
                x=top_10_decrec['Var_pct'],
                y=top_10_decrec.index,
                orientation='h',
                title='Departamentos con Mayor Decrecimiento (%)',
                labels={'x': 'Variación Porcentual (%)', 'y': 'Departamento'},
                color=top_10_decrec['Var_pct'],
                color_continuous_scale='Reds',
                text=top_10_decrec['Var_pct']
            )
            fig7.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig7.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig7, use_container_width=True)
    
    # Scatter plot: Líneas vs Operadores
    st.markdown("### 🔍 Relación Líneas - Competencia")
    
    scatter_data = lineas_por_depto.head(20).reset_index()
    fig8 = px.scatter(
        scatter_data,
        x='Operadores',
        y='Lineas',
        size='Valor',
        hover_data=['DEPARTAMENTO', 'Valor_por_linea'],
        title='Líneas vs Número de Operadores (Top 20)',
        labels={
            'Operadores': 'Número de Operadores',
            'Lineas': 'Número de Líneas'
        },
        color='Valor_por_linea',
        color_continuous_scale='Viridis'
    )
    fig8.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
    st.plotly_chart(fig8, use_container_width=True)
    
    # Mapa de calor: Top departamentos vs métricas
    st.markdown("### 🔥 Mapa de Calor: Indicadores Clave")
    
    top_15_heatmap = lineas_por_depto.head(15).copy()
    # Normalizar valores para comparación
    for col in ['Lineas', 'Valor', 'Operadores', 'Valor_por_linea']:
        top_15_heatmap[f'{col}_norm'] = (
            (top_15_heatmap[col] - top_15_heatmap[col].min()) / 
            (top_15_heatmap[col].max() - top_15_heatmap[col].min())
        )
    
    heatmap_data = top_15_heatmap[['Lineas_norm', 'Valor_norm', 'Operadores_norm', 'Valor_por_linea_norm']]
    heatmap_data.columns = ['Líneas', 'Valor Total', 'Operadores', 'ARPU']
    
    fig9 = px.imshow(
        heatmap_data.T,
        labels=dict(x="Departamento", y="Métrica", color="Valor Normalizado"),
        x=heatmap_data.index,
        y=heatmap_data.columns,
        title='Comparación de Indicadores Normalizados (Top 15)',
        color_continuous_scale='RdYlGn',
        aspect='auto'
    )
    fig9.update_xaxes(side="bottom", tickangle=45)
    st.plotly_chart(fig9, use_container_width=True)
    
    # Análisis de principales municipios
    st.markdown("### 🏙️ Top Municipios por Departamento")
    
    selected_depto = st.selectbox(
        "Seleccione un departamento:",
        options=lineas_por_depto.head(15).index.tolist(),
        index=0
    )
    
    if selected_depto:
        df_depto = df[df['DEPARTAMENTO'] == selected_depto]
        mun_depto = df_depto.groupby('MUNICIPIO').agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum',
            'VALOR_FACTURADO_O_COBRADO': 'sum',
            'EMPRESA': 'nunique'
        }).round(0)
        mun_depto.columns = ['Lineas', 'Valor', 'Operadores']
        mun_depto['Valor_por_linea'] = (mun_depto['Valor'] / mun_depto['Lineas']).round(0)
        mun_depto = mun_depto.sort_values('Lineas', ascending=False).head(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig10 = px.bar(
                x=mun_depto['Lineas'],
                y=mun_depto.index,
                orientation='h',
                title=f'Top 10 Municipios en {selected_depto}',
                labels={'x': 'Número de Líneas', 'y': 'Municipio'},
                color=mun_depto['Lineas'],
                color_continuous_scale='Blues',
                text=mun_depto['Lineas']
            )
            fig10.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig10.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig10, use_container_width=True)
        
        with col2:
            # Tabla de métricas
            display_mun = mun_depto.copy()
            display_mun['Participación %'] = ((display_mun['Lineas'] / df_depto['CANTIDAD_LINEAS_ACCESOS'].sum()) * 100).round(2)
            st.dataframe(display_mun, use_container_width=True, height=500)
    
    # Tabla resumen completa
    with st.expander("📋 Ver Todos los Departamentos (Tabla Detallada)"):
        display_df = lineas_por_depto.copy()
        display_df['Participación %'] = ((display_df['Lineas'] / total_lineas) * 100).round(2)
        display_df.columns = ['Líneas', 'Valor Facturado', 'Municipios', 'Operadores', 'Valor/Línea', '% Participación']
        st.dataframe(display_df, use_container_width=True, height=400)

def show_tendencias_años(df):
    """4.5 Tendencias entre años"""
    st.markdown("## 4.5 📈 Tendencias entre Años")
    
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
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            diff_lineas = lineas_ano.loc[2024, 'CANTIDAD_LINEAS_ACCESOS'] - lineas_ano.loc[2023, 'CANTIDAD_LINEAS_ACCESOS']
            diff_pct = (diff_lineas / lineas_ano.loc[2023, 'CANTIDAD_LINEAS_ACCESOS'] * 100)
            st.metric(
                "Variación de Líneas",
                f"{diff_lineas:+,.0f}",
                delta=f"{diff_pct:+.2f}%",
                delta_color="normal" if diff_lineas > 0 else "inverse"
            )
        
        with col2:
            diff_valor = lineas_ano.loc[2024, 'VALOR_FACTURADO_O_COBRADO'] - lineas_ano.loc[2023, 'VALOR_FACTURADO_O_COBRADO']
            diff_valor_pct = (diff_valor / lineas_ano.loc[2023, 'VALOR_FACTURADO_O_COBRADO'] * 100)
            st.metric(
                "Variación de Valor",
                f"${diff_valor/1e12:+.2f}B",
                delta=f"{diff_valor_pct:+.2f}%"
            )
        
        with col3:
            diff_vpl = lineas_ano.loc[2024, 'Valor_por_linea'] - lineas_ano.loc[2023, 'Valor_por_linea']
            diff_vpl_pct = (diff_vpl / lineas_ano.loc[2023, 'Valor_por_linea'] * 100)
            st.metric(
                "Variación ARPU",
                f"${diff_vpl:+,.0f}",
                delta=f"{diff_vpl_pct:+.2f}%"
            )
        
        with col4:
            # Calcular eficiencia (valor/línea relativo)
            eficiencia_2023 = lineas_ano.loc[2023, 'Valor_por_linea']
            eficiencia_2024 = lineas_ano.loc[2024, 'Valor_por_linea']
            mejora_eficiencia = ((eficiencia_2024 - eficiencia_2023) / eficiencia_2023 * 100)
            st.metric(
                "Mejora en Monetización",
                f"{mejora_eficiencia:+.1f}%",
                delta="Positivo" if mejora_eficiencia > 0 else "Negativo"
            )
    
    # Gráficos comparativos
    st.markdown("### 📈 Evolución Trimestral")
    
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
        fig1.update_traces(marker=dict(size=10), line=dict(width=3))
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
            title='Evolución del ARPU Trimestral',
            labels={'VPL': 'Valor por Línea (COP)'},
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig2.update_traces(marker=dict(size=10), line=dict(width=3))
        fig2.update_xaxes(tickvals=[1, 2, 3, 4])
        st.plotly_chart(fig2, use_container_width=True)
    
    # Análisis por segmento
    st.markdown("### 👥 Variación por Segmento")
    
    lineas_seg_ano = df.groupby(['ANNO', 'SEGMENTO'])['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
    pivot_seg = lineas_seg_ano.pivot(index='SEGMENTO', columns='ANNO', values='CANTIDAD_LINEAS_ACCESOS').fillna(0)
    
    if 2023 in pivot_seg.columns and 2024 in pivot_seg.columns:
        pivot_seg['Variacion'] = pivot_seg[2024] - pivot_seg[2023]
        pivot_seg['Var_pct'] = ((pivot_seg['Variacion'] / pivot_seg[2023]) * 100).round(2)
        pivot_seg = pivot_seg.replace([float('inf'), -float('inf')], 0)
        pivot_seg = pivot_seg.sort_values('Variacion', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 con mayor crecimiento absoluto
            top_10_crec = pivot_seg.head(10).sort_values('Variacion', ascending=True)
            fig3 = px.bar(
                x=top_10_crec['Variacion'],
                y=top_10_crec.index,
                orientation='h',
                title='Segmentos con Mayor Crecimiento Absoluto',
                labels={'x': 'Variación de Líneas', 'y': 'Segmento'},
                color=top_10_crec['Variacion'],
                color_continuous_scale='Greens',
                text=top_10_crec['Variacion']
            )
            fig3.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
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
                color_discrete_sequence=['#2E86AB', '#A23B72'],
                text='CANTIDAD_LINEAS_ACCESOS'
            )
            fig4.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
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
        title='Evolución por Tipo de Servicio (Individual vs Empaquetado)',
        labels={'CANTIDAD_LINEAS_ACCESOS': 'Número de Líneas'}
    )
    fig5.update_traces(marker=dict(size=8), line=dict(width=2.5))
    fig5.update_xaxes(tickvals=[1, 2, 3, 4])
    st.plotly_chart(fig5, use_container_width=True)
    
    # Evolución por tecnología (Top 5)
    st.markdown("### 🔧 Evolución por Tecnología")
    
    df_tech = df[df['TECNOLOGIA'] != 'NA'].copy()
    top_5_tech = df_tech.groupby('TECNOLOGIA')['CANTIDAD_LINEAS_ACCESOS'].sum().nlargest(5).index
    lineas_tech_trim = df_tech[df_tech['TECNOLOGIA'].isin(top_5_tech)].groupby(
        ['ANNO', 'TRIMESTRE', 'TECNOLOGIA']
    )['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
    
    fig6 = px.line(
        lineas_tech_trim,
        x='TRIMESTRE',
        y='CANTIDAD_LINEAS_ACCESOS',
        color='TECNOLOGIA',
        line_dash='ANNO',
        markers=True,
        title='Evolución Top 5 Tecnologías',
        labels={'CANTIDAD_LINEAS_ACCESOS': 'Número de Líneas'}
    )
    fig6.update_traces(marker=dict(size=7), line=dict(width=2))
    fig6.update_xaxes(tickvals=[1, 2, 3, 4])
    st.plotly_chart(fig6, use_container_width=True)
    
    # Análisis de crecimiento por departamento (Top 10)
    st.markdown("### 🗺️ Crecimiento Departamental")
    
    depto_ano = df.groupby(['DEPARTAMENTO', 'ANNO'])['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
    pivot_depto = depto_ano.pivot(index='DEPARTAMENTO', columns='ANNO', values='CANTIDAD_LINEAS_ACCESOS').fillna(0)
    
    if 2023 in pivot_depto.columns and 2024 in pivot_depto.columns:
        pivot_depto = pivot_depto[(pivot_depto[2023] > 0) & (pivot_depto[2024] > 0)]
        pivot_depto['Variacion'] = pivot_depto[2024] - pivot_depto[2023]
        pivot_depto['Var_pct'] = ((pivot_depto['Variacion'] / pivot_depto[2023]) * 100).round(2)
        
        # Filtrar departamentos significativos
        pivot_depto_sig = pivot_depto[pivot_depto[2023] >= pivot_depto[2023].quantile(0.3)]
        pivot_depto_sig = pivot_depto_sig.sort_values('Var_pct', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 con mayor crecimiento
            top_10_depto_crec = pivot_depto_sig.head(10).sort_values('Var_pct', ascending=True)
            fig7 = px.bar(
                x=top_10_depto_crec['Var_pct'],
                y=top_10_depto_crec.index,
                orientation='h',
                title='Departamentos con Mayor Crecimiento (%)',
                labels={'x': 'Variación Porcentual (%)', 'y': 'Departamento'},
                color=top_10_depto_crec['Var_pct'],
                color_continuous_scale='Greens',
                text=top_10_depto_crec['Var_pct']
            )
            fig7.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig7.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig7, use_container_width=True)
        
        with col2:
            # Top 10 con mayor decrecimiento
            top_10_depto_decrec = pivot_depto_sig.tail(10).sort_values('Var_pct', ascending=False)
            fig8 = px.bar(
                x=top_10_depto_decrec['Var_pct'],
                y=top_10_depto_decrec.index,
                orientation='h',
                title='Departamentos con Mayor Decrecimiento (%)',
                labels={'x': 'Variación Porcentual (%)', 'y': 'Departamento'},
                color=top_10_depto_decrec['Var_pct'],
                color_continuous_scale='Reds',
                text=top_10_depto_decrec['Var_pct']
            )
            fig8.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig8.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig8, use_container_width=True)
    
    # Análisis combinado
    st.markdown("### 🔄 Análisis Combinado: Líneas vs Valor")
    
    combined_ano = df.groupby('ANNO').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    }).reset_index()
    
    # Gráfico de doble eje
    fig9 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig9.add_trace(
        go.Bar(
            x=combined_ano['ANNO'],
            y=combined_ano['CANTIDAD_LINEAS_ACCESOS'],
            name="Líneas",
            marker_color='#2E86AB',
            text=combined_ano['CANTIDAD_LINEAS_ACCESOS'],
            texttemplate='%{text:,.0f}',
            textposition='outside'
        ),
        secondary_y=False
    )
    
    fig9.add_trace(
        go.Scatter(
            x=combined_ano['ANNO'],
            y=combined_ano['VALOR_FACTURADO_O_COBRADO'],
            name="Valor Facturado",
            mode='lines+markers',
            marker=dict(size=15, color='#A23B72'),
            line=dict(width=3, color='#A23B72')
        ),
        secondary_y=True
    )
    
    fig9.update_xaxes(title_text="Año")
    fig9.update_yaxes(title_text="<b>Número de Líneas</b>", secondary_y=False)
    fig9.update_yaxes(title_text="<b>Valor Facturado (COP)</b>", secondary_y=True)
    fig9.update_layout(
        title_text="Evolución de Líneas vs Valor Facturado",
        height=500
    )
    
    st.plotly_chart(fig9, use_container_width=True)
    
    # Tabla de variaciones detalladas por segmento
    with st.expander("📋 Ver Variaciones Detalladas por Segmento"):
        if 'Variacion' in pivot_seg.columns:
            display_df = pivot_seg[[2023, 2024, 'Variacion', 'Var_pct']].copy()
            display_df.columns = ['Líneas 2023', 'Líneas 2024', 'Variación Absoluta', 'Variación %']
            st.dataframe(display_df, use_container_width=True, height=400)
    
    # Resumen ejecutivo
    st.markdown("### 📋 Resumen Ejecutivo de Tendencias")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **📉 Hallazgos Clave:**
        - Reducción en número de líneas activas
        - Crecimiento significativo en valor facturado
        - Aumento sustancial en ARPU
        - Indica estrategia de monetización vs volumen
        """)
    
    with col2:
        st.success("""
        **💡 Implicaciones:**
        - Mercado en fase de maduración
        - Migración a servicios premium
        - Consolidación de operadores
        - Enfoque en calidad sobre cantidad
        """)
