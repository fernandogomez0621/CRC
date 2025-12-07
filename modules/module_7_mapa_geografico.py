"""
Módulo 7: Visualización Geográfica con Mapas de Colombia
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Coordenadas aproximadas de los departamentos de Colombia (centroides)
COORDS_DEPARTAMENTOS = {
    'AMAZONAS': {'lat': -1.44, 'lon': -71.94},
    'ANTIOQUIA': {'lat': 6.25, 'lon': -75.56},
    'ARAUCA': {'lat': 7.08, 'lon': -70.76},
    'ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA': {'lat': 12.58, 'lon': -81.70},
    'ATLÁNTICO': {'lat': 10.70, 'lon': -74.92},
    'BOGOTÁ D.C.': {'lat': 4.71, 'lon': -74.07},
    'BOLÍVAR': {'lat': 8.67, 'lon': -74.03},
    'BOYACÁ': {'lat': 5.45, 'lon': -73.36},
    'CALDAS': {'lat': 5.29, 'lon': -75.25},
    'CAQUETA': {'lat': 0.87, 'lon': -73.84},
    'CASANARE': {'lat': 5.76, 'lon': -71.57},
    'CAUCA': {'lat': 2.70, 'lon': -76.82},
    'CESAR': {'lat': 9.33, 'lon': -73.65},
    'CHOCÓ': {'lat': 5.25, 'lon': -76.82},
    'CÓRDOBA': {'lat': 8.05, 'lon': -75.57},
    'CUNDINAMARCA': {'lat': 5.02, 'lon': -74.03},
    'GUAINÍA': {'lat': 2.58, 'lon': -68.52},
    'GUAVIARE': {'lat': 1.91, 'lon': -72.64},
    'HUILA': {'lat': 2.54, 'lon': -75.78},
    'LA GUAJIRA': {'lat': 11.35, 'lon': -72.52},
    'MAGDALENA': {'lat': 10.41, 'lon': -74.41},
    'META': {'lat': 3.30, 'lon': -73.28},
    'NARIÑO': {'lat': 1.29, 'lon': -77.35},
    'NORTE DE SANTANDER': {'lat': 7.94, 'lon': -72.90},
    'PUTUMAYO': {'lat': 0.49, 'lon': -75.52},
    'QUINDÍO': {'lat': 4.46, 'lon': -75.67},
    'RISARALDA': {'lat': 5.31, 'lon': -75.99},
    'SANTANDER': {'lat': 6.64, 'lon': -73.65},
    'SUCRE': {'lat': 8.81, 'lon': -74.72},
    'TOLIMA': {'lat': 4.09, 'lon': -75.15},
    'VALLE DEL CAUCA': {'lat': 3.80, 'lon': -76.64},
    'VAUPÉS': {'lat': 0.85, 'lon': -70.81},
    'VICHADA': {'lat': 4.42, 'lon': -69.29}
}

def agregar_coordenadas(df):
    """Agrega coordenadas geográficas al dataframe"""
    df_map = df.copy()
    
    # Normalizar nombres de departamentos
    df_map['DEPARTAMENTO'] = df_map['DEPARTAMENTO'].str.upper().str.strip()
    
    # Agregar coordenadas
    df_map['lat'] = df_map['DEPARTAMENTO'].map(lambda x: COORDS_DEPARTAMENTOS.get(x, {}).get('lat'))
    df_map['lon'] = df_map['DEPARTAMENTO'].map(lambda x: COORDS_DEPARTAMENTOS.get(x, {}).get('lon'))
    
    # Filtrar registros sin coordenadas
    df_map = df_map.dropna(subset=['lat', 'lon'])
    
    return df_map

def show_mapa_cobertura(df):
    """7.1 Mapa de cobertura por departamento"""
    st.markdown("## 7.1 🗺️ Mapa de Cobertura por Departamento")
    
    st.markdown("""
    Visualización geográfica de la cobertura de servicios fijos en Colombia.
    El tamaño de los círculos representa el número de líneas/accesos por departamento.
    """)
    
    # Preparar datos agregados por departamento
    df_dept = df.groupby('DEPARTAMENTO').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum',
        'EMPRESA': 'nunique',
        'MUNICIPIO': 'nunique'
    }).reset_index()
    
    df_dept.columns = ['DEPARTAMENTO', 'Total_Lineas', 'Total_Valor', 'N_Operadores', 'N_Municipios']
    
    # Agregar coordenadas
    df_map = agregar_coordenadas(df_dept)
    
    if len(df_map) == 0:
        st.error("❌ No se pudieron cargar las coordenadas de los departamentos")
        return
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Departamentos", len(df_map))
    
    with col2:
        st.metric("Total Líneas", f"{df_map['Total_Lineas'].sum():,.0f}")
    
    with col3:
        st.metric("Operadores", df['EMPRESA'].nunique())
    
    with col4:
        st.metric("Municipios", df['MUNICIPIO'].nunique())
    
    st.markdown("---")
    
    # Opciones de visualización
    col1, col2 = st.columns([3, 1])
    
    with col2:
        metrica_color = st.selectbox(
            "Colorear por:",
            ['Total_Lineas', 'Total_Valor', 'N_Operadores', 'N_Municipios'],
            format_func=lambda x: {
                'Total_Lineas': '📊 Total Líneas',
                'Total_Valor': '💰 Valor Facturado',
                'N_Operadores': '🏢 N° Operadores',
                'N_Municipios': '🏙️ N° Municipios'
            }[x]
        )
        
        escala_log = st.checkbox("Escala logarítmica", value=False)
    
    with col1:
        # Crear mapa
        fig = px.scatter_geo(
            df_map,
            lat='lat',
            lon='lon',
            size='Total_Lineas',
            color=metrica_color,
            hover_name='DEPARTAMENTO',
            hover_data={
                'Total_Lineas': ':,.0f',
                'Total_Valor': ':$,.0f',
                'N_Operadores': True,
                'N_Municipios': True,
                'lat': False,
                'lon': False
            },
            size_max=50,
            color_continuous_scale='Viridis',
            title='Mapa de Cobertura de Servicios Fijos - Colombia'
        )
        
        # Configurar el mapa centrado en Colombia
        fig.update_geos(
            center=dict(lat=4.5, lon=-74),
            projection_scale=4,
            visible=True,
            showcountries=True,
            countrycolor="lightgray",
            showcoastlines=True,
            coastlinecolor="gray",
            showland=True,
            landcolor="rgb(243, 243, 243)",
            showlakes=True,
            lakecolor="rgb(204, 230, 255)"
        )
        
        if escala_log:
            fig.update_traces(marker=dict(sizemode='diameter'))
        
        fig.update_layout(
            height=600,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Top 10 departamentos
    st.markdown("### 📊 Top 10 Departamentos por Número de Líneas")
    
    top_10 = df_map.nlargest(10, 'Total_Lineas')[['DEPARTAMENTO', 'Total_Lineas', 'Total_Valor', 'N_Operadores', 'N_Municipios']]
    
    fig_bar = px.bar(
        top_10,
        x='Total_Lineas',
        y='DEPARTAMENTO',
        orientation='h',
        title='Top 10 Departamentos',
        color='Total_Lineas',
        color_continuous_scale='Blues',
        hover_data=['Total_Valor', 'N_Operadores']
    )
    
    fig_bar.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Tabla detallada
    with st.expander("📋 Ver Datos Detallados por Departamento"):
        df_display = df_map[['DEPARTAMENTO', 'Total_Lineas', 'Total_Valor', 'N_Operadores', 'N_Municipios']].sort_values('Total_Lineas', ascending=False)
        st.dataframe(df_display.style.format({
            'Total_Lineas': '{:,.0f}',
            'Total_Valor': '${:,.0f}',
            'N_Operadores': '{:.0f}',
            'N_Municipios': '{:.0f}'
        }), use_container_width=True, height=400)

def show_mapa_valor(df):
    """7.2 Mapa de valor facturado por departamento"""
    st.markdown("## 7.2 💰 Mapa de Valor Facturado")
    
    st.markdown("""
    Visualización geográfica del valor total facturado por departamento.
    Los círculos más grandes representan mayor facturación.
    """)
    
    # Preparar datos
    df_dept = df.groupby('DEPARTAMENTO').agg({
        'VALOR_FACTURADO_O_COBRADO': 'sum',
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'EMPRESA': 'nunique'
    }).reset_index()
    
    df_dept.columns = ['DEPARTAMENTO', 'Total_Valor', 'Total_Lineas', 'N_Operadores']
    df_dept['Valor_Por_Linea'] = df_dept['Total_Valor'] / df_dept['Total_Lineas']
    
    # Agregar coordenadas
    df_map = agregar_coordenadas(df_dept)
    
    if len(df_map) == 0:
        st.error("❌ No se pudieron cargar las coordenadas")
        return
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Valor Total", f"${df_map['Total_Valor'].sum()/1e9:.2f}B")
    
    with col2:
        st.metric("Valor Promedio/Depto", f"${df_map['Total_Valor'].mean()/1e6:.2f}M")
    
    with col3:
        st.metric("Valor Prom/Línea", f"${df_map['Valor_Por_Linea'].mean():,.0f}")
    
    st.markdown("---")
    
    # Tabs para diferentes visualizaciones
    tab1, tab2, tab3 = st.tabs(["🗺️ Mapa", "📊 Gráficas", "📈 Comparación"])
    
    with tab1:
        # Mapa de valor total
        fig_map = px.scatter_geo(
            df_map,
            lat='lat',
            lon='lon',
            size='Total_Valor',
            color='Valor_Por_Linea',
            hover_name='DEPARTAMENTO',
            hover_data={
                'Total_Valor': ':$,.0f',
                'Total_Lineas': ':,.0f',
                'Valor_Por_Linea': ':$,.0f',
                'N_Operadores': True,
                'lat': False,
                'lon': False
            },
            size_max=60,
            color_continuous_scale='RdYlGn',
            title='Valor Facturado por Departamento'
        )
        
        fig_map.update_geos(
            center=dict(lat=4.5, lon=-74),
            projection_scale=4,
            visible=True,
            showcountries=True,
            countrycolor="lightgray"
        )
        
        fig_map.update_layout(height=600, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 por valor total
            top_10_valor = df_map.nlargest(10, 'Total_Valor')
            
            fig1 = px.bar(
                top_10_valor,
                x='Total_Valor',
                y='DEPARTAMENTO',
                orientation='h',
                title='Top 10 por Valor Total Facturado',
                color='Total_Valor',
                color_continuous_scale='Blues'
            )
            fig1.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Top 10 por valor por línea
            top_10_vpl = df_map.nlargest(10, 'Valor_Por_Linea')
            
            fig2 = px.bar(
                top_10_vpl,
                x='Valor_Por_Linea',
                y='DEPARTAMENTO',
                orientation='h',
                title='Top 10 por Valor Promedio por Línea',
                color='Valor_Por_Linea',
                color_continuous_scale='Greens'
            )
            fig2.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        # Scatter plot: Líneas vs Valor
        fig_scatter = px.scatter(
            df_map,
            x='Total_Lineas',
            y='Total_Valor',
            size='N_Operadores',
            color='Valor_Por_Linea',
            hover_name='DEPARTAMENTO',
            title='Relación entre Líneas y Valor Facturado',
            labels={
                'Total_Lineas': 'Total de Líneas',
                'Total_Valor': 'Valor Facturado (COP)',
                'Valor_Por_Linea': 'Valor por Línea'
            },
            color_continuous_scale='Viridis'
        )
        
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.info("""
        **Interpretación**: Los departamentos en la parte superior derecha tienen tanto 
        alto número de líneas como alto valor facturado. El color indica el valor promedio 
        por línea (rentabilidad).
        """)

def show_mapa_tecnologias(df):
    """7.3 Mapa de distribución de tecnologías"""
    st.markdown("## 7.3 📡 Mapa de Tecnologías por Departamento")
    
    st.markdown("""
    Visualización de la distribución de tecnologías de acceso en cada departamento.
    """)
    
    # Selector de tecnología - Limpiar nulos y ordenar correctamente
    tecnologias_unicas = df['TECNOLOGIA'].dropna().unique()
    tecnologias_disponibles = sorted([str(t) for t in tecnologias_unicas if pd.notna(t)])
    
    if len(tecnologias_disponibles) == 0:
        st.error("❌ No hay tecnologías disponibles en los datos filtrados")
        return
    
    tecnologia_seleccionada = st.selectbox(
        "Seleccione una tecnología:",
        ['Todas'] + tecnologias_disponibles
    )
    
    # Filtrar por tecnología si se selecciona una específica
    if tecnologia_seleccionada != 'Todas':
        df_filtered = df[df['TECNOLOGIA'] == tecnologia_seleccionada]
    else:
        df_filtered = df
    
    # Preparar datos
    if tecnologia_seleccionada == 'Todas':
        # Mostrar tecnología dominante por departamento
        df_tech = df_filtered.groupby(['DEPARTAMENTO', 'TECNOLOGIA']).agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum'
        }).reset_index()
        
        # Encontrar tecnología dominante
        idx = df_tech.groupby('DEPARTAMENTO')['CANTIDAD_LINEAS_ACCESOS'].idxmax()
        df_dept = df_tech.loc[idx].reset_index(drop=True)
        df_dept.columns = ['DEPARTAMENTO', 'Tecnologia_Dominante', 'Lineas_Tecnologia']
        
        # Agregar total de líneas por departamento
        df_total = df_filtered.groupby('DEPARTAMENTO')['CANTIDAD_LINEAS_ACCESOS'].sum().reset_index()
        df_total.columns = ['DEPARTAMENTO', 'Total_Lineas']
        
        df_dept = df_dept.merge(df_total, on='DEPARTAMENTO')
        df_dept['Porcentaje'] = (df_dept['Lineas_Tecnologia'] / df_dept['Total_Lineas'] * 100).round(2)
    else:
        df_dept = df_filtered.groupby('DEPARTAMENTO').agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum',
            'EMPRESA': 'nunique'
        }).reset_index()
        df_dept.columns = ['DEPARTAMENTO', 'Lineas_Tecnologia', 'N_Operadores']
    
    # Agregar coordenadas
    df_map = agregar_coordenadas(df_dept)
    
    if len(df_map) == 0:
        st.error("❌ No hay datos disponibles para esta selección")
        return
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if tecnologia_seleccionada == 'Todas':
            st.metric("Tecnologías", df['TECNOLOGIA'].nunique())
        else:
            st.metric("Tecnología", tecnologia_seleccionada[:20] + "...")
    
    with col2:
        st.metric("Líneas", f"{df_map['Lineas_Tecnologia'].sum():,.0f}")
    
    with col3:
        st.metric("Departamentos", len(df_map))
    
    st.markdown("---")
    
    # Mapa
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if tecnologia_seleccionada == 'Todas':
            # Mapa coloreado por tecnología dominante
            fig_map = px.scatter_geo(
                df_map,
                lat='lat',
                lon='lon',
                size='Total_Lineas',
                color='Tecnologia_Dominante',
                hover_name='DEPARTAMENTO',
                hover_data={
                    'Tecnologia_Dominante': True,
                    'Lineas_Tecnologia': ':,.0f',
                    'Total_Lineas': ':,.0f',
                    'Porcentaje': ':.1f%',
                    'lat': False,
                    'lon': False
                },
                size_max=50,
                title='Tecnología Dominante por Departamento'
            )
        else:
            # Mapa de líneas con la tecnología específica
            fig_map = px.scatter_geo(
                df_map,
                lat='lat',
                lon='lon',
                size='Lineas_Tecnologia',
                color='Lineas_Tecnologia',
                hover_name='DEPARTAMENTO',
                hover_data={
                    'Lineas_Tecnologia': ':,.0f',
                    'N_Operadores': True,
                    'lat': False,
                    'lon': False
                },
                size_max=50,
                color_continuous_scale='Oranges',
                title=f'Distribución de {tecnologia_seleccionada}'
            )
        
        fig_map.update_geos(
            center=dict(lat=4.5, lon=-74),
            projection_scale=4,
            visible=True,
            showcountries=True,
            countrycolor="lightgray"
        )
        
        fig_map.update_layout(height=600, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Resumen")
        
        if tecnologia_seleccionada == 'Todas':
            tech_counts = df_map['Tecnologia_Dominante'].value_counts()
            
            fig_pie = px.pie(
                values=tech_counts.values,
                names=tech_counts.index,
                title='Tecnologías Dominantes'
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info(f"""
            **{tecnologia_seleccionada}**
            
            - Total líneas: {df_map['Lineas_Tecnologia'].sum():,.0f}
            - Departamentos: {len(df_map)}
            - Mayor presencia: {df_map.nlargest(1, 'Lineas_Tecnologia')['DEPARTAMENTO'].values[0]}
            """)
    
    # Gráfico de barras
    st.markdown("### 📊 Top 15 Departamentos")
    
    top_15 = df_map.nlargest(15, 'Lineas_Tecnologia')
    
    if tecnologia_seleccionada == 'Todas':
        fig_bar = px.bar(
            top_15,
            x='Lineas_Tecnologia',
            y='DEPARTAMENTO',
            orientation='h',
            color='Tecnologia_Dominante',
            title='Top 15 Departamentos por Líneas',
            hover_data=['Porcentaje']
        )
    else:
        fig_bar = px.bar(
            top_15,
            x='Lineas_Tecnologia',
            y='DEPARTAMENTO',
            orientation='h',
            color='Lineas_Tecnologia',
            color_continuous_scale='Oranges',
            title=f'Top 15 Departamentos - {tecnologia_seleccionada}'
        )
    
    fig_bar.update_layout(height=500, showlegend=True if tecnologia_seleccionada == 'Todas' else False)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Matriz de tecnologías por departamento
    with st.expander("🔍 Ver Matriz Completa de Tecnologías"):
        pivot_tech = df.pivot_table(
            index='DEPARTAMENTO',
            columns='TECNOLOGIA',
            values='CANTIDAD_LINEAS_ACCESOS',
            aggfunc='sum',
            fill_value=0
        ).astype(int)
        
        st.dataframe(pivot_tech.style.background_gradient(cmap='YlOrRd', axis=None), 
                     use_container_width=True, height=400)

def show_mapa_empresas(df):
    """7.4 Mapa de presencia de empresas por departamento"""
    st.markdown("## 7.4 🏢 Mapa de Presencia de Empresas")
    
    st.markdown("""
    Busque y visualice la presencia geográfica de operadores específicos en Colombia.
    Puede buscar por nombre o seleccionar de la lista.
    """)
    
    # Obtener lista de empresas ordenada
    empresas_disponibles = sorted(df['EMPRESA'].unique())
    
    # Buscador de empresa
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Input de búsqueda
        busqueda = st.text_input(
            "🔍 Buscar empresa por nombre:",
            placeholder="Ej: COMCEL, ETB, UNE, CLARO..."
        )
        
        # Filtrar empresas según búsqueda
        if busqueda:
            empresas_filtradas = [e for e in empresas_disponibles if busqueda.upper() in e.upper()]
        else:
            empresas_filtradas = empresas_disponibles[:20]  # Mostrar solo las primeras 20
        
        empresa_seleccionada = st.selectbox(
            "Seleccione una empresa:",
            empresas_filtradas,
            help=f"Total de empresas disponibles: {len(empresas_disponibles)}"
        )
    
    with col2:
        st.metric("Total Empresas", len(empresas_disponibles))
        if busqueda:
            st.metric("Resultados", len(empresas_filtradas))
    
    if not empresa_seleccionada:
        st.warning("⚠️ Seleccione una empresa para ver su presencia geográfica")
        return
    
    # Filtrar datos de la empresa seleccionada
    df_empresa = df[df['EMPRESA'] == empresa_seleccionada]
    
    if len(df_empresa) == 0:
        st.error("❌ No se encontraron datos para esta empresa")
        return
    
    # Preparar datos por departamento
    df_dept = df_empresa.groupby('DEPARTAMENTO').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum',
        'MUNICIPIO': 'nunique',
        'TECNOLOGIA': lambda x: ', '.join(x.unique()[:3])  # Top 3 tecnologías
    }).reset_index()
    
    df_dept.columns = ['DEPARTAMENTO', 'Total_Lineas', 'Total_Valor', 'N_Municipios', 'Tecnologias']
    
    # Agregar coordenadas
    df_map = agregar_coordenadas(df_dept)
    
    if len(df_map) == 0:
        st.error("❌ No se pudieron cargar las coordenadas")
        return
    
    st.markdown("---")
    
    # Métricas de la empresa
    st.markdown(f"### 📊 Resumen: {empresa_seleccionada[:60]}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Departamentos", len(df_map))
    
    with col2:
        st.metric("Municipios", df_empresa['MUNICIPIO'].nunique())
    
    with col3:
        st.metric("Total Líneas", f"{df_map['Total_Lineas'].sum():,.0f}")
    
    with col4:
        st.metric("Valor Total", f"${df_map['Total_Valor'].sum()/1e9:.2f}B")
    
    st.markdown("---")
    
    # Tabs de visualización
    tab1, tab2, tab3 = st.tabs(["🗺️ Mapa de Presencia", "📊 Análisis por Región", "📈 Detalles"])
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Mapa de presencia
            fig_map = px.scatter_geo(
                df_map,
                lat='lat',
                lon='lon',
                size='Total_Lineas',
                color='Total_Valor',
                hover_name='DEPARTAMENTO',
                hover_data={
                    'Total_Lineas': ':,.0f',
                    'Total_Valor': ':$,.0f',
                    'N_Municipios': True,
                    'Tecnologias': True,
                    'lat': False,
                    'lon': False
                },
                size_max=60,
                color_continuous_scale='Reds',
                title=f'Presencia de {empresa_seleccionada[:40]} en Colombia'
            )
            
            fig_map.update_geos(
                center=dict(lat=4.5, lon=-74),
                projection_scale=4,
                visible=True,
                showcountries=True,
                countrycolor="lightgray",
                showland=True,
                landcolor="rgb(250, 250, 250)"
            )
            
            fig_map.update_layout(height=600, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_map, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Cobertura")
            
            cobertura_pct = (len(df_map) / 33) * 100
            
            st.metric("% Departamentos", f"{cobertura_pct:.1f}%")
            
            # Top 3 departamentos
            st.markdown("#### Top 3 Deptos")
            top_3 = df_map.nlargest(3, 'Total_Lineas')
            for i, row in top_3.iterrows():
                st.write(f"**{row['DEPARTAMENTO']}**")
                st.write(f"↳ {row['Total_Lineas']:,.0f} líneas")
                st.write(f"↳ {row['N_Municipios']} municipios")
                st.markdown("---")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras: Líneas por departamento
            fig_bar1 = px.bar(
                df_map.nlargest(15, 'Total_Lineas'),
                x='Total_Lineas',
                y='DEPARTAMENTO',
                orientation='h',
                title='Top 15 Departamentos por Líneas',
                color='Total_Lineas',
                color_continuous_scale='Blues'
            )
            fig_bar1.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig_bar1, use_container_width=True)
        
        with col2:
            # Gráfico de barras: Valor por departamento
            fig_bar2 = px.bar(
                df_map.nlargest(15, 'Total_Valor'),
                x='Total_Valor',
                y='DEPARTAMENTO',
                orientation='h',
                title='Top 15 Departamentos por Valor',
                color='Total_Valor',
                color_continuous_scale='Greens'
            )
            fig_bar2.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig_bar2, use_container_width=True)
        
        # Distribución de tecnologías
        st.markdown("### 📡 Tecnologías Utilizadas")
        
        tech_dist = df_empresa['TECNOLOGIA'].value_counts().head(10)
        
        fig_tech = px.bar(
            x=tech_dist.values,
            y=tech_dist.index,
            orientation='h',
            title='Top 10 Tecnologías',
            color=tech_dist.values,
            color_continuous_scale='Oranges'
        )
        fig_tech.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_tech, use_container_width=True)
    
    with tab3:
        # Tabla detallada
        st.markdown("### 📋 Detalle por Departamento")
        
        df_display = df_map[['DEPARTAMENTO', 'Total_Lineas', 'Total_Valor', 'N_Municipios', 'Tecnologias']].sort_values('Total_Lineas', ascending=False)
        
        st.dataframe(df_display.style.format({
            'Total_Lineas': '{:,.0f}',
            'Total_Valor': '${:,.0f}',
            'N_Municipios': '{:.0f}'
        }), use_container_width=True, height=400)
        
        # Botón de descarga
        csv = df_display.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="⬇️ Descargar Datos CSV",
            data=csv,
            file_name=f"presencia_{empresa_seleccionada.replace(' ', '_')[:30]}.csv",
            mime="text/csv"
        )
        
        # Análisis de servicios
        st.markdown("### 📦 Distribución de Servicios")
        
        serv_dist = df_empresa['SERVICIO_PAQUETE'].value_counts()
        
        fig_serv = px.pie(
            values=serv_dist.values,
            names=serv_dist.index,
            title='Servicios Ofrecidos'
        )
        fig_serv.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_serv, use_container_width=True)