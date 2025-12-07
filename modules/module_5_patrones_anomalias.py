"""
Módulo 5: Identificación de Patrones y Anomalías
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def show_municipios_crecimiento(df):
    """5.1 Municipios con crecimiento inusualmente alto o bajo"""
    st.markdown("## 5.1 🏙️ Municipios con Crecimiento Inusual")
    
    # Calcular crecimiento por municipio
    lineas_mun_ano = df.groupby(['MUNICIPIO', 'DEPARTAMENTO', 'ANNO'])['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
    pivot_mun = lineas_mun_ano.pivot_table(
        index=['MUNICIPIO', 'DEPARTAMENTO'], 
        columns='ANNO', 
        values='CANTIDAD_LINEAS_ACCESOS', 
        fill_value=0
    )
    
    # Solo municipios con datos en ambos años
    if 2023 in pivot_mun.columns and 2024 in pivot_mun.columns:
        pivot_mun = pivot_mun[(pivot_mun[2023] > 0) & (pivot_mun[2024] > 0)]
        pivot_mun['Variacion'] = pivot_mun[2024] - pivot_mun[2023]
        pivot_mun['Var_pct'] = ((pivot_mun['Variacion'] / pivot_mun[2023]) * 100).round(2)
        
        # Filtrar municipios significativos (top 50% en volumen 2023)
        pivot_mun_filtrado = pivot_mun[pivot_mun[2023] >= pivot_mun[2023].quantile(0.5)]
        
        # Métricas
        st.markdown("### 📊 Estadísticas de Crecimiento")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            n_crecimiento = len(pivot_mun_filtrado[pivot_mun_filtrado['Var_pct'] > 0])
            st.metric("Municipios en Crecimiento", n_crecimiento)
        
        with col2:
            n_decrecimiento = len(pivot_mun_filtrado[pivot_mun_filtrado['Var_pct'] < 0])
            st.metric("Municipios en Decrecimiento", n_decrecimiento)
        
        with col3:
            var_media = pivot_mun_filtrado['Var_pct'].mean()
            st.metric("Variación Media", f"{var_media:+.2f}%")
        
        with col4:
            var_mediana = pivot_mun_filtrado['Var_pct'].median()
            st.metric("Variación Mediana", f"{var_mediana:+.2f}%")
        
        # Visualizaciones
        col1, col2 = st.columns(2)
        
        with col1:
            # Mayor crecimiento
            top_crec = pivot_mun_filtrado.nlargest(10, 'Var_pct')
            municipios_labels = [f"{m} ({d[:15]})" for m, d in top_crec.index]
            
            fig1 = px.bar(
                x=top_crec['Var_pct'],
                y=municipios_labels,
                orientation='h',
                title='Top 10 Municipios con Mayor Crecimiento',
                labels={'x': 'Variación (%)', 'y': 'Municipio'},
                color=top_crec['Var_pct'],
                color_continuous_scale='Greens'
            )
            fig1.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Mayor decrecimiento
            top_decrec = pivot_mun_filtrado.nsmallest(10, 'Var_pct')
            municipios_labels_d = [f"{m} ({d[:15]})" for m, d in top_decrec.index]
            
            fig2 = px.bar(
                x=top_decrec['Var_pct'],
                y=municipios_labels_d,
                orientation='h',
                title='Top 10 Municipios con Mayor Decrecimiento',
                labels={'x': 'Variación (%)', 'y': 'Municipio'},
                color=top_decrec['Var_pct'],
                color_continuous_scale='Reds'
            )
            fig2.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Distribución de variaciones
        st.markdown("### 📈 Distribución de Variaciones")
        
        fig3 = px.histogram(
            pivot_mun_filtrado,
            x='Var_pct',
            nbins=50,
            title='Distribución de Variaciones Porcentuales',
            labels={'Var_pct': 'Variación (%)'},
            color_discrete_sequence=['#1D3557']
        )
        fig3.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Sin cambio")
        fig3.add_vline(x=var_mediana, line_dash="dash", line_color="orange", 
                      annotation_text=f"Mediana: {var_mediana:.1f}%")
        st.plotly_chart(fig3, use_container_width=True)
        
        # Top municipios por volumen - comparación
        st.markdown("### 🏆 Top 10 Municipios por Volumen")
        
        top_10_vol = pivot_mun.nlargest(10, 2024)
        municipios_vol_labels = [f"{m[:20]} ({d[:10]})" for m, d in top_10_vol.index]
        
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            name='2023',
            y=municipios_vol_labels,
            x=top_10_vol[2023],
            orientation='h',
            marker_color='#2E86AB'
        ))
        fig4.add_trace(go.Bar(
            name='2024',
            y=municipios_vol_labels,
            x=top_10_vol[2024],
            orientation='h',
            marker_color='#A23B72'
        ))
        fig4.update_layout(
            title='Top 10 Municipios por Volumen: 2023 vs 2024',
            barmode='group',
            height=500
        )
        st.plotly_chart(fig4, use_container_width=True)
        
        # Tabla detallada
        with st.expander("📋 Ver Lista Completa de Variaciones"):
            display_df = pivot_mun_filtrado.reset_index()
            display_df.columns = ['Municipio', 'Departamento', 'Líneas 2023', 'Líneas 2024', 'Variación', 'Variación %']
            display_df = display_df.sort_values('Variación %', ascending=False)
            st.dataframe(display_df, use_container_width=True, height=400)

def show_valores_anomalos(df):
    """5.2 Paquetes con valores facturados fuera de rangos normales"""
    st.markdown("## 5.2 🚨 Valores Facturados Anómalos")
    
    st.info("💡 Se consideran outliers los valores fuera del rango [Q1 - 1.5×IQR, Q3 + 1.5×IQR]")
    
    # Análisis de outliers por servicio
    st.markdown("### 📊 Outliers por Servicio/Paquete")
    
    outliers_info = []
    for servicio in sorted(df['ID_SERVICIO_PAQUETE'].unique()):
        df_serv = df[(df['ID_SERVICIO_PAQUETE'] == servicio) & (df['VALOR_FACTURADO_O_COBRADO'] > 0)]
        
        if len(df_serv) > 0:
            Q1 = df_serv['VALOR_FACTURADO_O_COBRADO'].quantile(0.25)
            Q3 = df_serv['VALOR_FACTURADO_O_COBRADO'].quantile(0.75)
            IQR = Q3 - Q1
            limite_inf = Q1 - 1.5 * IQR
            limite_sup = Q3 + 1.5 * IQR
            
            outliers = df_serv[
                (df_serv['VALOR_FACTURADO_O_COBRADO'] < limite_inf) | 
                (df_serv['VALOR_FACTURADO_O_COBRADO'] > limite_sup)
            ]
            pct_outliers = (len(outliers) / len(df_serv) * 100)
            
            nombre = df_serv['SERVICIO_PAQUETE'].iloc[0]
            outliers_info.append({
                'Servicio': nombre,
                'Total Registros': len(df_serv),
                'Outliers': len(outliers),
                'Porcentaje': pct_outliers,
                'Rango Normal': f"${limite_inf:,.0f} - ${limite_sup:,.0f}"
            })
    
    outliers_df = pd.DataFrame(outliers_info).sort_values('Porcentaje', ascending=False)
    
    # Visualización de porcentaje de outliers
    fig1 = px.bar(
        outliers_df,
        x='Porcentaje',
        y='Servicio',
        orientation='h',
        title='Porcentaje de Outliers por Servicio',
        labels={'Porcentaje': 'Porcentaje de Outliers (%)'},
        color='Porcentaje',
        color_continuous_scale='Reds'
    )
    fig1.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Boxplots por servicio
    st.markdown("### 📦 Distribución de Valores por Servicio")
    
    # Filtrar valores para mejor visualización
    df_plot = df[df['VALOR_FACTURADO_O_COBRADO'] > 0].copy()
    df_plot = df_plot[df_plot['VALOR_FACTURADO_O_COBRADO'] < df_plot['VALOR_FACTURADO_O_COBRADO'].quantile(0.95)]
    
    fig2 = px.box(
        df_plot,
        x='SERVICIO_PAQUETE',
        y='VALOR_FACTURADO_O_COBRADO',
        title='Distribución de Valores Facturados (hasta P95)',
        labels={'VALOR_FACTURADO_O_COBRADO': 'Valor Facturado', 'SERVICIO_PAQUETE': 'Servicio'},
        color='SERVICIO_PAQUETE'
    )
    fig2.update_xaxes(tickangle=45)
    fig2.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Top registros con valores extremos
    st.markdown("### 🔝 Top 10 Registros con Mayor Valor Facturado")
    
    top_valores = df.nlargest(10, 'VALOR_FACTURADO_O_COBRADO')[
        ['EMPRESA', 'DEPARTAMENTO', 'MUNICIPIO', 'SERVICIO_PAQUETE', 
         'CANTIDAD_LINEAS_ACCESOS', 'VALOR_FACTURADO_O_COBRADO', 'ANNO', 'TRIMESTRE']
    ].copy()
    
    top_valores['VALOR_POR_LINEA'] = (
        top_valores['VALOR_FACTURADO_O_COBRADO'] / top_valores['CANTIDAD_LINEAS_ACCESOS']
    ).round(0)
    
    st.dataframe(top_valores, use_container_width=True, hide_index=True)
    
    # Scatter: Líneas vs Valor (con outliers marcados)
    st.markdown("### 📈 Identificación Visual de Outliers")
    
    df_scatter = df[(df['CANTIDAD_LINEAS_ACCESOS'] > 0) & (df['VALOR_FACTURADO_O_COBRADO'] > 0)].copy()
    df_scatter['VALOR_POR_LINEA'] = df_scatter['VALOR_FACTURADO_O_COBRADO'] / df_scatter['CANTIDAD_LINEAS_ACCESOS']
    
    Q1_vpl = df_scatter['VALOR_POR_LINEA'].quantile(0.25)
    Q3_vpl = df_scatter['VALOR_POR_LINEA'].quantile(0.75)
    IQR_vpl = Q3_vpl - Q1_vpl
    limite_inf_vpl = Q1_vpl - 1.5 * IQR_vpl
    limite_sup_vpl = Q3_vpl + 1.5 * IQR_vpl
    
    df_scatter['ES_OUTLIER'] = (
        (df_scatter['VALOR_POR_LINEA'] < limite_inf_vpl) | 
        (df_scatter['VALOR_POR_LINEA'] > limite_sup_vpl)
    )
    
    # Muestra para visualización
    sample_size = min(5000, len(df_scatter))
    df_sample = df_scatter.sample(sample_size)
    
    fig3 = px.scatter(
        df_sample,
        x='CANTIDAD_LINEAS_ACCESOS',
        y='VALOR_FACTURADO_O_COBRADO',
        color='ES_OUTLIER',
        title='Identificación de Outliers: Líneas vs Valor',
        labels={
            'CANTIDAD_LINEAS_ACCESOS': 'Cantidad de Líneas',
            'VALOR_FACTURADO_O_COBRADO': 'Valor Facturado',
            'ES_OUTLIER': 'Es Outlier'
        },
        color_discrete_map={True: '#E63946', False: '#2E86AB'},
        opacity=0.5
    )
    fig3.update_layout(height=500)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Evolución temporal de outliers
    st.markdown("### 📅 Evolución Temporal de Outliers")
    
    outliers_por_trim = []
    for ano in df['ANNO'].unique():
        for trim in [1, 2, 3, 4]:
            df_periodo = df_scatter[(df_scatter['ANNO'] == ano) & (df_scatter['TRIMESTRE'] == trim)]
            if len(df_periodo) > 0:
                Q1 = df_periodo['VALOR_POR_LINEA'].quantile(0.25)
                Q3 = df_periodo['VALOR_POR_LINEA'].quantile(0.75)
                IQR = Q3 - Q1
                limite_inf = Q1 - 1.5 * IQR
                limite_sup = Q3 + 1.5 * IQR
                
                n_outliers = len(df_periodo[
                    (df_periodo['VALOR_POR_LINEA'] < limite_inf) | 
                    (df_periodo['VALOR_POR_LINEA'] > limite_sup)
                ])
                pct = (n_outliers / len(df_periodo) * 100)
                
                outliers_por_trim.append({
                    'Año': ano,
                    'Trimestre': trim,
                    'Porcentaje': pct
                })
    
    outliers_trim_df = pd.DataFrame(outliers_por_trim)
    
    fig4 = px.line(
        outliers_trim_df,
        x='Trimestre',
        y='Porcentaje',
        color='Año',
        markers=True,
        title='Evolución del Porcentaje de Outliers',
        labels={'Porcentaje': 'Porcentaje de Outliers (%)'},
        color_discrete_sequence=['#2E86AB', '#A23B72']
    )
    fig4.update_xaxes(tickvals=[1, 2, 3, 4])
    st.plotly_chart(fig4, use_container_width=True)
    
    # Tabla resumen
    with st.expander("📋 Ver Resumen de Outliers por Servicio"):
        st.dataframe(outliers_df, use_container_width=True, hide_index=True)

def show_tecnologias_zona(df):
    """5.3 Comparación de tecnologías usadas por zona geográfica"""
    st.markdown("## 5.3 🗺️ Tecnologías por Zona Geográfica")
    
    # Filtrar tecnologías definidas
    df_con_tech = df[df['TECNOLOGIA'] != 'NA'].copy()
    
    # Métricas generales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tecnologías Diferentes", df_con_tech['TECNOLOGIA'].nunique())
    
    with col2:
        st.metric("Departamentos", df_con_tech['DEPARTAMENTO'].nunique())
    
    with col3:
        st.metric("Regiones", df_con_tech['REGION'].nunique())
    
    # Tabs para análisis
    tab1, tab2, tab3 = st.tabs(["🏛️ Por Departamento", "🌎 Por Región", "📊 Diversidad Tecnológica"])
    
    with tab1:
        st.markdown("### Top 5 Tecnologías por Departamento")
        
        # Selector de departamento
        top_10_deptos = df_con_tech['DEPARTAMENTO'].value_counts().head(10).index.tolist()
        depto_seleccionado = st.selectbox(
            "Seleccione un departamento:",
            top_10_deptos
        )
        
        df_depto = df_con_tech[df_con_tech['DEPARTAMENTO'] == depto_seleccionado]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top tecnologías en el departamento
            top_tech_depto = df_depto['TECNOLOGIA'].value_counts().head(5)
            fig1 = px.pie(
                values=top_tech_depto.values,
                names=top_tech_depto.index,
                title=f'Top 5 Tecnologías en {depto_seleccionado}',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Comparación con nacional
            tech_nacional = df_con_tech['TECNOLOGIA'].value_counts(normalize=True).head(5) * 100
            tech_depto_pct = df_depto['TECNOLOGIA'].value_counts(normalize=True).head(5) * 100
            
            # Combinar datos
            comp_data = pd.DataFrame({
                'Nacional': tech_nacional,
                depto_seleccionado: tech_depto_pct
            }).fillna(0)
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name='Nacional',
                x=comp_data.index,
                y=comp_data['Nacional'],
                marker_color='#2E86AB'
            ))
            fig2.add_trace(go.Bar(
                name=depto_seleccionado,
                x=comp_data.index,
                y=comp_data[depto_seleccionado],
                marker_color='#A23B72'
            ))
            fig2.update_layout(
                title='Comparación con Promedio Nacional',
                barmode='group',
                xaxis_tickangle=45
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Heatmap Top 10 departamentos vs Top 5 tecnologías
        st.markdown("### 🔥 Heatmap: Departamentos vs Tecnologías")
        
        top_5_tech = df_con_tech['TECNOLOGIA'].value_counts().head(5).index.tolist()
        heatmap_data = pd.crosstab(
            df_con_tech[df_con_tech['DEPARTAMENTO'].isin(top_10_deptos)]['DEPARTAMENTO'],
            df_con_tech[df_con_tech['DEPARTAMENTO'].isin(top_10_deptos)]['TECNOLOGIA']
        )
        heatmap_data = heatmap_data[top_5_tech]
        heatmap_data_norm = heatmap_data.div(heatmap_data.sum(axis=1), axis=0) * 100
        
        fig3 = px.imshow(
            heatmap_data_norm,
            labels=dict(x="Tecnología", y="Departamento", color="Porcentaje (%)"),
            title="Distribución Tecnológica por Departamento",
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab2:
        st.markdown("### Análisis por Región")
        
        # Top 3 tecnologías por región
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución de registros por región
            region_counts = df_con_tech['REGION'].value_counts()
            fig4 = px.pie(
                values=region_counts.values,
                names=region_counts.index,
                title='Distribución de Registros por Región',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            # Top tecnología por región
            top_tech_por_region = df_con_tech.groupby('REGION')['TECNOLOGIA'].agg(
                lambda x: x.value_counts().index[0] if len(x) > 0 else 'N/A'
            )
            
            fig5 = px.bar(
                x=top_tech_por_region.index,
                y=[1]*len(top_tech_por_region),
                text=top_tech_por_region.values,
                title='Tecnología Principal por Región',
                labels={'x': 'Región', 'y': ''}
            )
            fig5.update_traces(textposition='inside')
            fig5.update_yaxes(showticklabels=False)
            st.plotly_chart(fig5, use_container_width=True)
        
        # Top 3 por región - barras agrupadas
        st.markdown("#### Top 3 Tecnologías por Región")
        
        top_tech_region_data = []
        for region in df_con_tech['REGION'].unique():
            df_region = df_con_tech[df_con_tech['REGION'] == region]
            top_3 = df_region['TECNOLOGIA'].value_counts().head(3)
            for tech, count in top_3.items():
                pct = (count / len(df_region) * 100)
                top_tech_region_data.append({
                    'Región': region,
                    'Tecnología': tech,
                    'Porcentaje': pct
                })
        
        top_tech_region_df = pd.DataFrame(top_tech_region_data)
        
        fig6 = px.bar(
            top_tech_region_df,
            x='Porcentaje',
            y='Región',
            color='Tecnología',
            orientation='h',
            title='Top 3 Tecnologías por Región',
            barmode='group'
        )
        fig6.update_layout(height=500)
        st.plotly_chart(fig6, use_container_width=True)
    
    with tab3:
        st.markdown("### Diversidad Tecnológica")
        
        # Diversidad por departamento
        diversidad = df_con_tech.groupby('DEPARTAMENTO')['TECNOLOGIA'].nunique().sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 15 departamentos con mayor diversidad
            top_15_div = diversidad.head(15)
            fig7 = px.bar(
                x=top_15_div.values,
                y=top_15_div.index,
                orientation='h',
                title='Top 15 Departamentos - Diversidad Tecnológica',
                labels={'x': 'Número de Tecnologías Diferentes', 'y': 'Departamento'},
                color=top_15_div.values,
                color_continuous_scale='Viridis'
            )
            fig7.update_layout(showlegend=False, height=600)
            st.plotly_chart(fig7, use_container_width=True)
        
        with col2:
            # Correlación: registros vs diversidad
            div_registros = df_con_tech.groupby('DEPARTAMENTO').agg({
                'TECNOLOGIA': 'nunique',
                'MUNICIPIO': 'size'
            }).reset_index()
            div_registros.columns = ['Departamento', 'N_Tecnologias', 'N_Registros']
            
            fig8 = px.scatter(
                div_registros,
                x='N_Registros',
                y='N_Tecnologias',
                hover_data=['Departamento'],
                title='Registros vs Diversidad Tecnológica',
                labels={
                    'N_Registros': 'Número de Registros',
                    'N_Tecnologias': 'Número de Tecnologías'
                },
                trendline='ols'
            )
            fig8.update_layout(height=600)
            st.plotly_chart(fig8, use_container_width=True)
        
        # Tabla de diversidad
        with st.expander("📋 Ver Ranking Completo de Diversidad"):
            div_completa = df_con_tech.groupby('DEPARTAMENTO').agg({
                'TECNOLOGIA': 'nunique',
                'MUNICIPIO': 'nunique',
                'CANTIDAD_LINEAS_ACCESOS': 'sum'
            }).reset_index()
            div_completa.columns = ['Departamento', 'N° Tecnologías', 'N° Municipios', 'Total Líneas']
            div_completa = div_completa.sort_values('N° Tecnologías', ascending=False)
            st.dataframe(div_completa, use_container_width=True, hide_index=True, height=400)