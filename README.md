# Inspiration Times

Blog interactivo de campañas publicitarias peruanas. Una aplicación Streamlit que permite explorar y analizar campañas publicitarias de agencias y marcas peruanas.

## Características

- 🔍 **Búsqueda por palabras clave** en campañas, descripciones y reconocimientos
- 🎯 **Filtros avanzados** por agencia, sector, medios y rango de fechas
- 📊 **Visualizaciones dinámicas**:
  - Distribución de campañas por agencia
  - Distribución por sector (gráfico de pastel)
  - Distribución por tipo de medio
  - Evolución de estrategias a lo largo del tiempo
- 📈 **Métricas en tiempo real** de total de campañas, agencias y sectores

## Instalación Local

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/inspiration-times.git
cd inspiration-times
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

## Despliegue en Streamlit Cloud

1. Sube el repositorio a GitHub
2. Ve a [Streamlit Cloud](https://share.streamlit.io/)
3. Selecciona "New app"
4. Conecta tu repositorio de GitHub
5. Selecciona la rama `main` y el archivo `app.py`
6. ¡Listo! Tu aplicación estará disponible en internet

## Datos

La aplicación contiene 20 campañas publicitarias peruanas con información sobre:
- Nombre de la campaña
- Marca
- Agencia publicitaria
- Sector (Turismo, Bebidas, Telecomunicaciones, etc.)
- Medios utilizados (TV, Digital, Radio, Influencers, etc.)
- Tipo de estrategia
- Fecha de lanzamiento
- Tono de comunicación
- Reconocimientos obtenidos
- Descripción

## Tecnologías

- [Streamlit](https://streamlit.io/) - Framework para crear aplicaciones web con Python
- [Pandas](https://pandas.pydata.org/) - Análisis y manipulación de datos
- [Matplotlib](https://matplotlib.org/) - Visualización
- [Seaborn](https://seaborn.pydata.org/) - Visualización estadística

## Estilos

La interfaz sigue el estilo del New York Times con:
- Color rojo principal: `#AA0601`
- Color de fondo crema: `#F5F1DE`
- Tipografía Georgia serif

## Licencia

Este proyecto está bajo la licencia MIT.
