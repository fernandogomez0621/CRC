"""
Módulo 1: Descripción General de la Base de Datos
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_registros_por_año(df):
    """1.1 Número total de registros por año"""
    st.markdown("## 1.1 📊 Registros por Año")
    
    # Métricas principales
    registros_por_ano = df.groupby('ANNO').size()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 2023 in registros_por_ano.index:
            st.metric("Registros 2023", f"{registros_por_ano[2023]:,}")
    
    with col2:
        if 2024 in registros_por_ano.index:
            st.metric("Registros 2024", f"{registros_por_ano[2024]:,}")
    
    with col3:
        if len(registros_por_ano) >= 2:
            diff = registros_por_ano[2024] - registros_por_ano[2023]
            diff_pct = (diff / registros_por_ano[2023]) * 100
            st.metric(
                "Variación", 
                f"{diff:+,}",
                delta=f"{diff_pct:+.2f}%"
            )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras por año
        fig1 = px.bar(
            x=registros_por_ano.index,
            y=registros_por_ano.values,
            labels={'x': 'Año', 'y': 'Número de Registros'},
            title='Registros por Año',
            color=registros_por_ano.index,
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig1.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Gráfico por trimestre
        trim_ano = df.groupby(['ANNO', 'TRIMESTRE']).size().reset_index(name='count')
        fig2 = px.line(
            trim_ano,
            x='TRIMESTRE',
            y='count',
            color='ANNO',
            markers=True,
            title='Registros por Trimestre',
            labels={'count': 'Número de Registros', 'TRIMESTRE': 'Trimestre'},
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig2.update_layout(height=400)
        fig2.update_xaxes(tickvals=[1, 2, 3, 4])
        st.plotly_chart(fig2, use_container_width=True)
    
    # Tabla detallada
    with st.expander("📋 Ver Datos Detallados"):
        st.dataframe(
            trim_ano.pivot(index='TRIMESTRE', columns='ANNO', values='count'),
            use_container_width=True
        )

def show_operadores(df):
    """1.2 Conteo de operadores reportados"""
    st.markdown("## 1.2 🏢 Operadores")
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Operadores", df['EMPRESA'].nunique())
    
    with col2:
        ops_2023 = set(df[df['ANNO'] == 2023]['EMPRESA'].unique()) if 2023 in df['ANNO'].values else set()
        ops_2024 = set(df[df['ANNO'] == 2024]['EMPRESA'].unique()) if 2024 in df['ANNO'].values else set()
        ops_comunes = len(ops_2023.intersection(ops_2024))
        st.metric("Operadores en Ambos Años", ops_comunes)
    
    with col3:
        top_operador = df['EMPRESA'].value_counts().index[0]
        st.metric("Operador Principal", top_operador[:20] + "...")
    
    # Gráficos
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Top 10 operadores
        top_10_ops = df['EMPRESA'].value_counts().head(10)
        fig1 = px.bar(
            x=top_10_ops.values,
            y=[op[:30] for op in top_10_ops.index],
            orientation='h',
            title='Top 10 Operadores por Número de Registros',
            labels={'x': 'Número de Registros', 'y': 'Operador'},
            color=top_10_ops.values,
            color_continuous_scale='Blues'
        )
        fig1.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Comparación 2023 vs 2024
        top_10_empresas = df['EMPRESA'].value_counts().head(10).index
        df_top_10 = df[df['EMPRESA'].isin(top_10_empresas)]
        valor_ops_ano = df_top_10.groupby(['EMPRESA', 'ANNO']).size().reset_index(name='count')
        
        fig2 = px.bar(
            valor_ops_ano,
            x='count',
            y='EMPRESA',
            color='ANNO',
            orientation='h',
            barmode='group',
            title='Top 10 Operadores: 2023 vs 2024',
            labels={'count': 'Número de Registros', 'EMPRESA': 'Operador'},
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig2.update_layout(height=500)
        fig2.update_yaxes(ticktext=[op[:25] for op in top_10_empresas], 
                          tickvals=list(top_10_empresas))
        st.plotly_chart(fig2, use_container_width=True)
    
    # Tabla detallada
    with st.expander("📋 Ver Todos los Operadores"):
        operadores_df = df.groupby('EMPRESA').agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum',
            'VALOR_FACTURADO_O_COBRADO': 'sum',
            'DEPARTAMENTO': 'nunique'
        }).reset_index()
        operadores_df.columns = ['Operador', 'Total Líneas', 'Valor Total', 'N° Departamentos']
        operadores_df = operadores_df.sort_values('Valor Total', ascending=False)
        st.dataframe(operadores_df, use_container_width=True, height=400)

def show_cobertura_geografica(df):
    """1.3 Distribución por departamentos y municipios"""
    st.markdown("## 1.3 🗺️ Cobertura Geográfica")
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Departamentos", df['DEPARTAMENTO'].nunique())
    
    with col2:
        st.metric("Municipios", df['MUNICIPIO'].nunique())
    
    with col3:
        top_depto = df['DEPARTAMENTO'].value_counts().index[0]
        st.metric("Depto. con Más Registros", top_depto)
    
    with col4:
        regiones = df['REGION'].nunique()
        st.metric("Regiones", regiones)
    
    # Tabs para organizar visualizaciones
    tab1, tab2, tab3 = st.tabs(["📊 Departamentos", "🏙️ Municipios", "🌎 Regiones"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 15 departamentos
            top_15_deptos = df['DEPARTAMENTO'].value_counts().head(15)
            fig1 = px.bar(
                x=top_15_deptos.values,
                y=top_15_deptos.index,
                orientation='h',
                title='Top 15 Departamentos por Registros',
                labels={'x': 'Número de Registros', 'y': 'Departamento'},
                color=top_15_deptos.values,
                color_continuous_scale='Viridis'
            )
            fig1.update_layout(showlegend=False, height=600)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Comparación 2023 vs 2024
            top_10_deptos = df['DEPARTAMENTO'].value_counts().head(10).index
            df_top_deptos = df[df['DEPARTAMENTO'].isin(top_10_deptos)]
            deptos_ano = df_top_deptos.groupby(['DEPARTAMENTO', 'ANNO']).size().reset_index(name='count')
            
            fig2 = px.bar(
                deptos_ano,
                x='count',
                y='DEPARTAMENTO',
                color='ANNO',
                orientation='h',
                barmode='group',
                title='Top 10 Departamentos: 2023 vs 2024',
                color_discrete_sequence=['#2E86AB', '#A23B72']
            )
            fig2.update_layout(height=600)
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 15 municipios
            top_15_mun = df['MUNICIPIO'].value_counts().head(15)
            fig3 = px.bar(
                x=top_15_mun.values,
                y=top_15_mun.index,
                orientation='h',
                title='Top 15 Municipios por Registros',
                labels={'x': 'Número de Registros', 'y': 'Municipio'},
                color=top_15_mun.values,
                color_continuous_scale='Oranges'
            )
            fig3.update_layout(showlegend=False, height=600)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Municipios por departamento
            mun_por_depto = df.groupby('DEPARTAMENTO')['MUNICIPIO'].nunique().sort_values(ascending=False).head(10)
            fig4 = px.bar(
                x=mun_por_depto.values,
                y=mun_por_depto.index,
                orientation='h',
                title='Departamentos con Más Municipios',
                labels={'x': 'Número de Municipios', 'y': 'Departamento'}
            )
            fig4.update_layout(height=600)
            st.plotly_chart(fig4, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución por región
            region_counts = df['REGION'].value_counts()
            fig5 = px.pie(
                values=region_counts.values,
                names=region_counts.index,
                title='Distribución de Registros por Región',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig5.update_layout(height=500)
            st.plotly_chart(fig5, use_container_width=True)
        
        with col2:
            # Registros por región y año
            region_ano = df.groupby(['REGION', 'ANNO']).size().reset_index(name='count')
            fig6 = px.bar(
                region_ano,
                x='REGION',
                y='count',
                color='ANNO',
                barmode='group',
                title='Registros por Región y Año',
                color_discrete_sequence=['#2E86AB', '#A23B72']
            )
            fig6.update_layout(height=500)
            st.plotly_chart(fig6, use_container_width=True)

def show_servicios_individual_vs_empaquetado(df):
    """1.4 Distribución de servicios individuales vs empaquetados"""
    st.markdown("## 1.4 📦 Servicios: Individual vs Empaquetado")
    
    # Métricas
    tipo_servicio_count = df['TIPO_SERVICIO'].value_counts()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        individuales = tipo_servicio_count.get('Individual', 0)
        st.metric("Servicios Individuales", f"{individuales:,}")
    
    with col2:
        empaquetados = tipo_servicio_count.get('Empaquetado', 0)
        st.metric("Servicios Empaquetados", f"{empaquetados:,}")
    
    with col3:
        pct_empaquetado = (empaquetados / len(df) * 100) if len(df) > 0 else 0
        st.metric("% Empaquetados", f"{pct_empaquetado:.1f}%")
    
    # Visualizaciones
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart general
        fig1 = px.pie(
            values=tipo_servicio_count.values,
            names=tipo_servicio_count.index,
            title='Distribución: Individual vs Empaquetado',
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Comparación por año
        tipo_ano = df.groupby(['TIPO_SERVICIO', 'ANNO']).size().reset_index(name='count')
        fig2 = px.bar(
            tipo_ano,
            x='TIPO_SERVICIO',
            y='count',
            color='ANNO',
            barmode='group',
            title='Individual vs Empaquetado: 2023 vs 2024',
            color_discrete_sequence=['#2E86AB', '#A23B72']
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detalle por servicio
    st.markdown("### 📋 Detalle por Tipo de Servicio/Paquete")
    
    servicio_detail = df.groupby(['SERVICIO_PAQUETE', 'TIPO_SERVICIO']).size().reset_index(name='count')
    servicio_detail['Porcentaje'] = (servicio_detail['count'] / len(df) * 100).round(2)
    servicio_detail = servicio_detail.sort_values('count', ascending=False)
    
    fig3 = px.bar(
        servicio_detail,
        x='count',
        y='SERVICIO_PAQUETE',
        orientation='h',
        color='TIPO_SERVICIO',
        title='Registros por Tipo de Servicio/Paquete',
        labels={'count': 'Número de Registros', 'SERVICIO_PAQUETE': 'Servicio/Paquete'},
        color_discrete_sequence=['#2E86AB', '#A23B72']
    )
    fig3.update_layout(height=500)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Evolución trimestral
    st.markdown("### 📈 Evolución Trimestral")
    
    trim_tipo = df.groupby(['ANNO', 'TRIMESTRE', 'TIPO_SERVICIO']).size().reset_index(name='count')
    
    fig4 = px.line(
        trim_tipo,
        x='TRIMESTRE',
        y='count',
        color='TIPO_SERVICIO',
        line_dash='ANNO',
        markers=True,
        title='Evolución Trimestral por Tipo de Servicio',
        labels={'count': 'Número de Registros', 'TRIMESTRE': 'Trimestre'}
    )
    fig4.update_xaxes(tickvals=[1, 2, 3, 4])
    st.plotly_chart(fig4, use_container_width=True)
    
    # Tabla resumen
    with st.expander("📊 Ver Tabla Resumen"):
        st.dataframe(servicio_detail, use_container_width=True)