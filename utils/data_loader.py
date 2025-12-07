"""
Módulo para cargar y filtrar datos
"""
import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_data():
    """
    Carga el dataset limpio con caché para mejorar el rendimiento.
    
    Returns:
        pd.DataFrame: Dataset cargado
    """
    data_path = Path("data/empaquetamiento_fijo_limpio_2023_2024.csv")
    
    if not data_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {data_path}")
    
    df = pd.read_csv(data_path)
    
    # Agregar columnas derivadas útiles
    df['TIPO_SERVICIO'] = df['ID_SERVICIO_PAQUETE'].apply(
        lambda x: 'Individual' if x in [1, 2, 3] else 'Empaquetado'
    )
    
    # Clasificar tipos de paquetes
    paquete_clasificacion = {
        4: 'Duo Play',
        5: 'Duo Play',
        6: 'Duo Play',
        7: 'Triple Play'
    }
    df['TIPO_PAQUETE'] = df['ID_SERVICIO_PAQUETE'].map(paquete_clasificacion)
    
    # Clasificar tipo de cliente
    residencial_segmentos = [
        'Residencial Estrato 1', 'Residencial Estrato 2', 'Residencial Estrato 3',
        'Residencial Estrato 4', 'Residencial Estrato 5', 'Residencial Estrato 6'
    ]
    df['TIPO_CLIENTE'] = df['SEGMENTO'].apply(
        lambda x: 'Residencial' if x in residencial_segmentos else 'Corporativo/Otros'
    )
    
    # Calcular valor por línea
    df['VALOR_POR_LINEA'] = df.apply(
        lambda row: row['VALOR_FACTURADO_O_COBRADO'] / row['CANTIDAD_LINEAS_ACCESOS'] 
        if row['CANTIDAD_LINEAS_ACCESOS'] > 0 else 0,
        axis=1
    )
    
    # Agregar región geográfica
    regiones = {
        'Andina': ['CUNDINAMARCA', 'ANTIOQUIA', 'BOYACA', 'SANTANDER', 'NORTE DE SANTANDER', 
                   'TOLIMA', 'HUILA', 'CALDAS', 'RISARALDA', 'QUINDIO'],
        'Caribe': ['ATLANTICO', 'BOLIVAR', 'MAGDALENA', 'CESAR', 'LA GUAJIRA', 'CORDOBA', 'SUCRE', 'SAN ANDRES'],
        'Pacifica': ['VALLE DEL CAUCA', 'CAUCA', 'NARIÑO', 'CHOCO'],
        'Orinoquia': ['META', 'CASANARE', 'ARAUCA', 'VICHADA'],
        'Amazonia': ['CAQUETA', 'PUTUMAYO', 'AMAZONAS', 'GUAINIA', 'GUAVIARE', 'VAUPES']
    }
    
    df['REGION'] = 'Otra'
    for region, deptos in regiones.items():
        df.loc[df['DEPARTAMENTO'].isin(deptos), 'REGION'] = region
    
    return df

def filter_data(df, año_inicio, año_fin, trimestre_inicio, trimestre_fin):
    """
    Filtra el dataset según el rango de fechas seleccionado.
    
    Args:
        df: DataFrame a filtrar
        año_inicio: Año de inicio
        año_fin: Año de fin
        trimestre_inicio: Trimestre de inicio
        trimestre_fin: Trimestre de fin
    
    Returns:
        pd.DataFrame: Dataset filtrado
    """
    # Crear una columna auxiliar para facilitar el filtrado
    df['PERIODO'] = df['ANNO'] * 10 + df['TRIMESTRE']
    periodo_inicio = año_inicio * 10 + trimestre_inicio
    periodo_fin = año_fin * 10 + trimestre_fin
    
    df_filtrado = df[(df['PERIODO'] >= periodo_inicio) & (df['PERIODO'] <= periodo_fin)].copy()
    
    return df_filtrado

def get_summary_stats(df):
    """
    Calcula estadísticas resumen del dataset.
    
    Args:
        df: DataFrame
    
    Returns:
        dict: Diccionario con estadísticas
    """
    stats = {
        'total_registros': len(df),
        'total_lineas': df['CANTIDAD_LINEAS_ACCESOS'].sum(),
        'total_valor': df['VALOR_FACTURADO_O_COBRADO'].sum(),
        'valor_promedio': df['VALOR_FACTURADO_O_COBRADO'].mean(),
        'n_departamentos': df['DEPARTAMENTO'].nunique(),
        'n_municipios': df['MUNICIPIO'].nunique(),
        'n_operadores': df['EMPRESA'].nunique(),
        'n_servicios': df['SERVICIO_PAQUETE'].nunique()
    }
    return stats