"""
Módulo para preparar y limpiar el dataset de empaquetamiento de servicios fijos
"""
import pandas as pd
import numpy as np
from pathlib import Path

def generate_clean_dataset():
    """
    Descarga, limpia y prepara el dataset de empaquetamiento de servicios fijos.
    
    Returns:
        bool: True si se generó exitosamente, False en caso contrario
    """
    try:
        print("="*80)
        print("GENERANDO DATASET LIMPIO")
        print("="*80)
        
        # URL del dataset
        url = "https://www.postdata.gov.co/sites/default/files/datasets/data/EMPAQUETAMIENTO_FIJO_11.csv"
        
        print("\n1. Descargando datos...")
        df = pd.read_csv(url, sep=None, engine='python', on_bad_lines='skip', encoding='utf-8')
        df.columns = df.columns.str.replace('\ufeff', '')
        print(f"   ✓ Datos descargados: {len(df):,} registros")
        
        # Filtrar años 2023 y 2024
        print("\n2. Filtrando años 2023 y 2024...")
        df_analisis = df[df['ANNO'].isin([2023, 2024])].copy()
        print(f"   ✓ Registros filtrados: {len(df_analisis):,}")
        
        # Definir tipos esperados
        campos_esperados = {
            'ANNO': 'int64', 'TRIMESTRE': 'int64', 'ID_EMPRESA': 'int64', 'EMPRESA': 'object',
            'ID_DEPARTAMENTO': 'int64', 'DEPARTAMENTO': 'object', 'ID_MUNICIPIO': 'int64',
            'MUNICIPIO': 'object', 'ID_SEGMENTO': 'int64', 'SEGMENTO': 'object',
            'ID_SERVICIO_PAQUETE': 'int64', 'SERVICIO_PAQUETE': 'object',
            'VELOCIDAD_EFECTIVA_DOWNSTREAM': 'float64', 'VELOCIDAD_EFECTIVA_UPSTREAM': 'float64',
            'ID_TECNOLOGIA_ACCESO': 'int64', 'TECNOLOGIA': 'object', 'ID_ESTADO': 'int64',
            'ESTADO': 'object', 'CANTIDAD_LINEAS_ACCESOS': 'int64',
            'VALOR_FACTURADO_O_COBRADO': 'int64', 'OTROS_VALORES_FACTURADOS': 'int64'
        }
        
        # Convertir tipos de datos
        print("\n3. Convirtiendo tipos de datos...")
        conversiones_necesarias = {}
        for campo, tipo_esperado in campos_esperados.items():
            if campo in df_analisis.columns:
                tipo_actual = str(df_analisis[campo].dtype)
                if tipo_actual != tipo_esperado and tipo_actual == 'object' and tipo_esperado in ['int64', 'float64']:
                    conversiones_necesarias[campo] = tipo_esperado
        
        for campo, tipo_esperado in conversiones_necesarias.items():
            try:
                if tipo_esperado == 'int64':
                    df_analisis[campo] = pd.to_numeric(df_analisis[campo], errors='coerce').astype('Int64')
                elif tipo_esperado == 'float64':
                    df_analisis[campo] = pd.to_numeric(df_analisis[campo], errors='coerce')
                print(f"   ✓ {campo} convertido a {tipo_esperado}")
            except Exception as e:
                print(f"   ✗ Error convirtiendo {campo}: {e}")
        
        # Corregir campo TECNOLOGIA
        print("\n4. Corrigiendo campo TECNOLOGIA...")
        df_analisis['TECNOLOGIA'] = df_analisis['TECNOLOGIA'].replace('NA (No Aplica)', 'NA')
        print("   ✓ TECNOLOGIA estandarizada")
        
        # Imputar valores nulos
        print("\n5. Imputando valores nulos...")
        
        # Imputar valores facturados
        for campo in ['VALOR_FACTURADO_O_COBRADO', 'OTROS_VALORES_FACTURADOS']:
            nulos_antes = df_analisis[campo].isna().sum()
            if nulos_antes > 0:
                medianas = df_analisis.groupby(['ID_DEPARTAMENTO', 'ID_SERVICIO_PAQUETE'])[campo].median()
                for idx in df_analisis[df_analisis[campo].isna()].index:
                    dept = df_analisis.loc[idx, 'ID_DEPARTAMENTO']
                    serv = df_analisis.loc[idx, 'ID_SERVICIO_PAQUETE']
                    if (dept, serv) in medianas.index:
                        valor = int(medianas[(dept, serv)])
                        df_analisis.at[idx, campo] = valor
                    else:
                        df_analisis.at[idx, campo] = 0
                print(f"   ✓ {campo}: {nulos_antes:,} valores imputados")
        
        # Imputar velocidades
        servicios_con_internet = [1, 4, 5, 7]
        for campo in ['VELOCIDAD_EFECTIVA_DOWNSTREAM', 'VELOCIDAD_EFECTIVA_UPSTREAM']:
            nulos_antes = df_analisis[campo].isna().sum()
            if nulos_antes > 0:
                # Servicios sin internet: poner 0
                mask_sin_internet = (~df_analisis['ID_SERVICIO_PAQUETE'].isin(servicios_con_internet)) & (df_analisis[campo].isna())
                df_analisis.loc[mask_sin_internet, campo] = 0.0
                
                # Servicios con internet: imputar con mediana
                mask_con_internet = (df_analisis['ID_SERVICIO_PAQUETE'].isin(servicios_con_internet)) & (df_analisis[campo].isna())
                medianas = df_analisis[df_analisis['ID_SERVICIO_PAQUETE'].isin(servicios_con_internet)].groupby(
                    ['ID_DEPARTAMENTO', 'ID_SERVICIO_PAQUETE']
                )[campo].median()
                
                for idx in df_analisis[mask_con_internet].index:
                    dept = df_analisis.loc[idx, 'ID_DEPARTAMENTO']
                    serv = df_analisis.loc[idx, 'ID_SERVICIO_PAQUETE']
                    if (dept, serv) in medianas.index:
                        df_analisis.at[idx, campo] = float(medianas[(dept, serv)])
                    else:
                        mediana_global = df_analisis[df_analisis['ID_SERVICIO_PAQUETE']==serv][campo].median()
                        if pd.notna(mediana_global):
                            df_analisis.at[idx, campo] = float(mediana_global)
                        else:
                            df_analisis.at[idx, campo] = 0.0
                
                print(f"   ✓ {campo}: {nulos_antes:,} valores imputados")
        
        # Crear directorio data si no existe
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Guardar dataset limpio
        output_path = data_dir / "empaquetamiento_fijo_limpio_2023_2024.csv"
        df_analisis.to_csv(output_path, index=False, encoding='utf-8')
        
        print("\n" + "="*80)
        print("DATASET GENERADO EXITOSAMENTE")
        print("="*80)
        print(f"Archivo: {output_path}")
        print(f"Registros: {len(df_analisis):,}")
        print(f"Columnas: {len(df_analisis.columns)}")
        print(f"Nulos restantes: {df_analisis.isnull().sum().sum()}")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al generar dataset: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    generate_clean_dataset()