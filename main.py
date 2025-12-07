import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Servicios Fijos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1D3557;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #457B9D;
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1D3557;
    }
    </style>
""", unsafe_allow_html=True)

# Importar módulos
from modules import module_1_descripcion_general
from modules import module_2_analisis_exploratorio
from modules import module_3_valor_facturado
from modules import module_4_cantidad_lineas
from modules import module_5_patrones_anomalias
from modules import module_6_clustering
from modules import module_7_mapa_geografico
from modules import module_8_info_empresas
from utils import data_loader

def main():
    # Título principal
    st.markdown('<p class="main-header">📊 Análisis de Servicios Fijos - Colombia</p>', unsafe_allow_html=True)
    
    # Verificar y cargar datos
    data_path = Path("data/empaquetamiento_fijo_limpio_2023_2024.csv")
    
    if not data_path.exists():
        st.error("⚠️ No se encontró el archivo de datos. Ejecutando proceso de limpieza...")
        with st.spinner("Generando dataset limpio..."):
            from utils.data_preparation import generate_clean_dataset
            success = generate_clean_dataset()
            if success:
                st.success("✅ Dataset generado exitosamente!")
                st.rerun()
            else:
                st.error("❌ Error al generar el dataset. Por favor, verifica la conexión.")
                return
    
    # Cargar datos
    try:
        df = data_loader.load_data()
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return
    
    # Sidebar - Navegación
    with st.sidebar:
        # Logo mejorado sin placeholder
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1D3557 0%, #457B9D 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0;">📊 POSTDATA</h2>
            <p style="color: #F1FAEE; margin: 5px 0 0 0; font-size: 0.9em;">Análisis de Servicios Fijos</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        # Filtros globales
        st.markdown("### 🔍 Filtros Globales")
        
        # Selector de año
        años_disponibles = sorted(df['ANNO'].unique())
        año_inicio = st.selectbox(
            "Año inicio",
            años_disponibles,
            index=0,
            key="año_inicio"
        )
        
        año_fin = st.selectbox(
            "Año fin",
            años_disponibles,
            index=len(años_disponibles)-1,
            key="año_fin"
        )
        
        # Selector de trimestre
        col1, col2 = st.columns(2)
        with col1:
            trimestre_inicio = st.selectbox(
                "Trim. inicio",
                [1, 2, 3, 4],
                index=0,
                key="trim_inicio"
            )
        with col2:
            trimestre_fin = st.selectbox(
                "Trim. fin",
                [1, 2, 3, 4],
                index=3,
                key="trim_fin"
            )
        
        # Validación de fechas
        fecha_valida = True
        if año_inicio > año_fin:
            st.error("⚠️ El año de inicio no puede ser mayor al año fin")
            fecha_valida = False
        elif año_inicio == año_fin and trimestre_inicio > trimestre_fin:
            st.error("⚠️ El trimestre de inicio no puede ser mayor al trimestre fin")
            fecha_valida = False
        
        st.markdown("---")
        
        # Navegación principal
        st.markdown("### 📂 Navegación")
        
        modulo_seleccionado = st.radio(
            "Seleccione un módulo:",
            [
                "🏠 Inicio",
                "1️⃣ Descripción General",
                "2️⃣ Análisis Exploratorio",
                "3️⃣ Valor Facturado",
                "4️⃣ Cantidad de Líneas",
                "5️⃣ Patrones y Anomalías",
                "6️⃣ Clustering (ML)",
                "7️⃣ Mapa Geográfico",
                "8️⃣ Info de Empresas"
            ],
            key="modulo_principal"
        )
        
        # Submenús desplegables
        submodulo = None
        
        if modulo_seleccionado == "1️⃣ Descripción General":
            st.markdown("#### Submódulos:")
            submodulo = st.radio(
                "",
                [
                    "1.1 Registros por Año",
                    "1.2 Operadores",
                    "1.3 Cobertura Geográfica",
                    "1.4 Servicios Individuales vs Empaquetados"
                ],
                key="submodulo_1"
            )
        
        elif modulo_seleccionado == "2️⃣ Análisis Exploratorio":
            st.markdown("#### Submódulos:")
            submodulo = st.radio(
                "",
                [
                    "2.1 Tipos de Paquetes",
                    "2.2 Frecuencia por Tecnología",
                    "2.3 Comparación 2023 vs 2024"
                ],
                key="submodulo_2"
            )
        
        elif modulo_seleccionado == "3️⃣ Valor Facturado":
            st.markdown("#### Submódulos:")
            submodulo = st.radio(
                "",
                [
                    "3.1 Distribución por Paquete",
                    "3.2 Distribución por Operador",
                    "3.3 Comparación por Regiones",
                    "3.4 Evolución Trimestral"
                ],
                key="submodulo_3"
            )
        
        elif modulo_seleccionado == "4️⃣ Cantidad de Líneas":
            st.markdown("#### Submódulos:")
            submodulo = st.radio(
                "",
                [
                    "4.1 Distribución por Segmento",
                    "4.2 Relación Líneas-Paquete",
                    "4.3 Tendencias entre Años"
                ],
                key="submodulo_4"
            )
        
        elif modulo_seleccionado == "5️⃣ Patrones y Anomalías":
            st.markdown("#### Submódulos:")
            submodulo = st.radio(
                "",
                [
                    "5.1 Municipios con Crecimiento Inusual",
                    "5.2 Valores Facturados Anómalos",
                    "5.3 Tecnologías por Zona Geográfica"
                ],
                key="submodulo_5"
            )
        
        elif modulo_seleccionado == "6️⃣ Clustering (ML)":
            st.markdown("#### Submódulos:")
            submodulo = st.radio(
                "",
                [
                    "6.1 Configuración y Exploración",
                    "6.2 Análisis de Clusters",
                    "6.3 Perfiles y Patrones"
                ],
                key="submodulo_6"
            )
        
        elif modulo_seleccionado == "7️⃣ Mapa Geográfico":
            st.markdown("#### Submódulos:")
            submodulo = st.radio(
                "",
                [
                    "7.1 Mapa de Cobertura",
                    "7.2 Mapa de Valor Facturado",
                    "7.3 Mapa de Tecnologías",
                    "7.4 Mapa de Empresas"
                ],
                key="submodulo_7"
            )
        
        elif modulo_seleccionado == "8️⃣ Info de Empresas":
            st.markdown("#### Submódulos:")
            submodulo = st.radio(
                "",
                [
                    "8.1 Búsqueda de Empresa",
                    "8.2 Comparación de Empresas",
                    "8.3 Ranking de Empresas"
                ],
                key="submodulo_8"
            )
        
        st.markdown("---")
        
        # Información del dataset
        with st.expander("ℹ️ Información del Dataset"):
            st.metric("Total Registros", f"{len(df):,}")
            st.metric("Años", f"{df['ANNO'].min()} - {df['ANNO'].max()}")
            st.metric("Departamentos", df['DEPARTAMENTO'].nunique())
            st.metric("Operadores", df['EMPRESA'].nunique())
    
    # Contenido principal
    if not fecha_valida:
        st.warning("⚠️ Por favor, ajuste los filtros de fecha en la barra lateral.")
        return
    
    # Filtrar datos según selección
    df_filtrado = data_loader.filter_data(
        df, 
        año_inicio, 
        año_fin, 
        trimestre_inicio, 
        trimestre_fin
    )
    
    # Mostrar información del filtro
    st.info(f"📅 Período seleccionado: {año_inicio}-T{trimestre_inicio} a {año_fin}-T{trimestre_fin} | 📊 Registros: {len(df_filtrado):,}")
    
    # Renderizar módulo seleccionado
    if modulo_seleccionado == "🏠 Inicio":
        show_home(df_filtrado)
    
    elif modulo_seleccionado == "1️⃣ Descripción General":
        if submodulo == "1.1 Registros por Año":
            module_1_descripcion_general.show_registros_por_año(df_filtrado)
        elif submodulo == "1.2 Operadores":
            module_1_descripcion_general.show_operadores(df_filtrado)
        elif submodulo == "1.3 Cobertura Geográfica":
            module_1_descripcion_general.show_cobertura_geografica(df_filtrado)
        elif submodulo == "1.4 Servicios Individuales vs Empaquetados":
            module_1_descripcion_general.show_servicios_individual_vs_empaquetado(df_filtrado)
    
    elif modulo_seleccionado == "2️⃣ Análisis Exploratorio":
        if submodulo == "2.1 Tipos de Paquetes":
            module_2_analisis_exploratorio.show_tipos_paquetes(df_filtrado)
        elif submodulo == "2.2 Frecuencia por Tecnología":
            module_2_analisis_exploratorio.show_frecuencia_tecnologia(df_filtrado)
        elif submodulo == "2.3 Comparación 2023 vs 2024":
            module_2_analisis_exploratorio.show_comparacion_años(df_filtrado)
    
    elif modulo_seleccionado == "3️⃣ Valor Facturado":
        if submodulo == "3.1 Distribución por Paquete":
            module_3_valor_facturado.show_distribucion_por_paquete(df_filtrado)
        elif submodulo == "3.2 Distribución por Operador":
            module_3_valor_facturado.show_distribucion_por_operador(df_filtrado)
        elif submodulo == "3.3 Comparación por Regiones":
            module_3_valor_facturado.show_comparacion_regiones(df_filtrado)
        elif submodulo == "3.4 Evolución Trimestral":
            module_3_valor_facturado.show_evolucion_trimestral(df_filtrado)
    
    elif modulo_seleccionado == "4️⃣ Cantidad de Líneas":
        if submodulo == "4.1 Distribución por Segmento":
            module_4_cantidad_lineas.show_distribucion_por_segmento(df_filtrado)
        elif submodulo == "4.2 Relación Líneas-Paquete":
            module_4_cantidad_lineas.show_relacion_lineas_paquete(df_filtrado)
        elif submodulo == "4.3 Tendencias entre Años":
            module_4_cantidad_lineas.show_tendencias_años(df_filtrado)
    
    elif modulo_seleccionado == "5️⃣ Patrones y Anomalías":
        if submodulo == "5.1 Municipios con Crecimiento Inusual":
            module_5_patrones_anomalias.show_municipios_crecimiento(df_filtrado)
        elif submodulo == "5.2 Valores Facturados Anómalos":
            module_5_patrones_anomalias.show_valores_anomalos(df_filtrado)
        elif submodulo == "5.3 Tecnologías por Zona Geográfica":
            module_5_patrones_anomalias.show_tecnologias_zona(df_filtrado)
    
    elif modulo_seleccionado == "6️⃣ Clustering (ML)":
        if submodulo == "6.1 Configuración y Exploración":
            module_6_clustering.show_configuracion_exploración(df_filtrado)
        elif submodulo == "6.2 Análisis de Clusters":
            module_6_clustering.show_analisis_clusters(df_filtrado)
        elif submodulo == "6.3 Perfiles y Patrones":
            module_6_clustering.show_perfiles_patrones(df_filtrado)
    
    elif modulo_seleccionado == "7️⃣ Mapa Geográfico":
        if submodulo == "7.1 Mapa de Cobertura":
            module_7_mapa_geografico.show_mapa_cobertura(df_filtrado)
        elif submodulo == "7.2 Mapa de Valor Facturado":
            module_7_mapa_geografico.show_mapa_valor(df_filtrado)
        elif submodulo == "7.3 Mapa de Tecnologías":
            module_7_mapa_geografico.show_mapa_tecnologias(df_filtrado)
        elif submodulo == "7.4 Mapa de Empresas":
            module_7_mapa_geografico.show_mapa_empresas(df_filtrado)
    
    elif modulo_seleccionado == "8️⃣ Info de Empresas":
        if submodulo == "8.1 Búsqueda de Empresa":
            module_8_info_empresas.show_busqueda_empresa(df_filtrado)
        elif submodulo == "8.2 Comparación de Empresas":
            module_8_info_empresas.show_comparacion_empresas(df_filtrado)
        elif submodulo == "8.3 Ranking de Empresas":
            module_8_info_empresas.show_ranking_empresas(df_filtrado)

def show_home(df):
    """Página de inicio con resumen ejecutivo"""
    st.markdown("## 🏠 Bienvenido al Dashboard de Análisis")
    
    st.markdown("""
    ### 📋 Sobre este Dashboard
    
    Esta aplicación interactiva permite explorar y analizar datos de **Empaquetamiento de Servicios Fijos** 
    en Colombia para los años 2023 y 2024.
    
    **Fuente de datos:** [Postdata - Gobierno de Colombia](https://www.postdata.gov.co)
    """)
    
    # Métricas principales
    st.markdown("### 📊 Métricas Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Registros",
            f"{len(df):,}",
            delta=None
        )
    
    with col2:
        total_lineas = df['CANTIDAD_LINEAS_ACCESOS'].sum()
        st.metric(
            "Total Líneas",
            f"{total_lineas:,.0f}",
            delta=None
        )
    
    with col3:
        total_valor = df['VALOR_FACTURADO_O_COBRADO'].sum()
        st.metric(
            "Valor Total Facturado",
            f"${total_valor/1e9:.2f}B",
            delta=None
        )
    
    with col4:
        n_operadores = df['EMPRESA'].nunique()
        st.metric(
            "Operadores",
            f"{n_operadores}",
            delta=None
        )
    
    st.markdown("---")
    
    # Guía de uso
    st.markdown("### 🎯 Cómo usar este Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🔍 Filtros Globales
        - Ajuste el período de análisis en la barra lateral
        - Seleccione año y trimestre de inicio y fin
        - Los filtros se aplican a todos los módulos
        """)
        
        st.markdown("""
        #### 📂 Navegación
        - Use el menú lateral para navegar entre módulos
        - Cada módulo tiene submódulos específicos
        - Los análisis se actualizan automáticamente
        """)
    
    with col2:
        st.markdown("""
        #### 📊 Módulos Disponibles
        1. **Descripción General**: Panorama del dataset
        2. **Análisis Exploratorio**: Patrones y tendencias
        3. **Valor Facturado**: Análisis económico
        4. **Cantidad de Líneas**: Distribución de servicios
        5. **Patrones y Anomalías**: Detección de outliers
        6. **Clustering (ML)**: Segmentación inteligente
        7. **Mapa Geográfico**: Visualización territorial
        8. **Info de Empresas**: Análisis de operadores 🆕
        """)
    
    st.markdown("---")
    
    # Distribución rápida
    st.markdown("### 📈 Vista Rápida")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top 5 Departamentos")
        top_deptos = df['DEPARTAMENTO'].value_counts().head(5)
        for i, (depto, count) in enumerate(top_deptos.items(), 1):
            pct = count / len(df) * 100
            st.write(f"{i}. **{depto}**: {count:,} ({pct:.1f}%)")
    
    with col2:
        st.markdown("#### Top 5 Operadores")
        top_ops = df['EMPRESA'].value_counts().head(5)
        for i, (op, count) in enumerate(top_ops.items(), 1):
            pct = count / len(df) * 100
            st.write(f"{i}. **{op[:30]}**: {count:,} ({pct:.1f}%)")

if __name__ == "__main__":
    main()