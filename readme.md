# 📊 Dashboard de Análisis de Servicios Fijos - Colombia

Dashboard interactivo desarrollado en **Streamlit** para el análisis de datos de empaquetamiento de servicios fijos en Colombia (2023-2024), utilizando datos públicos de [Postdata - Gobierno de Colombia](https://www.postdata.gov.co).

[![Ver aplicación desplegada](https://img.shields.io/badge/Ver%20App-Deploy-blue)](http://157.137.229.69:5555/)
## 🚀 Aplicación desplegada

La aplicación está disponible aquí:  
👉 http://157.137.229.69:5555/


## 🎯 Características Principales

- **8 Módulos de Análisis Completos**
- **Visualizaciones Interactivas** con Plotly
- **Mapas Geográficos** de Colombia
- **Machine Learning** (Clustering con K-Means)
- **Filtros Dinámicos** por año y trimestre
- **+50 Gráficos y Métricas**

---

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/andresgomez2000/POSTDATA.git
cd POSTDATA
```

### 2. Crear entorno virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Contenido de requirements.txt:**
```
streamlit==1.31.0
pandas==2.1.4
numpy==1.24.3
plotly==5.18.0
scikit-learn==1.3.2
```

---

## 📁 Estructura del Proyecto

```
POSTDATA/
│
├── app.py                          # Aplicación principal
├── requirements.txt                # Dependencias
├── README.md                       # Este archivo
│
├── data/                           # Carpeta de datos
│   └── empaquetamiento_fijo_limpio_2023_2024.csv
│
├── modules/                        # Módulos de análisis
│   ├── __init__.py
│   ├── module_1_descripcion_general.py
│   ├── module_2_analisis_exploratorio.py
│   ├── module_3_valor_facturado.py
│   ├── module_4_cantidad_lineas.py
│   ├── module_5_patrones_anomalias.py
│   ├── module_6_clustering.py
│   ├── module_7_mapa_geografico.py
│   └── module_8_info_empresas.py
│
└── utils/                          # Utilidades
    ├── __init__.py
    ├── data_loader.py              # Cargador de datos
    └── data_preparation.py         # Preparación de datos
```

---

## 💾 Preparación de Datos

### Opción 1: Datos Limpios Pre-procesados

Si ya tiene el archivo limpio, colóquelo en la carpeta `data/`:

```
data/empaquetamiento_fijo_limpio_2023_2024.csv
```

### Opción 2: Proceso Automático de Limpieza

Si tiene los archivos originales de Postdata, el dashboard puede procesarlos automáticamente:

1. Coloque los archivos originales en la carpeta `data/`:
   - `empaquetamiento_2023_*.csv`
   - `empaquetamiento_2024_*.csv`

2. El dashboard detectará que no existe el archivo limpio y ejecutará automáticamente el proceso de limpieza.

---

## ▶️ Ejecutar la Aplicación

```bash
streamlit run app.py
```

El dashboard se abrirá automáticamente en su navegador en: `http://localhost:8501`

---

## 📊 Módulos del Dashboard

### 1️⃣ Descripción General
- **1.1 Registros por Año**: Análisis de volumen de datos
- **1.2 Operadores**: Top operadores y participación
- **1.3 Cobertura Geográfica**: Departamentos y municipios
- **1.4 Servicios Individual vs Empaquetado**: Distribución de tipos

### 2️⃣ Análisis Exploratorio
- **2.1 Tipos de Paquetes**: Duo Play vs Triple Play
- **2.2 Frecuencia por Tecnología**: HFC, FTTH, xDSL, etc.
- **2.3 Comparación 2023 vs 2024**: Evolución temporal

### 3️⃣ Valor Facturado
- **3.1 Distribución por Paquete**: Análisis de ingresos
- **3.2 Distribución por Operador**: Concentración de mercado
- **3.3 Comparación por Regiones**: Análisis geográfico
- **3.4 Evolución Trimestral**: Tendencias temporales

### 4️⃣ Cantidad de Líneas
- **4.1 Distribución por Segmento**: Residencial vs Corporativo
- **4.2 Relación Líneas-Paquete**: Correlaciones
- **4.3 Tendencias entre Años**: Crecimiento

### 5️⃣ Patrones y Anomalías
- **5.1 Municipios con Crecimiento Inusual**: Detección de outliers
- **5.2 Valores Facturados Anómalos**: Análisis estadístico
- **5.3 Tecnologías por Zona Geográfica**: Diversidad tecnológica

### 6️⃣ Clustering (Machine Learning)
- **6.1 Configuración y Exploración**: Preparación de datos
- **6.2 Análisis de Clusters**: K-Means con validación
- **6.3 Perfiles y Patrones**: Segmentación inteligente

### 7️⃣ Mapa Geográfico
- **7.1 Mapa de Cobertura**: Visualización nacional
- **7.2 Mapa de Valor Facturado**: Distribución económica
- **7.3 Mapa de Tecnologías**: Infraestructura
- **7.4 Mapa de Empresas**: Presencia geográfica

### 8️⃣ Info de Empresas 🆕
- **8.1 Búsqueda de Empresa**: Análisis individual detallado
- **8.2 Comparación de Empresas**: Benchmarking
- **8.3 Ranking de Empresas**: Top operadores por métricas

---

## 🎨 Características Técnicas

### Tecnologías Utilizadas
- **Streamlit**: Framework de aplicaciones web
- **Pandas**: Manipulación de datos
- **Plotly**: Visualizaciones interactivas
- **Scikit-learn**: Machine Learning (clustering)
- **NumPy**: Operaciones numéricas

### Funcionalidades
- ✅ Filtros globales por año y trimestre
- ✅ Navegación intuitiva con sidebar
- ✅ Más de 50 visualizaciones interactivas
- ✅ Mapas geográficos de Colombia
- ✅ Clustering automático con K-Means
- ✅ Exportación de datos en CSV
- ✅ Diseño responsive

---

## 🔧 Configuración Avanzada

### Cambiar Puerto

```bash
streamlit run app.py --server.port 8502
```

### Modo Desarrollo (auto-reload)

```bash
streamlit run app.py --server.runOnSave true
```

### Configuración de Memoria

Si trabaja con datasets grandes:

```bash
streamlit run app.py --server.maxUploadSize 500
```

---

## 📈 Casos de Uso

### Para Analistas de Datos
- Exploración rápida de tendencias
- Identificación de patrones y anomalías
- Comparación de operadores

### Para Reguladores
- Monitoreo de mercado
- Análisis de cobertura
- Evaluación de competencia

### Para Investigadores
- Análisis de mercado
- Clustering de operadores
- Estudios de infraestructura

---

## 🐛 Solución de Problemas

### Error: "No se encontró el archivo de datos"

Asegúrese de tener el archivo CSV en la carpeta correcta:
```
data/empaquetamiento_fijo_limpio_2023_2024.csv
```

### Error: "ModuleNotFoundError"

Instale todas las dependencias:
```bash
pip install -r requirements.txt
```

### El dashboard se ve mal o no carga

1. Limpie la caché de Streamlit:
```bash
streamlit cache clear
```

2. Reinicie el servidor

### Datos muy lentos

Si el dataset es muy grande, considere:
- Filtrar por periodo específico
- Reducir el número de registros en limpieza
- Aumentar memoria RAM disponible

---

## 📝 Información del Proyecto

### Fuente de Datos
Los datos provienen de [Postdata](https://www.postdata.gov.co/dataset/empaquetamiento-de-servicios-fijos), el portal de datos abiertos del Gobierno de Colombia.

### Actualizaciones
El dashboard está preparado para recibir datos actualizados. Simplemente reemplace el archivo CSV en la carpeta `data/` y reinicie la aplicación.



---

## 👥 Contribuciones

Este proyecto fue desarrollado como parte de una prueba técnica para análisis de datos con Python.

---

**Desarrollado por: Andrés Gómez**


**¡Disfrute explorando los datos de servicios fijos de Colombia! 🇨🇴 📊**
