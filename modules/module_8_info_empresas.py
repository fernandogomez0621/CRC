"""
Módulo 8: Información Detallada de Empresas
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Coordenadas de departamentos (copiadas del módulo 7)
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
    df_map['DEPARTAMENTO'] = df_map['DEPARTAMENTO'].str.upper().str.strip()
    df_map['lat'] = df_map['DEPARTAMENTO'].map(lambda x: COORDS_DEPARTAMENTOS.get(x, {}).get('lat'))
    df_map['lon'] = df_map['DEPARTAMENTO'].map(lambda x: COORDS_DEPARTAMENTOS.get(x, {}).get('lon'))
    df_map = df_map.dropna(subset=['lat', 'lon'])
    return df_map

def show_busqueda_empresa(df):
    """8.1 Búsqueda y análisis detallado de una empresa"""
    st.markdown("## 8.1 🔍 Búsqueda de Empresa")
    
    st.markdown("""
    Busque un operador específico para ver su análisis completo: cobertura, servicios, 
    tecnologías, evolución temporal y métricas financieras.
    """)
    
    # Búsqueda de empresa
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Obtener top 100 empresas por valor facturado (ordenadas de mayor a menor)
        top_empresas_por_valor = df.groupby('EMPRESA')['VALOR_FACTURADO_O_COBRADO'].sum().nlargest(100)
        empresas_top_100 = top_empresas_por_valor.index.tolist()  # Ya vienen ordenadas
        
        # Todas las empresas disponibles (para referencia)
        total_empresas = df['EMPRESA'].nunique()
        
        # Buscador mejorado
        busqueda = st.text_input(
            "🔍 Buscar empresa:",
            placeholder="Escriba el nombre de la empresa (ej: COMCEL, UNE, CLARO, ETB)...",
            help="La búsqueda no distingue mayúsculas/minúsculas"
        )
        
        # Filtrar empresas
        if busqueda and len(busqueda) >= 2:
            busqueda_upper = busqueda.upper()
            empresas_filtradas = [e for e in empresas_top_100 if busqueda_upper in str(e).upper()]
            
            if len(empresas_filtradas) == 0:
                st.warning(f"⚠️ No se encontraron empresas con '{busqueda}' en el Top 100 por valor facturado")
                st.info("💡 Intente con términos más cortos o revise la ortografía")
                return
        else:
            # Mostrar las top 100 por valor facturado
            empresas_filtradas = empresas_top_100
        
        # Mostrar cuántas opciones hay
        opciones_text = f"Top 100 por valor facturado" if not busqueda else f"{len(empresas_filtradas)} empresas encontradas"
        
        empresa_seleccionada = st.selectbox(
            f"Seleccione una empresa ({opciones_text}):",
            empresas_filtradas,
            help=f"Empresas ordenadas por valor facturado (mayor a menor). Total: {total_empresas}"
        )
    
    with col2:
        st.metric("Total Empresas", total_empresas)
        if busqueda and len(busqueda) >= 2:
            st.metric("Encontradas", len(empresas_filtradas))
        else:
            st.metric("Top por Valor", 100)
    
    if not empresa_seleccionada:
        return
    
    # Filtrar datos de la empresa
    df_empresa = df[df['EMPRESA'] == empresa_seleccionada]
    
    st.markdown("---")
    st.markdown(f"## 📊 {empresa_seleccionada}")
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Departamentos", df_empresa['DEPARTAMENTO'].nunique())
    
    with col2:
        st.metric("Municipios", df_empresa['MUNICIPIO'].nunique())
    
    with col3:
        total_lineas = df_empresa['CANTIDAD_LINEAS_ACCESOS'].sum()
        st.metric("Total Líneas", f"{total_lineas:,.0f}")
    
    with col4:
        total_valor = df_empresa['VALOR_FACTURADO_O_COBRADO'].sum()
        st.metric("Valor Total", f"${total_valor/1e9:.2f}B")
    
    with col5:
        valor_promedio = total_valor / total_lineas if total_lineas > 0 else 0
        st.metric("$/Línea Prom", f"${valor_promedio:,.0f}")
    
    st.markdown("---")
    
    # Tabs de información
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ Mapa", "📍 Cobertura", "📡 Tecnologías", "📦 Servicios", "📈 Evolución"])
    
    with tab1:
        # Mapa geográfico de presencia
        st.markdown("### 🗺️ Presencia Geográfica")
        
        # Preparar datos por departamento
        df_dept = df_empresa.groupby('DEPARTAMENTO').agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum',
            'VALOR_FACTURADO_O_COBRADO': 'sum',
            'MUNICIPIO': 'nunique'
        }).reset_index()
        
        df_dept.columns = ['DEPARTAMENTO', 'Total_Lineas', 'Total_Valor', 'N_Municipios']
        
        # Agregar coordenadas
        df_map = agregar_coordenadas(df_dept)
        
        if len(df_map) > 0:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Mapa
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
                        'lat': False,
                        'lon': False
                    },
                    size_max=60,
                    color_continuous_scale='Reds',
                    title=f'Presencia de {empresa_seleccionada[:50]}'
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
                st.markdown("### 🎯 Cobertura")
                cobertura_pct = (len(df_map) / 33) * 100
                st.metric("% Deptos", f"{cobertura_pct:.1f}%")
                
                st.markdown("#### Top 5")
                top_5 = df_map.nlargest(5, 'Total_Lineas')
                for idx, (i, row) in enumerate(top_5.iterrows(), 1):
                    st.write(f"**{idx}. {row['DEPARTAMENTO']}**")
                    st.write(f"   {row['Total_Lineas']:,.0f} líneas")
        else:
            st.warning("⚠️ No se pudieron cargar coordenadas geográficas")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top departamentos
            dept_data = df_empresa.groupby('DEPARTAMENTO').agg({
                'CANTIDAD_LINEAS_ACCESOS': 'sum',
                'VALOR_FACTURADO_O_COBRADO': 'sum'
            }).reset_index().sort_values('CANTIDAD_LINEAS_ACCESOS', ascending=False).head(15)
            
            fig1 = px.bar(
                dept_data,
                x='CANTIDAD_LINEAS_ACCESOS',
                y='DEPARTAMENTO',
                orientation='h',
                title='Top 15 Departamentos por Líneas',
                color='CANTIDAD_LINEAS_ACCESOS',
                color_continuous_scale='Blues'
            )
            fig1.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Top municipios
            mun_data = df_empresa.groupby('MUNICIPIO').agg({
                'CANTIDAD_LINEAS_ACCESOS': 'sum'
            }).reset_index().sort_values('CANTIDAD_LINEAS_ACCESOS', ascending=False).head(15)
            
            fig2 = px.bar(
                mun_data,
                x='CANTIDAD_LINEAS_ACCESOS',
                y='MUNICIPIO',
                orientation='h',
                title='Top 15 Municipios por Líneas',
                color='CANTIDAD_LINEAS_ACCESOS',
                color_continuous_scale='Greens'
            )
            fig2.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Mapa de regiones
        st.markdown("### 🗺️ Distribución por Región")
        region_data = df_empresa.groupby('REGION').agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum',
            'VALOR_FACTURADO_O_COBRADO': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_region1 = px.pie(
                region_data,
                values='CANTIDAD_LINEAS_ACCESOS',
                names='REGION',
                title='Distribución de Líneas por Región'
            )
            st.plotly_chart(fig_region1, use_container_width=True)
        
        with col2:
            fig_region2 = px.pie(
                region_data,
                values='VALOR_FACTURADO_O_COBRADO',
                names='REGION',
                title='Distribución de Valor por Región'
            )
            st.plotly_chart(fig_region2, use_container_width=True)
    
    with tab3:
        # Análisis de tecnologías
        tech_data = df_empresa.groupby('TECNOLOGIA').agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum',
            'VELOCIDAD_EFECTIVA_DOWNSTREAM': 'mean',
            'VELOCIDAD_EFECTIVA_UPSTREAM': 'mean'
        }).reset_index().sort_values('CANTIDAD_LINEAS_ACCESOS', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras de tecnologías
            fig_tech1 = px.bar(
                tech_data.head(10),
                x='CANTIDAD_LINEAS_ACCESOS',
                y='TECNOLOGIA',
                orientation='h',
                title='Top 10 Tecnologías por Líneas',
                color='CANTIDAD_LINEAS_ACCESOS',
                color_continuous_scale='Oranges'
            )
            fig_tech1.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig_tech1, use_container_width=True)
        
        with col2:
            # Pie chart de tecnologías
            fig_tech2 = px.pie(
                tech_data.head(8),
                values='CANTIDAD_LINEAS_ACCESOS',
                names='TECNOLOGIA',
                title='Distribución Top 8 Tecnologías'
            )
            fig_tech2.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_tech2, use_container_width=True)
        
        # Tabla de velocidades por tecnología
        st.markdown("### 📊 Velocidades Promedio por Tecnología")
        
        tech_display = tech_data[['TECNOLOGIA', 'CANTIDAD_LINEAS_ACCESOS', 
                                   'VELOCIDAD_EFECTIVA_DOWNSTREAM', 'VELOCIDAD_EFECTIVA_UPSTREAM']].copy()
        tech_display.columns = ['Tecnología', 'Líneas', 'Vel. Bajada (Mbps)', 'Vel. Subida (Mbps)']
        
        st.dataframe(tech_display.style.format({
            'Líneas': '{:,.0f}',
            'Vel. Bajada (Mbps)': '{:.2f}',
            'Vel. Subida (Mbps)': '{:.2f}'
        }), use_container_width=True, height=300)
    
    with tab4:
        # Análisis de servicios
        serv_data = df_empresa.groupby('SERVICIO_PAQUETE').agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum',
            'VALOR_FACTURADO_O_COBRADO': 'sum'
        }).reset_index()
        
        serv_data['Valor_Por_Linea'] = serv_data['VALOR_FACTURADO_O_COBRADO'] / serv_data['CANTIDAD_LINEAS_ACCESOS']
        serv_data = serv_data.sort_values('CANTIDAD_LINEAS_ACCESOS', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución de servicios
            fig_serv1 = px.pie(
                serv_data,
                values='CANTIDAD_LINEAS_ACCESOS',
                names='SERVICIO_PAQUETE',
                title='Distribución por Tipo de Servicio/Paquete'
            )
            fig_serv1.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig_serv1, use_container_width=True)
        
        with col2:
            # Valor por línea por servicio
            fig_serv2 = px.bar(
                serv_data,
                x='Valor_Por_Linea',
                y='SERVICIO_PAQUETE',
                orientation='h',
                title='Valor Promedio por Línea según Servicio',
                color='Valor_Por_Linea',
                color_continuous_scale='RdYlGn'
            )
            fig_serv2.update_layout(showlegend=False)
            st.plotly_chart(fig_serv2, use_container_width=True)
        
        # Análisis individual vs empaquetado
        st.markdown("### 📦 Individual vs Empaquetado")
        
        tipo_serv = df_empresa.groupby('TIPO_SERVICIO').agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum',
            'VALOR_FACTURADO_O_COBRADO': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_tipo1 = px.bar(
                tipo_serv,
                x='TIPO_SERVICIO',
                y='CANTIDAD_LINEAS_ACCESOS',
                title='Líneas: Individual vs Empaquetado',
                color='TIPO_SERVICIO',
                color_discrete_map={'Individual': '#2E86AB', 'Empaquetado': '#A23B72'}
            )
            st.plotly_chart(fig_tipo1, use_container_width=True)
        
        with col2:
            fig_tipo2 = px.bar(
                tipo_serv,
                x='TIPO_SERVICIO',
                y='VALOR_FACTURADO_O_COBRADO',
                title='Valor: Individual vs Empaquetado',
                color='TIPO_SERVICIO',
                color_discrete_map={'Individual': '#2E86AB', 'Empaquetado': '#A23B72'}
            )
            st.plotly_chart(fig_tipo2, use_container_width=True)
    
    with tab5:
        # Evolución temporal
        st.markdown("### 📈 Evolución Temporal")
        
        # Crear periodo
        df_empresa['PERIODO'] = df_empresa['ANNO'].astype(str) + '-T' + df_empresa['TRIMESTRE'].astype(str)
        
        evol_data = df_empresa.groupby('PERIODO').agg({
            'CANTIDAD_LINEAS_ACCESOS': 'sum',
            'VALOR_FACTURADO_O_COBRADO': 'sum'
        }).reset_index()
        
        # Ordenar por periodo
        evol_data = evol_data.sort_values('PERIODO')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Evolución de líneas
            fig_evol1 = px.line(
                evol_data,
                x='PERIODO',
                y='CANTIDAD_LINEAS_ACCESOS',
                title='Evolución de Líneas por Trimestre',
                markers=True,
                line_shape='spline'
            )
            fig_evol1.update_traces(line_color='#2E86AB', line_width=3)
            fig_evol1.update_layout(height=400)
            st.plotly_chart(fig_evol1, use_container_width=True)
        
        with col2:
            # Evolución de valor
            fig_evol2 = px.line(
                evol_data,
                x='PERIODO',
                y='VALOR_FACTURADO_O_COBRADO',
                title='Evolución de Valor Facturado por Trimestre',
                markers=True,
                line_shape='spline'
            )
            fig_evol2.update_traces(line_color='#A23B72', line_width=3)
            fig_evol2.update_layout(height=400)
            st.plotly_chart(fig_evol2, use_container_width=True)
        
        # Crecimiento trimestral
        if len(evol_data) > 1:
            evol_data['Crecimiento_Lineas'] = evol_data['CANTIDAD_LINEAS_ACCESOS'].pct_change() * 100
            evol_data['Crecimiento_Valor'] = evol_data['VALOR_FACTURADO_O_COBRADO'].pct_change() * 100
            
            st.markdown("### 📊 Tasa de Crecimiento Trimestral (%)")
            
            fig_crec = go.Figure()
            
            fig_crec.add_trace(go.Bar(
                x=evol_data['PERIODO'],
                y=evol_data['Crecimiento_Lineas'],
                name='Crecimiento Líneas',
                marker_color='#2E86AB'
            ))
            
            fig_crec.add_trace(go.Bar(
                x=evol_data['PERIODO'],
                y=evol_data['Crecimiento_Valor'],
                name='Crecimiento Valor',
                marker_color='#A23B72'
            ))
            
            fig_crec.update_layout(
                barmode='group',
                title='Crecimiento Trimestral',
                yaxis_title='% Crecimiento',
                height=400
            )
            
            st.plotly_chart(fig_crec, use_container_width=True)

def show_comparacion_empresas(df):
    """8.2 Comparación entre múltiples empresas"""
    st.markdown("## 8.2 ⚖️ Comparación de Empresas")
    
    st.markdown("""
    Seleccione hasta 5 empresas para comparar sus métricas lado a lado.
    """)
    
    # Obtener top 100 empresas por valor facturado (ordenadas de mayor a menor)
    top_empresas_por_valor = df.groupby('EMPRESA')['VALOR_FACTURADO_O_COBRADO'].sum().nlargest(100)
    empresas_top_100 = top_empresas_por_valor.index.tolist()  # Ya vienen ordenadas
    
    # Selector múltiple de empresas
    total_empresas = df['EMPRESA'].nunique()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Buscador
        busqueda = st.text_input(
            "🔍 Filtrar empresas:",
            placeholder="Buscar...",
            help="Filtre la lista antes de seleccionar (búsqueda en Top 100 por valor facturado)"
        )
        
        # Filtrar
        if busqueda:
            empresas_filtradas = [e for e in empresas_top_100 if busqueda.upper() in e.upper()]
        else:
            empresas_filtradas = empresas_top_100
        
        empresas_seleccionadas = st.multiselect(
            f"Seleccione empresas a comparar (máx 5) - Top 100 ordenadas por valor:",
            empresas_filtradas,
            max_selections=5,
            help="Las empresas están ordenadas de mayor a menor valor facturado"
        )
    
    with col2:
        st.metric("Total Empresas", total_empresas)
        st.metric("Top 100", len(empresas_top_100))
        if empresas_seleccionadas:
            st.metric("Seleccionadas", len(empresas_seleccionadas))
    
    if len(empresas_seleccionadas) < 2:
        st.info("ℹ️ Seleccione al menos 2 empresas para comparar")
        return
    
    # Filtrar datos
    df_comp = df[df['EMPRESA'].isin(empresas_seleccionadas)]
    
    # Calcular métricas por empresa
    metricas = df_comp.groupby('EMPRESA').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum',
        'DEPARTAMENTO': 'nunique',
        'MUNICIPIO': 'nunique',
        'VELOCIDAD_EFECTIVA_DOWNSTREAM': 'mean',
        'VELOCIDAD_EFECTIVA_UPSTREAM': 'mean'
    }).reset_index()
    
    metricas['Valor_Por_Linea'] = metricas['VALOR_FACTURADO_O_COBRADO'] / metricas['CANTIDAD_LINEAS_ACCESOS']
    metricas.columns = ['Empresa', 'Total_Lineas', 'Total_Valor', 'N_Deptos', 'N_Munis', 
                        'Vel_Bajada', 'Vel_Subida', 'Valor_Por_Linea']
    
    st.markdown("---")
    
    # Tabla comparativa
    st.markdown("### 📊 Tabla Comparativa")
    
    display_metrics = metricas.copy()
    display_metrics['Total_Valor'] = display_metrics['Total_Valor'] / 1e9  # En miles de millones
    
    st.dataframe(display_metrics.style.format({
        'Total_Lineas': '{:,.0f}',
        'Total_Valor': '${:.2f}B',
        'N_Deptos': '{:.0f}',
        'N_Munis': '{:.0f}',
        'Vel_Bajada': '{:.2f} Mbps',
        'Vel_Subida': '{:.2f} Mbps',
        'Valor_Por_Linea': '${:,.0f}'
    }).background_gradient(cmap='YlGnBu', subset=['Total_Lineas', 'Total_Valor']),
    use_container_width=True)
    
    st.markdown("---")
    
    # Gráficos comparativos
    tab1, tab2, tab3 = st.tabs(["📊 Volumen", "💰 Financiero", "🌐 Cobertura"])
    
    with tab1:
        # Comparación de líneas
        fig1 = px.bar(
            metricas,
            x='Empresa',
            y='Total_Lineas',
            title='Comparación de Total de Líneas',
            color='Total_Lineas',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Comparación de velocidades
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=metricas['Empresa'],
            y=metricas['Vel_Bajada'],
            name='Velocidad Bajada',
            marker_color='#2E86AB'
        ))
        fig2.add_trace(go.Bar(
            x=metricas['Empresa'],
            y=metricas['Vel_Subida'],
            name='Velocidad Subida',
            marker_color='#A23B72'
        ))
        fig2.update_layout(
            barmode='group',
            title='Comparación de Velocidades Promedio (Mbps)',
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Valor total
            fig3 = px.bar(
                metricas,
                x='Empresa',
                y='Total_Valor',
                title='Comparación de Valor Total Facturado',
                color='Total_Valor',
                color_continuous_scale='Greens'
            )
            fig3.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Valor por línea
            fig4 = px.bar(
                metricas,
                x='Empresa',
                y='Valor_Por_Linea',
                title='Valor Promedio por Línea',
                color='Valor_Por_Linea',
                color_continuous_scale='RdYlGn'
            )
            fig4.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig4, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Cobertura departamental
            fig5 = px.bar(
                metricas,
                x='Empresa',
                y='N_Deptos',
                title='Número de Departamentos',
                color='N_Deptos',
                color_continuous_scale='Oranges'
            )
            fig5.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig5, use_container_width=True)
        
        with col2:
            # Cobertura municipal
            fig6 = px.bar(
                metricas,
                x='Empresa',
                y='N_Munis',
                title='Número de Municipios',
                color='N_Munis',
                color_continuous_scale='Purples'
            )
            fig6.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig6, use_container_width=True)

def show_ranking_empresas(df):
    """8.3 Ranking de empresas por diferentes métricas"""
    st.markdown("## 8.3 🏆 Ranking de Empresas")
    
    st.markdown("""
    Rankings de los principales operadores según diferentes criterios.
    """)
    
    # Selector de métrica para ranking
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        metrica_ranking = st.selectbox(
            "Seleccione métrica para ranking:",
            [
                'Total de Líneas',
                'Valor Facturado',
                'Valor por Línea',
                'Cobertura Departamental',
                'Cobertura Municipal',
                'Velocidad Promedio'
            ]
        )
    
    with col2:
        top_n = st.slider("Top N empresas:", 5, 50, 20, 5)
    
    with col3:
        mostrar_valores = st.checkbox("Mostrar valores", value=True)
    
    # Calcular métricas
    ranking_data = df.groupby('EMPRESA').agg({
        'CANTIDAD_LINEAS_ACCESOS': 'sum',
        'VALOR_FACTURADO_O_COBRADO': 'sum',
        'DEPARTAMENTO': 'nunique',
        'MUNICIPIO': 'nunique',
        'VELOCIDAD_EFECTIVA_DOWNSTREAM': 'mean'
    }).reset_index()
    
    ranking_data['Valor_Por_Linea'] = ranking_data['VALOR_FACTURADO_O_COBRADO'] / ranking_data['CANTIDAD_LINEAS_ACCESOS']
    
    # Seleccionar columna según métrica
    metrica_map = {
        'Total de Líneas': ('CANTIDAD_LINEAS_ACCESOS', '{:,.0f}', 'Blues'),
        'Valor Facturado': ('VALOR_FACTURADO_O_COBRADO', '${:,.0f}', 'Greens'),
        'Valor por Línea': ('Valor_Por_Linea', '${:,.0f}', 'RdYlGn'),
        'Cobertura Departamental': ('DEPARTAMENTO', '{:.0f}', 'Oranges'),
        'Cobertura Municipal': ('MUNICIPIO', '{:.0f}', 'Purples'),
        'Velocidad Promedio': ('VELOCIDAD_EFECTIVA_DOWNSTREAM', '{:.2f} Mbps', 'Reds')
    }
    
    col_name, formato, color_scale = metrica_map[metrica_ranking]
    
    # Ordenar y tomar top N
    ranking_top = ranking_data.nlargest(top_n, col_name).copy()
    ranking_top['Ranking'] = range(1, len(ranking_top) + 1)
    
    # Acortar nombres largos
    ranking_top['Empresa_Display'] = ranking_top['EMPRESA'].apply(lambda x: x[:40] + '...' if len(x) > 40 else x)
    
    st.markdown("---")
    
    # Gráfico de ranking
    fig = px.bar(
        ranking_top,
        y='Empresa_Display',
        x=col_name,
        orientation='h',
        title=f'Top {top_n} Empresas por {metrica_ranking}',
        color=col_name,
        color_continuous_scale=color_scale,
        text=col_name if mostrar_valores else None
    )
    
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(
        showlegend=False,
        height=max(500, top_n * 25),
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla detallada
    st.markdown(f"### 📋 Tabla Detallada - Top {top_n}")
    
    display_cols = ['Ranking', 'EMPRESA', 'CANTIDAD_LINEAS_ACCESOS', 'VALOR_FACTURADO_O_COBRADO', 
                    'Valor_Por_Linea', 'DEPARTAMENTO', 'MUNICIPIO', 'VELOCIDAD_EFECTIVA_DOWNSTREAM']
    
    display_df = ranking_top[display_cols].copy()
    display_df.columns = ['#', 'Empresa', 'Total Líneas', 'Valor Total', 'Valor/Línea', 
                          'Deptos', 'Munis', 'Vel. Bajada']
    
    st.dataframe(display_df.style.format({
        'Total Líneas': '{:,.0f}',
        'Valor Total': '${:,.0f}',
        'Valor/Línea': '${:,.0f}',
        'Deptos': '{:.0f}',
        'Munis': '{:.0f}',
        'Vel. Bajada': '{:.2f}'
    }).background_gradient(cmap='YlGnBu', subset=['Total Líneas', 'Valor Total']),
    use_container_width=True, height=400)
    
    # Descargar ranking
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="⬇️ Descargar Ranking CSV",
        data=csv,
        file_name=f"ranking_{metrica_ranking.replace(' ', '_').lower()}.csv",
        mime="text/csv"
    )
    
    # Estadísticas del ranking
    st.markdown("---")
    st.markdown("### 📊 Estadísticas del Ranking")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Líder", ranking_top.iloc[0]['EMPRESA'][:25])
    
    with col2:
        valor_lider = ranking_top.iloc[0][col_name]
        st.metric("Valor Líder", formato.format(valor_lider))
    
    with col3:
        valor_promedio = ranking_top[col_name].mean()
        st.metric("Promedio Top " + str(top_n), formato.format(valor_promedio))
    
    with col4:
        concentracion = (ranking_top.head(5)[col_name].sum() / ranking_top[col_name].sum() * 100)
        st.metric("Concentración Top 5", f"{concentracion:.1f}%")