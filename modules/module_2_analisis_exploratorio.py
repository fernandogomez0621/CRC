"""
Módulo 2: Análisis Exploratorio Inicial
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_tipos_paquetes(df):
    """2.1 Tipos de paquetes más comunes"""
    st.markdown("## 2.1 📦 Tipos de Paquetes Más Comunes")
    
    # Filtrar solo empaquetados
    df_empaquetados = df[df['TIPO_SERVICIO'] == 'Empaquetado'].copy()
    
    if len(df_empaquetados) == 0:
        st.warning("No hay servicios empaquetados en el período seleccionado")
        return
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Empaquetados", f"{len(df_empaquetados):,}")
    
    with col2:
        duo_play = len(df_empaquetados[df_empaquetados['TIPO_PAQUETE'] == 'Duo Play'])
        st.metric("Duo Play", f"{duo_play:,}")
    
    with col3:
        triple_play = len(df_empaquetados[df_empaquetados['TIPO_PAQUETE'] == 'Triple Play'])
        st.metric("Triple Play", f"{triple_play:,}")
    
    # Visualizaciones principales
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart Duo vs Triple
        tipo_paquete_count = df_empaquetados['TIPO_PAQUETE'].value_counts()
        fig1 = px.pie(
            values=tipo_paquete_count.values,
            names=tipo_paquete_count.index,
            title='Duo Play vs Triple Play',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4']
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Detalle de Duo Play
        duo_detail = df_empaquetados[df_empaquetados['TIPO_PAQUETE'] == 'Duo Play']['SERVICIO_PAQUETE'].value_counts()
        fig2 = px.bar(
            x=duo_detail.values,
            y=duo_detail.index,
            orientation='h',
            title='Detalle de Duo Play',
            labels={'x': 'Número de Registros', 'y': 'Tipo de Duo Play'},
            color=duo_detail.values,
            color_continuous_scale='Reds'
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Comparación por año
    st.markdown("### 📊 Comparación por Año")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_ano = df_empaquetados.groupby(['TIPO_PAQUETE', 'ANNO']).size().reset_index(name='count')
        fig3 = px.bar(
            tipo_ano,
            x='TIPO_PAQUETE',
            y='count',
            color='ANNO',
            barmode='group',
            title='Paquetes por Año: 2023 vs 2024',
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Evolución trimestral
        trim_paquete = df_empaquetados.groupby(['ANNO', 'TRIMESTRE', 'TIPO_PAQUETE']).size().reset_index(name='count')
        fig4 = px.line(
            trim_paquete,
            x='TRIMESTRE',
            y='count',
            color='TIPO_PAQUETE',
            line_dash='ANNO',
            markers=True,
            title='Evolución Trimestral de Paquetes',
            labels={'count': 'Número de Registros'}
        )
        fig4.update_xaxes(tickvals=[1, 2, 3, 4])
        st.plotly_chart(fig4, use_container_width=True)
    
    # Análisis por servicio específico
    st.markdown("### 🔍 Análisis Detallado por Servicio")
    
    servicio_counts = df_empaquetados['SERVICIO_PAQUETE'].value_counts()
    fig5 = px.bar(
        x=servicio_counts.values,
        y=servicio_counts.index,
        orientation='h',
        title='Distribución por Tipo Específico de Paquete',
        labels={'x': 'Número de Registros', 'y': 'Servicio/Paquete'},
        color=servicio_counts.values,
        color_continuous_scale='Viridis'
    )
    fig5.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)
    
    # Tabla resumen
    with st.expander("📋 Ver Datos Detallados"):
        resumen = df_empaquetados.groupby(['SERVICIO_PAQUETE', 'TIPO_PAQUETE']).agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum',
            'VALOR_FACTURADO_O_COBRADO': 'sum'
        }).reset_index()
        resumen.columns = ['Servicio', 'Tipo', 'Total Líneas', 'Valor Total']
        st.dataframe(resumen, use_container_width=True)

def show_frecuencia_tecnologia(df):
    """2.2 Frecuencia por tecnología"""
    st.markdown("## 2.2 🔧 Frecuencia por Tecnología")
    
    # Filtrar tecnologías definidas
    df_con_tech = df[df['TECNOLOGIA'] != 'NA'].copy()
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tecnologías Diferentes", df_con_tech['TECNOLOGIA'].nunique())
    
    with col2:
        tech_principal = df_con_tech['TECNOLOGIA'].value_counts().index[0]
        st.metric("Tecnología Principal", tech_principal[:25])
    
    with col3:
        pct_con_tech = (len(df_con_tech) / len(df) * 100) if len(df) > 0 else 0
        st.metric("% con Tecnología Definida", f"{pct_con_tech:.1f}%")
    
    # Tabs para organizar
    tab1, tab2, tab3 = st.tabs(["📊 Distribución General", "📈 Comparación Anual", "🌍 Por Región"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 tecnologías
            top_10_tech = df_con_tech['TECNOLOGIA'].value_counts().head(10)
            fig1 = px.bar(
                x=top_10_tech.values,
                y=top_10_tech.index,
                orientation='h',
                title='Top 10 Tecnologías',
                labels={'x': 'Número de Registros', 'y': 'Tecnología'},
                color=top_10_tech.values,
                color_continuous_scale='Blues'
            )
            fig1.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Distribución porcentual
            tech_pct = (df_con_tech['TECNOLOGIA'].value_counts().head(10) / len(df_con_tech) * 100)
            fig2 = px.bar(
                x=tech_pct.index,
                y=tech_pct.values,
                title='Distribución Porcentual - Top 10',
                labels={'y': 'Porcentaje (%)', 'x': 'Tecnología'},
                color=tech_pct.values,
                color_continuous_scale='Oranges'
            )
            fig2.update_layout(showlegend=False, height=500)
            fig2.update_xaxes(tickangle=45)
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Comparación 2023 vs 2024
            top_10_tech_names = df_con_tech['TECNOLOGIA'].value_counts().head(10).index
            df_top_tech = df_con_tech[df_con_tech['TECNOLOGIA'].isin(top_10_tech_names)]
            tech_ano = df_top_tech.groupby(['TECNOLOGIA', 'ANNO']).size().reset_index(name='count')
            
            fig3 = px.bar(
                tech_ano,
                x='count',
                y='TECNOLOGIA',
                color='ANNO',
                orientation='h',
                barmode='group',
                title='Top 10 Tecnologías: 2023 vs 2024',
                color_discrete_sequence=['#2E86AB', '#A23B72']
            )
            fig3.update_layout(height=500)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Evolución trimestral Top 5
            top_5_tech = df_con_tech['TECNOLOGIA'].value_counts().head(5).index
            trim_tech = df_con_tech[df_con_tech['TECNOLOGIA'].isin(top_5_tech)].groupby(
                ['ANNO', 'TRIMESTRE', 'TECNOLOGIA']
            ).size().reset_index(name='count')
            
            fig4 = px.line(
                trim_tech,
                x='TRIMESTRE',
                y='count',
                color='TECNOLOGIA',
                line_dash='ANNO',
                markers=True,
                title='Evolución Trimestral - Top 5 Tecnologías',
                labels={'count': 'Número de Registros'}
            )
            fig4.update_xaxes(tickvals=[1, 2, 3, 4])
            fig4.update_layout(height=500)
            st.plotly_chart(fig4, use_container_width=True)
    
    with tab3:
        # Tecnologías por región
        region_tech = df_con_tech.groupby(['REGION', 'TECNOLOGIA']).size().reset_index(name='count')
        
        # Top 3 tecnologías por región
        top_tech_por_region = []
        for region in df_con_tech['REGION'].unique():
            top_3 = region_tech[region_tech['REGION'] == region].nlargest(3, 'count')
            top_tech_por_region.append(top_3)
        
        top_tech_df = pd.concat(top_tech_por_region)
        
        fig5 = px.bar(
            top_tech_df,
            x='count',
            y='REGION',
            color='TECNOLOGIA',
            orientation='h',
            title='Top 3 Tecnologías por Región',
            labels={'count': 'Número de Registros'},
            barmode='group'
        )
        fig5.update_layout(height=500)
        st.plotly_chart(fig5, use_container_width=True)
        
        # Heatmap región-tecnología
        st.markdown("#### 🔥 Heatmap: Región vs Tecnología (Top 5)")
        top_5_tech_names = df_con_tech['TECNOLOGIA'].value_counts().head(5).index
        heatmap_data = pd.crosstab(
            df_con_tech[df_con_tech['TECNOLOGIA'].isin(top_5_tech_names)]['REGION'],
            df_con_tech[df_con_tech['TECNOLOGIA'].isin(top_5_tech_names)]['TECNOLOGIA']
        )
        
        fig6 = px.imshow(
            heatmap_data,
            labels=dict(x="Tecnología", y="Región", color="Registros"),
            title="Distribución de Tecnologías por Región",
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        st.plotly_chart(fig6, use_container_width=True)

def show_comparacion_años(df):
    """2.3 Comparación entre 2023 y 2024"""
    st.markdown("## 2.3 📊 Comparación 2023 vs 2024")
    
    # Calcular métricas por año
    metricas = {}
    for ano in df['ANNO'].unique():
        df_ano = df[df['ANNO'] == ano]
        metricas[ano] = {
            'registros': len(df_ano),
            'lineas': df_ano['CANTIDAD_LINEAS_ACCESOS'].sum(),
            'valor_facturado': df_ano['VALOR_FACTURADO_O_COBRADO'].sum(),
            'operadores': df_ano['EMPRESA'].nunique(),
            'departamentos': df_ano['DEPARTAMENTO'].nunique(),
            'municipios': df_ano['MUNICIPIO'].nunique()
        }
    
    # Métricas principales
    st.markdown("### 📈 Métricas Clave")
    
    col1, col2, col3 = st.columns(3)
    
    if 2023 in metricas and 2024 in metricas:
        with col1:
            diff_registros = metricas[2024]['registros'] - metricas[2023]['registros']
            diff_pct = (diff_registros / metricas[2023]['registros'] * 100) if metricas[2023]['registros'] > 0 else 0
            st.metric(
                "Variación de Registros",
                f"{diff_registros:+,}",
                delta=f"{diff_pct:+.2f}%"
            )
        
        with col2:
            diff_lineas = metricas[2024]['lineas'] - metricas[2023]['lineas']
            diff_pct_lineas = (diff_lineas / metricas[2023]['lineas'] * 100) if metricas[2023]['lineas'] > 0 else 0
            st.metric(
                "Variación de Líneas",
                f"{diff_lineas:+,.0f}",
                delta=f"{diff_pct_lineas:+.2f}%"
            )
        
        with col3:
            diff_valor = metricas[2024]['valor_facturado'] - metricas[2023]['valor_facturado']
            diff_pct_valor = (diff_valor / metricas[2023]['valor_facturado'] * 100) if metricas[2023]['valor_facturado'] > 0 else 0
            st.metric(
                "Variación de Valor",
                f"${diff_valor/1e9:+.2f}B",
                delta=f"{diff_pct_valor:+.2f}%"
            )
    
    # Tabla comparativa
    st.markdown("### 📋 Tabla Comparativa Detallada")
    
    if len(metricas) >= 2:
        comparacion_data = []
        metricas_nombres = {
            'registros': 'Registros',
            'lineas': 'Líneas totales',
            'valor_facturado': 'Valor facturado',
            'operadores': 'Operadores',
            'departamentos': 'Departamentos',
            'municipios': 'Municipios'
        }
        
        for key, nombre in metricas_nombres.items():
            val_2023 = metricas.get(2023, {}).get(key, 0)
            val_2024 = metricas.get(2024, {}).get(key, 0)
            diff = val_2024 - val_2023
            diff_pct = (diff / val_2023 * 100) if val_2023 > 0 else 0
            
            comparacion_data.append({
                'Métrica': nombre,
                '2023': val_2023,
                '2024': val_2024,
                'Diferencia': diff,
                'Variación %': f"{diff_pct:+.2f}%"
            })
        
        comparacion_df = pd.DataFrame(comparacion_data)
        st.dataframe(comparacion_df, use_container_width=True, hide_index=True)
    
    # Visualizaciones
    st.markdown("### 📊 Visualizaciones Comparativas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras métricas generales
        if len(metricas) >= 2:
            metricas_viz = ['registros', 'operadores', 'departamentos', 'municipios']
            nombres_viz = ['Registros', 'Operadores', 'Departamentos', 'Municipios']
            
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                name='2023',
                x=nombres_viz,
                y=[metricas.get(2023, {}).get(m, 0) for m in metricas_viz],
                marker_color='#2E86AB'
            ))
            fig1.add_trace(go.Bar(
                name='2024',
                x=nombres_viz,
                y=[metricas.get(2024, {}).get(m, 0) for m in metricas_viz],
                marker_color='#A23B72'
            ))
            fig1.update_layout(
                title='Métricas Generales: 2023 vs 2024',
                barmode='group',
                height=400
            )
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Líneas por año
        if len(metricas) >= 2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=[2023, 2024],
                y=[metricas.get(2023, {}).get('lineas', 0), metricas.get(2024, {}).get('lineas', 0)],
                marker_color=['#2E86AB', '#A23B72'],
                text=[f"{metricas.get(2023, {}).get('lineas', 0):,.0f}", 
                      f"{metricas.get(2024, {}).get('lineas', 0):,.0f}"],
                textposition='outside'
            ))
            fig2.update_layout(
                title='Líneas Totales por Año',
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Análisis por segmento
    st.markdown("### 🎯 Comparación por Segmento")
    
    segmento_comp = df.groupby(['ANNO', 'SEGMENTO']).agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 8 segmentos por líneas
        top_8_seg = df.groupby('SEGMENTO')['CANTIDAD_LINEAS_ACCESOS'].sum().nlargest(8).index
        seg_lineas = segmento_comp[segmento_comp['SEGMENTO'].isin(top_8_seg)]
        
        fig3 = px.bar(
            seg_lineas,
            x='CANTIDAD_LINEAS_ACCESOS',
            y='SEGMENTO',
            color='ANNO',
            orientation='h',
            barmode='group',
            title='Líneas por Segmento (Top 8): 2023 vs 2024',
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig3.update_layout(height=500)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Top 8 segmentos por valor
        seg_valor = segmento_comp[segmento_comp['SEGMENTO'].isin(top_8_seg)]
        
        fig4 = px.bar(
            seg_valor,
            x='VALOR_FACTURADO_O_COBRADO',
            y='SEGMENTO',
            color='ANNO',
            orientation='h',
            barmode='group',
            title='Valor Facturado por Segmento (Top 8): 2023 vs 2024',
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig4.update_layout(height=500)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Evolución mensual
    st.markdown("### 📅 Evolución Trimestral Detallada")
    
    trim_comp = df.groupby(['ANNO', 'TRIMESTRE']).agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig5 = px.line(
            trim_comp,
            x='TRIMESTRE',
            y='CANTIDAD_LINEAS_ACCESOS',
            color='ANNO',
            markers=True,
            title='Evolución Trimestral de Líneas',
            labels={'CANTIDAD_LINEAS_ACCESOS': 'Total de Líneas'},
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig5.update_xaxes(tickvals=[1, 2, 3, 4])
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        fig6 = px.line(
            trim_comp,
            x='TRIMESTRE',
            y='VALOR_FACTURADO_O_COBRADO',
            color='ANNO',
            markers=True,
            title='Evolución Trimestral de Valor Facturado',
            labels={'VALOR_FACTURADO_O_COBRADO': 'Valor Facturado'},
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig6.update_xaxes(tickvals=[1, 2, 3, 4])
        st.plotly_chart(fig6, use_container_width=True)