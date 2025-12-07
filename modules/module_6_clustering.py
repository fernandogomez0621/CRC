"""
Módulo 6: Análisis de Clustering con Machine Learning
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

def preparar_datos_clustering(df):
    """Prepara los datos para clustering"""
    
    # Agregar características de agregación por operador-tecnología-servicio
    df_agg = df.groupby(['EMPRESA', 'TECNOLOGIA', 'SERVICIO_PAQUETE']).agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum',
        'VELOCIDAD_EFECTIVA_DOWNSTREAM': 'mean',
        'VELOCIDAD_EFECTIVA_UPSTREAM': 'mean',
        'DEPARTAMENTO': 'nunique',  # Cobertura geográfica (conteo)
        'MUNICIPIO': 'nunique'       # Cobertura geográfica (conteo)
    }).reset_index()
    
    # Renombrar para claridad
    df_agg.rename(columns={
        'DEPARTAMENTO': 'N_DEPARTAMENTOS',
        'MUNICIPIO': 'N_MUNICIPIOS'
    }, inplace=True)
    
    # Calcular métricas derivadas
    df_agg['VALOR_POR_LINEA'] = df_agg['VALOR_FACTURADO_O_COBRADO'] / df_agg['CANTIDAD_LINEAS_ACCESOS']
    df_agg['RATIO_VELOCIDAD'] = df_agg['VELOCIDAD_EFECTIVA_DOWNSTREAM'] / (df_agg['VELOCIDAD_EFECTIVA_UPSTREAM'] + 1)
    
    # Reemplazar valores infinitos
    df_agg.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_agg.fillna(0, inplace=True)
    
    return df_agg

def show_configuracion_exploración(df):
    """6.1 Configuración y exploración de datos para clustering"""
    st.markdown("## 6.1 🔧 Configuración y Exploración de Datos")
    
    st.markdown("""
    ### 📊 Análisis de Clustering
    
    El clustering permite identificar **grupos naturales** de operadores con características similares
    en términos de tecnología, servicios ofrecidos, cobertura y valores facturados.
    """)
    
    # Preparar datos
    with st.spinner("Preparando datos para clustering..."):
        df_cluster = preparar_datos_clustering(df)
    
    # Información del dataset preparado
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Registros Agregados", f"{len(df_cluster):,}")
    
    with col2:
        st.metric("Operadores Únicos", df['EMPRESA'].nunique())
    
    with col3:
        st.metric("Tecnologías", df['TECNOLOGIA'].nunique())
    
    with col4:
        st.metric("Servicios", df['SERVICIO_PAQUETE'].nunique())
    
    st.markdown("---")
    
    # Selector de variables para clustering
    st.markdown("### 🎯 Selección de Variables")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        variables_disponibles = [
            'CANTIDAD_LINEAS_ACCESOS',
            'VALOR_FACTURADO_O_COBRADO',
            'VELOCIDAD_EFECTIVA_DOWNSTREAM',
            'VELOCIDAD_EFECTIVA_UPSTREAM',
            'N_DEPARTAMENTOS',  # Número de departamentos (cobertura)
            'N_MUNICIPIOS',     # Número de municipios (cobertura)
            'VALOR_POR_LINEA',
            'RATIO_VELOCIDAD'
        ]
        
        variables_seleccionadas = st.multiselect(
            "Seleccione las variables para el análisis:",
            variables_disponibles,
            default=['CANTIDAD_LINEAS_ACCESOS', 'VALOR_FACTURADO_O_COBRADO', 
                     'VELOCIDAD_EFECTIVA_DOWNSTREAM', 'N_DEPARTAMENTOS']
        )
    
    with col2:
        st.info("""
        **Sugerencias:**
        - Mínimo 2 variables
        - Mezclar variables de volumen, valor y cobertura
        - N_DEPARTAMENTOS y N_MUNICIPIOS miden cobertura geográfica
        - VALOR_POR_LINEA normaliza por escala del operador
        """)
    
    if len(variables_seleccionadas) < 2:
        st.warning("⚠️ Seleccione al menos 2 variables para continuar")
        return
    
    # Explicación de variables
    st.markdown("---")
    with st.expander("ℹ️ Descripción de Variables"):
        st.markdown("""
        **Variables Originales:**
        - `CANTIDAD_LINEAS_ACCESOS`: Total de líneas/accesos del operador
        - `VALOR_FACTURADO_O_COBRADO`: Ingresos totales facturados
        - `VELOCIDAD_EFECTIVA_DOWNSTREAM`: Velocidad promedio de bajada (Mbps)
        - `VELOCIDAD_EFECTIVA_UPSTREAM`: Velocidad promedio de subida (Mbps)
        
        **Variables de Cobertura (agregadas):**
        - `N_DEPARTAMENTOS`: Número de departamentos donde opera (diversificación geográfica)
        - `N_MUNICIPIOS`: Número de municipios donde opera (alcance territorial)
        
        **Variables Derivadas:**
        - `VALOR_POR_LINEA`: Ingreso promedio por línea (rentabilidad)
        - `RATIO_VELOCIDAD`: Relación bajada/subida (simetría del servicio)
        """)
    
    
    # Guardar configuración en session_state
    if 'cluster_config' not in st.session_state:
        st.session_state.cluster_config = {}
    
    st.session_state.cluster_config['variables'] = variables_seleccionadas
    st.session_state.cluster_config['df_cluster'] = df_cluster
    
    # Estadísticas de las variables seleccionadas
    st.markdown("### 📈 Estadísticas de Variables Seleccionadas")
    
    stats_df = df_cluster[variables_seleccionadas].describe().T
    stats_df['cv'] = (stats_df['std'] / stats_df['mean'] * 100).round(2)
    
    st.dataframe(stats_df.style.format("{:.2f}"), use_container_width=True)
    
    # Distribuciones
    st.markdown("### 📊 Distribución de Variables")
    
    n_vars = len(variables_seleccionadas)
    n_cols = min(2, n_vars)
    n_rows = (n_vars + 1) // 2
    
    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=variables_seleccionadas
    )
    
    for idx, var in enumerate(variables_seleccionadas):
        row = idx // 2 + 1
        col = idx % 2 + 1
        
        fig.add_trace(
            go.Histogram(x=df_cluster[var], name=var, showlegend=False),
            row=row,
            col=col
        )
    
    fig.update_layout(height=300 * n_rows, title_text="Distribuciones de Variables")
    st.plotly_chart(fig, use_container_width=True)
    
    # Matriz de correlación
    st.markdown("### 🔗 Matriz de Correlación")
    
    corr_matrix = df_cluster[variables_seleccionadas].corr()
    
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig_corr.update_layout(
        title="Matriz de Correlación de Variables",
        height=500
    )
    
    st.plotly_chart(fig_corr, use_container_width=True)

def calcular_elbow_silhouette(X, max_k=10):
    """Calcula métricas para método del codo y silhouette"""
    inertias = []
    silhouettes = []
    calinski = []
    davies = []
    
    K_range = range(2, max_k + 1)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        
        inertias.append(kmeans.inertia_)
        silhouettes.append(silhouette_score(X, labels))
        calinski.append(calinski_harabasz_score(X, labels))
        davies.append(davies_bouldin_score(X, labels))
    
    return {
        'K': list(K_range),
        'inertia': inertias,
        'silhouette': silhouettes,
        'calinski': calinski,
        'davies': davies
    }

def show_analisis_clusters(df):
    """6.2 Análisis y determinación del número óptimo de clusters"""
    st.markdown("## 6.2 🎯 Análisis de Clusters")
    
    # Verificar configuración
    if 'cluster_config' not in st.session_state or 'variables' not in st.session_state.cluster_config:
        st.warning("⚠️ Por favor, configure las variables en la sección 6.1 primero")
        return
    
    df_cluster = st.session_state.cluster_config['df_cluster']
    variables = st.session_state.cluster_config['variables']
    
    # Preparar datos
    X = df_cluster[variables].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Configuración
    col1, col2 = st.columns([1, 3])
    
    with col1:
        max_clusters = st.slider(
            "Número máximo de clusters a evaluar:",
            min_value=5,
            max_value=15,
            value=10,
            step=1
        )
        
        st.markdown("---")
        
        metodo_seleccionado = st.radio(
            "Método de visualización:",
            ["Método del Codo", "Silhouette Score", "Calinski-Harabasz", "Davies-Bouldin", "Todos"]
        )
    
    with col2:
        with st.spinner("Calculando métricas de clustering..."):
            metrics = calcular_elbow_silhouette(X_scaled, max_clusters)
        
        # Crear gráficos según selección
        if metodo_seleccionado == "Todos":
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    'Método del Codo (Inercia)',
                    'Silhouette Score',
                    'Calinski-Harabasz Index',
                    'Davies-Bouldin Index'
                ]
            )
            
            # Inercia
            fig.add_trace(
                go.Scatter(
                    x=metrics['K'],
                    y=metrics['inertia'],
                    mode='lines+markers',
                    name='Inercia',
                    line=dict(color='#2E86AB', width=3)
                ),
                row=1, col=1
            )
            
            # Silhouette
            fig.add_trace(
                go.Scatter(
                    x=metrics['K'],
                    y=metrics['silhouette'],
                    mode='lines+markers',
                    name='Silhouette',
                    line=dict(color='#A23B72', width=3)
                ),
                row=1, col=2
            )
            
            # Calinski
            fig.add_trace(
                go.Scatter(
                    x=metrics['K'],
                    y=metrics['calinski'],
                    mode='lines+markers',
                    name='Calinski-Harabasz',
                    line=dict(color='#2CA02C', width=3)
                ),
                row=2, col=1
            )
            
            # Davies-Bouldin
            fig.add_trace(
                go.Scatter(
                    x=metrics['K'],
                    y=metrics['davies'],
                    mode='lines+markers',
                    name='Davies-Bouldin',
                    line=dict(color='#D62728', width=3)
                ),
                row=2, col=2
            )
            
            fig.update_layout(height=700, showlegend=False, title_text="Métricas de Evaluación de Clusters")
            
        else:
            # Gráfico individual según selección
            metric_map = {
                "Método del Codo": ('inertia', 'Inercia', '#2E86AB'),
                "Silhouette Score": ('silhouette', 'Silhouette Score', '#A23B72'),
                "Calinski-Harabasz": ('calinski', 'Calinski-Harabasz', '#2CA02C'),
                "Davies-Bouldin": ('davies', 'Davies-Bouldin', '#D62728')
            }
            
            metric_key, metric_label, color = metric_map[metodo_seleccionado]
            
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=metrics['K'],
                    y=metrics[metric_key],
                    mode='lines+markers',
                    name=metric_label,
                    line=dict(color=color, width=3),
                    marker=dict(size=10)
                )
            )
            
            fig.update_layout(
                title=f"{metodo_seleccionado}",
                xaxis_title="Número de Clusters",
                yaxis_title=metric_label,
                height=500
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Recomendaciones
    st.markdown("### 💡 Recomendaciones")
    
    # Encontrar k óptimo
    best_silhouette_k = metrics['K'][np.argmax(metrics['silhouette'])]
    best_calinski_k = metrics['K'][np.argmax(metrics['calinski'])]
    best_davies_k = metrics['K'][np.argmin(metrics['davies'])]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Mejor Silhouette", f"{best_silhouette_k} clusters")
    
    with col2:
        st.metric("Mejor Calinski-Harabasz", f"{best_calinski_k} clusters")
    
    with col3:
        st.metric("Mejor Davies-Bouldin", f"{best_davies_k} clusters")
    
    st.info(f"""
    **Interpretación:**
    - **Silhouette Score**: Mayor es mejor (cohesión y separación)
    - **Calinski-Harabasz**: Mayor es mejor (varianza entre clusters)
    - **Davies-Bouldin**: Menor es mejor (similitud entre clusters)
    
    **Recomendación basada en métricas**: Considere entre **{min(best_silhouette_k, best_calinski_k)}** y **{max(best_silhouette_k, best_calinski_k)}** clusters.
    """)
    
    # Selector del número final de clusters
    st.markdown("---")
    st.markdown("### 🎯 Aplicar Clustering")
    
    n_clusters_final = st.slider(
        "Seleccione el número de clusters a generar:",
        min_value=2,
        max_value=max_clusters,
        value=best_silhouette_k,
        step=1
    )
    
    if st.button("🚀 Generar Clusters", type="primary"):
        with st.spinner(f"Generando {n_clusters_final} clusters..."):
            # Aplicar K-means
            kmeans = KMeans(n_clusters=n_clusters_final, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            
            # Agregar labels al dataframe
            df_cluster['Cluster'] = labels
            
            # PCA para visualización
            pca_2d = PCA(n_components=2)
            pca_3d = PCA(n_components=3)
            
            X_pca_2d = pca_2d.fit_transform(X_scaled)
            X_pca_3d = pca_3d.fit_transform(X_scaled)
            
            df_cluster['PCA1'] = X_pca_2d[:, 0]
            df_cluster['PCA2'] = X_pca_2d[:, 1]
            df_cluster['PCA3_1'] = X_pca_3d[:, 0]
            df_cluster['PCA3_2'] = X_pca_3d[:, 1]
            df_cluster['PCA3_3'] = X_pca_3d[:, 2]
            
            # Guardar en session_state
            st.session_state.cluster_config['df_clustered'] = df_cluster
            st.session_state.cluster_config['n_clusters'] = n_clusters_final
            st.session_state.cluster_config['pca_2d_var'] = pca_2d.explained_variance_ratio_
            st.session_state.cluster_config['pca_3d_var'] = pca_3d.explained_variance_ratio_
            st.session_state.cluster_config['kmeans'] = kmeans
            st.session_state.cluster_config['scaler'] = scaler
            
            # Métricas finales
            silhouette_final = silhouette_score(X_scaled, labels)
            calinski_final = calinski_harabasz_score(X_scaled, labels)
            davies_final = davies_bouldin_score(X_scaled, labels)
            
            st.success(f"✅ {n_clusters_final} clusters generados exitosamente!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Silhouette Score", f"{silhouette_final:.3f}")
            with col2:
                st.metric("Calinski-Harabasz", f"{calinski_final:.1f}")
            with col3:
                st.metric("Davies-Bouldin", f"{davies_final:.3f}")
            
            st.info("📊 Vaya a la sección **6.3 Perfiles y Patrones** para explorar los clusters generados.")

def show_perfiles_patrones(df):
    """6.3 Visualización y análisis de perfiles de clusters"""
    st.markdown("## 6.3 📊 Perfiles y Patrones de Clusters")
    
    # Verificar que se hayan generado clusters
    if 'cluster_config' not in st.session_state or 'df_clustered' not in st.session_state.cluster_config:
        st.warning("⚠️ Por favor, genere los clusters en la sección 6.2 primero")
        return
    
    df_cluster = st.session_state.cluster_config['df_clustered']
    n_clusters = st.session_state.cluster_config['n_clusters']
    variables = st.session_state.cluster_config['variables']
    pca_2d_var = st.session_state.cluster_config['pca_2d_var']
    pca_3d_var = st.session_state.cluster_config['pca_3d_var']
    
    # Resumen de clusters
    st.markdown("### 📈 Resumen de Clusters")
    
    cluster_summary = df_cluster.groupby('Cluster').agg({
        'CANTIDAD_LINEAS_ACCESOS': ['sum', 'mean'],
        'VALOR_FACTURADO_O_COBRADO': ['sum', 'mean'],
        'EMPRESA': 'count'
    }).round(2)
    
    cluster_summary.columns = ['Total Líneas', 'Prom Líneas', 'Total Valor', 'Prom Valor', 'N° Registros']
    
    st.dataframe(cluster_summary.style.format({
        'Total Líneas': '{:,.0f}',
        'Prom Líneas': '{:,.2f}',
        'Total Valor': '${:,.0f}',
        'Prom Valor': '${:,.2f}',
        'N° Registros': '{:.0f}'
    }), use_container_width=True)
    
    # Visualizaciones
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Visualización PCA", "📊 Características", "🔍 Detalle por Cluster", "📥 Exportar"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # PCA 2D
            fig_2d = px.scatter(
                df_cluster,
                x='PCA1',
                y='PCA2',
                color='Cluster',
                hover_data=['EMPRESA', 'TECNOLOGIA', 'SERVICIO_PAQUETE'],
                title=f'Visualización PCA 2D - {n_clusters} Clusters',
                labels={
                    'PCA1': f'PC1 ({pca_2d_var[0]:.1%} var)',
                    'PCA2': f'PC2 ({pca_2d_var[1]:.1%} var)'
                },
                color_continuous_scale='Viridis'
            )
            fig_2d.update_layout(height=500)
            st.plotly_chart(fig_2d, use_container_width=True)
        
        with col2:
            # PCA 3D
            fig_3d = px.scatter_3d(
                df_cluster,
                x='PCA3_1',
                y='PCA3_2',
                z='PCA3_3',
                color='Cluster',
                hover_data=['EMPRESA', 'TECNOLOGIA'],
                title=f'Visualización PCA 3D - {n_clusters} Clusters',
                labels={
                    'PCA3_1': f'PC1 ({pca_3d_var[0]:.1%})',
                    'PCA3_2': f'PC2 ({pca_3d_var[1]:.1%})',
                    'PCA3_3': f'PC3 ({pca_3d_var[2]:.1%})'
                },
                color_continuous_scale='Viridis'
            )
            fig_3d.update_layout(height=500)
            st.plotly_chart(fig_3d, use_container_width=True)
    
    with tab2:
        # Características promedio por cluster
        st.markdown("### 📊 Características Promedio por Cluster")
        
        # Seleccionar variables numéricas
        numeric_cols = df_cluster[variables].select_dtypes(include=[np.number]).columns
        
        cluster_means = df_cluster.groupby('Cluster')[numeric_cols].mean()
        
        # Normalizar para comparación
        cluster_means_norm = (cluster_means - cluster_means.min()) / (cluster_means.max() - cluster_means.min())
        
        # Gráfico de radar
        fig_radar = go.Figure()
        
        for cluster_id in range(n_clusters):
            fig_radar.add_trace(go.Scatterpolar(
                r=cluster_means_norm.loc[cluster_id].values,
                theta=cluster_means_norm.columns,
                fill='toself',
                name=f'Cluster {cluster_id}'
            ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title="Perfil de Características (Normalizado)",
            height=600
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Heatmap de características
        fig_heat = go.Figure(data=go.Heatmap(
            z=cluster_means.T.values,
            x=[f'Cluster {i}' for i in range(n_clusters)],
            y=cluster_means.columns,
            colorscale='RdYlBu_r',
            text=cluster_means.T.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        
        fig_heat.update_layout(
            title="Heatmap de Características por Cluster",
            height=400
        )
        
        st.plotly_chart(fig_heat, use_container_width=True)
    
    with tab3:
        # Detalle por cluster seleccionado
        st.markdown("### 🔍 Explorar Cluster Individual")
        
        cluster_selected = st.selectbox(
            "Seleccione un cluster:",
            range(n_clusters),
            format_func=lambda x: f"Cluster {x}"
        )
        
        df_cluster_sel = df_cluster[df_cluster['Cluster'] == cluster_selected]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Registros", len(df_cluster_sel))
        
        with col2:
            st.metric("Total Líneas", f"{df_cluster_sel['CANTIDAD_LINEAS_ACCESOS'].sum():,.0f}")
        
        with col3:
            st.metric("Total Valor", f"${df_cluster_sel['VALOR_FACTURADO_O_COBRADO'].sum():,.0f}")
        
        # Top operadores en este cluster
        st.markdown("#### 🏢 Top 10 Operadores")
        top_ops = df_cluster_sel['EMPRESA'].value_counts().head(10)
        
        fig_ops = px.bar(
            x=top_ops.values,
            y=[op[:40] for op in top_ops.index],
            orientation='h',
            title=f'Top 10 Operadores en Cluster {cluster_selected}',
            labels={'x': 'Frecuencia', 'y': 'Operador'}
        )
        fig_ops.update_layout(height=400)
        st.plotly_chart(fig_ops, use_container_width=True)
        
        # Distribución de tecnologías
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📡 Tecnologías")
            tech_dist = df_cluster_sel['TECNOLOGIA'].value_counts()
            fig_tech = px.pie(
                values=tech_dist.values,
                names=tech_dist.index,
                title='Distribución de Tecnologías'
            )
            st.plotly_chart(fig_tech, use_container_width=True)
        
        with col2:
            st.markdown("#### 📦 Servicios")
            serv_dist = df_cluster_sel['SERVICIO_PAQUETE'].value_counts()
            fig_serv = px.pie(
                values=serv_dist.values,
                names=serv_dist.index,
                title='Distribución de Servicios'
            )
            st.plotly_chart(fig_serv, use_container_width=True)
    
    with tab4:
        # Exportación
        st.markdown("### 📥 Exportar Resultados")
        
        st.markdown("""
        Descargue los resultados del clustering en formato CSV para análisis adicional.
        """)
        
        # Preparar CSV
        df_export = df_cluster[['EMPRESA', 'TECNOLOGIA', 'SERVICIO_PAQUETE', 'Cluster'] + variables]
        
        csv = df_export.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="⬇️ Descargar Resultados CSV",
            data=csv,
            file_name=f"clustering_resultados_{n_clusters}_clusters.csv",
            mime="text/csv"
        )
        
        # Resumen para exportar
        summary_csv = cluster_summary.to_csv(encoding='utf-8-sig')
        
        st.download_button(
            label="⬇️ Descargar Resumen de Clusters",
            data=summary_csv,
            file_name=f"clustering_resumen_{n_clusters}_clusters.csv",
            mime="text/csv"
        )
        
        st.success("✅ Archivos listos para descargar")