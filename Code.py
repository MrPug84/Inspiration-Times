import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns

# --- Definición de funciones de búsqueda y filtrado ---

def buscar_campanas_por_palabra_clave(keyword, fields, dataframe):
    """
    Busca campañas por palabras clave en los campos de texto especificados.

    Args:
        keyword (str): La palabra clave a buscar.
        fields (list): Una lista de nombres de columnas donde buscar la palabra clave.
        dataframe (pd.DataFrame): El DataFrame donde realizar la búsqueda.

    Returns:
        pd.DataFrame: Un DataFrame con las campañas que coinciden con la búsqueda.
    """
    keyword_lower = keyword.lower()
    mask = pd.Series([False] * len(dataframe), index=dataframe.index)

    for field in fields:
        if field in dataframe.columns and dataframe[field].dtype == 'object':
            field_mask = dataframe[field].astype(str).str.contains(keyword_lower, case=False, na=False)
            mask = mask | field_mask
        elif field == 'medios' and field in dataframe.columns:
            field_mask = dataframe[field].apply(lambda x: any(keyword_lower in str(item).lower() for item in x))
            mask = mask | field_mask

    return dataframe[mask].reset_index(drop=True)

def filtrar_campanas_por_criterios(dataframe, criterios):
    """
    Filtra campañas en un DataFrame por múltiples criterios.

    Args:
        dataframe (pd.DataFrame): El DataFrame que contiene los datos de las campañas.
        criterios (dict): Un diccionario donde las claves son los nombres de las columnas
                          y los valores son los criterios de filtrado.

    Returns:
        pd.DataFrame: Un DataFrame con las campañas que cumplen todos los criterios especificados.
    """
    mask = pd.Series([True] * len(dataframe), index=dataframe.index)

    for columna, valor_criterio in criterios.items():
        if columna not in dataframe.columns:
            continue

        if columna in ['agencia', 'sector', 'tipo_estrategia', 'tono_comunicacion']:
            if pd.api.types.is_string_dtype(dataframe[columna]):
                mask &= (dataframe[columna].str.lower() == str(valor_criterio).lower())

        elif columna == 'medios':
            if isinstance(valor_criterio, list):
                medios_sub_mask = pd.Series([False] * len(dataframe), index=dataframe.index)
                for medio_buscado in valor_criterio:
                    medios_sub_mask |= dataframe['medios'].apply(lambda x:
                        any(str(medio_buscado).lower() == str(m).lower() for m in x)
                    )
                mask &= medios_sub_mask

        elif columna == 'fecha_lanzamiento':
            if isinstance(valor_criterio, (tuple, list)) and len(valor_criterio) == 2:
                try:
                    fecha_inicio = pd.to_datetime(valor_criterio[0])
                    fecha_fin = pd.to_datetime(valor_criterio[1])
                    mask &= (dataframe['fecha_lanzamiento'] >= fecha_inicio) & \
                            (dataframe['fecha_lanzamiento'] <= fecha_fin)
                except ValueError:
                    pass

    return dataframe[mask].reset_index(drop=True)

# --- Cargar y Preprocesar Datos ---

datos_string_csv = """id,nombre_campana,marca,agencia,sector,medios,tipo_estrategia,fecha_lanzamiento,tono_comunicacion,reconocimientos,descripcion
1,Perú Eres Tú,Perú (Marca País),McCann,Turismo,TV|Radio|Digital,Identidad Nacional,2023-01-15,Emocional,Festival Cannes,Campaña que posiciona Perú como destino turístico
2,Ama lo Tuyo,Inca Kola,VML,Bebidas,TV|OOH|Digital,Nostalgia y Orgullo,2022-06-20,Desenfadado,Lápiz de Oro,Reposicionamiento basado en patrimonio cultural
3,La Voz del Pueblo,Movistar,Circus Grey,Telecomunicaciones,Digital|Social Media,Engagement Social,2024-03-10,Inspirador,Effie Awards,Plataforma de participación ciudadana
4,Juntos Somos Más,BCP,Fahrenheit DDB,Finanzas,TV|Digital|Experiencial,Inclusión Financiera,2023-09-05,Humano,IAB Peru Awards,Campaña sobre educación financiera
5,Destapa lo Mejor,Corona,Digitas,Bebidas,Digital|Influencers|OOH,Experiencia,2024-01-12,Joven,Cannes Lions,Activación con micro-influencers
6,Poder Femenino,Avon,121 Latam,Belleza,Digital|TV|Social,Empoderamiento,2023-05-22,Inspirador,Premios Óscar de Publicidad,Celebra mujeres emprendedoras
7,Sin Límites,Nike,Valor,Deporte,Digital|OOH|Experiencias,Rendimiento,2024-02-14,Motivacional,Festival Publicidad Lima,Atletas peruanos como protagonistas
8,Recuerda Quién Eres,Telefónica,Ogilvy Perú,Telecomunicaciones,TV|Digital,Identidad,2023-11-08,Nostálgico,Premio Aníbal Ford,Conexión emocional con usuarios
9,Reinvéntate,Scotiabank,Boost Brand,Finanzas,Digital|Redes Sociales,Transformación,2024-04-19,Optimista,Viral en Redes,Adaptación a nuevas economías
10,Sabor a Perú,Gloria,McCann,Alimentos,TV|OOH|Digital,Patrimonio Culinario,2023-07-30,Cálido,Lápiz de Oro,Productos lácteos con raíces peruanas
11,Somos Resilientes,Agua Oxigenada Mercononi,VML,Salud,Digital|Influencers,Resiliencia,2024-05-10,Humano,Trending Topic,Mensajes positivos post-pandemia
12,La Conexión Verdadera,Claro,Circus Grey,Telecomunicaciones,TV|Digital|Social,Comunidad,2023-08-15,Emocional,Premios Lima Advertising,Humanos conectados
13,Tu Futuro Empieza Hoy,Beca Perú,Fahrenheit DDB,Educación,Digital|TV,Aspiración,2024-06-01,Inspirador,IAB Awards,Becas para jóvenes peruanos
14,Muévete,Reebok,Digitas,Deporte,Digital|Influencers,Actividad Física,2023-10-25,Energético,Festival Publicidad,Movimiento y bienestar
15,Raíces Profundas,Quilmes,121 Latam,Bebidas,OOH|TV|Digital,Tradición,2024-03-20,Nostálgico,Cannes Lions,Herencia familiar
16,Vive Más,Seguros Integra,Valor,Seguros,Digital|TV,Calidad de Vida,2023-12-05,Tranquilizador,Lápiz de Oro,Protección familiar
17,El Poder está en Ti,Nestlé,Ogilvy Perú,Alimentos,TV|Digital|Experiencial,Empoderamiento,2024-02-28,Motivacional,Premio Aníbal Ford,Nutrición y desarrollo
18,Más Cerca,Interbank,Boost Brand,Finanzas,Digital|Social,Proximidad,2024-01-30,Cálido,IAB Awards,Banking digital accesible
19,Herencia de Innovación,Samsung,McCann,Tecnología,Digital|TV|OOH,Innovación,2023-09-12,Futurista,Cannes Lions,Tecnología con raíces peruanas
20,Juntos por Perú,Caja Arequipa,VML,Finanzas,Digital|Experiencial,Solidaridad,2024-04-05,Inspirador,Festival Publicidad,Microfinanzas solidarias"""

df = pd.read_csv(io.StringIO(datos_string_csv), sep=',')
df['medios'] = df['medios'].apply(lambda x: x.split('|'))
df['fecha_lanzamiento'] = pd.to_datetime(df['fecha_lanzamiento'])
df['año_lanzamiento'] = df['fecha_lanzamiento'].dt.year

# Traducción de los valores de la columna 'medios'
media_translation_map = {
    'TV': 'Televisión',
    'Radio': 'Radio',
    'Digital': 'Digital',
    'OOH': 'Publicidad Exterior',
    'Influencers': 'Influencers',
    'Social Media': 'Redes Sociales',
    'Social': 'Redes Sociales',
    'Experiencial': 'Experiencial',
    'Experiencias': 'Experiencial'
}

df['medios'] = df['medios'].apply(lambda x: [media_translation_map.get(medio, medio) for medio in x])

# --- Configuración de la interfaz de usuario Streamlit ---

st.set_page_config(page_title="Inspiration Times", layout="wide")

# Estilos CSS personalizados estilo New York Times
st.markdown("""
    <style>
    /* Colores: Rojo NYT (#AA0601) y Crema (#F5F1DE) */
    :root {
        --nyt-red: #AA0601;
        --nyt-cream: #F5F1DE;
        --dark-gray: #333333;
    }
    
    /* Fondo general */
    .stApp {
        background-color: var(--nyt-cream) !important;
    }
    
    /* Títulos principales */
    h1 {
        color: var(--nyt-red) !important;
        font-family: 'Georgia', serif !important;
        font-size: 3em !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        margin-bottom: 0.5em !important;
    }
    
    /* Subtítulos */
    h2 {
        color: var(--nyt-red) !important;
        font-family: 'Georgia', serif !important;
        font-size: 1.8em !important;
        font-weight: bold !important;
        border-bottom: 3px solid var(--nyt-red) !important;
        padding-bottom: 10px !important;
    }
    
    /* Texto general */
    body, p, span, div {
        font-family: 'Georgia', serif !important;
        color: var(--nyt-red) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--nyt-cream) !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: var(--nyt-red) !important;
    }
    
    /* Botones y selectbox */
    .stSelectbox, .stMultiSelect, .stDateInput {
        font-family: 'Georgia', serif !important;
    }
    
    .stSelectbox label, .stMultiSelect label, .stDateInput label {
        color: var(--nyt-red) !important;
        font-family: 'Georgia', serif !important;
    }
    
    .stButton > button {
        background-color: var(--nyt-red) !important;
        color: var(--nyt-cream) !important;
        font-family: 'Georgia', serif !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        background-color: #8a0501 !important;
        color: var(--nyt-cream) !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        font-family: 'Georgia', serif !important;
        background-color: var(--nyt-cream) !important;
    }
    
    /* Métrica */
    .metric-card {
        background-color: var(--nyt-cream) !important;
        border-left: 4px solid var(--nyt-red) !important;
    }
    
    /* Input de búsqueda */
    .stTextInput input {
        font-family: 'Georgia', serif !important;
        border-color: var(--nyt-red) !important;
        background-color: white !important;
        color: var(--nyt-red) !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--nyt-red) !important;
        box-shadow: 0 0 0 1px var(--nyt-red) !important;
    }
    
    .stTextInput label {
        color: var(--nyt-red) !important;
    }
    
    /* Elementos de entrada */
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > select {
        background-color: white !important;
        color: var(--nyt-red) !important;
    }
    
    /* Tabs y tabs content */
    .stTabs [data-baseweb="tab-list"] button {
        color: var(--nyt-red) !important;
        font-family: 'Georgia', serif !important;
    }
    
    /* Warnings, Info, Success */
    .stWarning, .stInfo, .stSuccess, .stError {
        background-color: white !important;
        color: var(--nyt-red) !important;
        font-family: 'Georgia', serif !important;
    }
    
    .streamlit-expanderHeader {
        color: var(--nyt-red) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title('📰 INSPIRATION TIMES')
st.markdown("<p style='font-family: Georgia, serif; color: #666; font-style: italic; margin-top: -15px;'>Blog interactivo de campañas publicitarias peruanas</p>", unsafe_allow_html=True)

# Campo de entrada de texto para búsqueda de palabras clave
keyword_search = st.text_input('🔍 Buscar campaña por palabra clave...', '')

# Barra lateral para filtros
st.sidebar.header('🎯 Filtros de Campañas')

# Filtro por 'Agencia'
agencias_unicas = ['Todas'] + sorted(df['agencia'].unique().tolist())
agencia_filter = st.sidebar.selectbox('Filtrar por Agencia', agencias_unicas)

# Filtro por 'Sector'
sectores_unicos = ['Todos'] + sorted(df['sector'].unique().tolist())
sector_filter = st.sidebar.selectbox('Filtrar por Sector', sectores_unicos)

# Filtro por 'Medios'
medios_unicos = sorted(list(set(item for sublist in df['medios'] for item in sublist)))
medios_filter = st.sidebar.multiselect('Filtrar por Medios', medios_unicos)

# Filtro por 'fecha_lanzamiento'
st.sidebar.subheader('📅 Rango de Fechas de Lanzamiento')
min_date_df = df['fecha_lanzamiento'].min().to_pydatetime().date()
max_date_df = df['fecha_lanzamiento'].max().to_pydatetime().date()
start_date = st.sidebar.date_input('Fecha de Inicio', value=min_date_df)
end_date = st.sidebar.date_input('Fecha de Fin', value=max_date_df)

# --- Lógica de Búsqueda y Filtrado ---

df_actual = df.copy()

if keyword_search:
    df_actual = buscar_campanas_por_palabra_clave(
        keyword_search,
        ['nombre_campana', 'descripcion', 'reconocimientos', 'tono_comunicacion'],
        df_actual
    )

criterios_filtrado = {}

if agencia_filter != 'Todas':
    criterios_filtrado['agencia'] = agencia_filter

if sector_filter != 'Todos':
    criterios_filtrado['sector'] = sector_filter

if medios_filter:
    criterios_filtrado['medios'] = medios_filter

if start_date <= end_date:
    criterios_filtrado['fecha_lanzamiento'] = (start_date, end_date)
else:
    st.sidebar.error('La fecha de inicio no puede ser posterior a la fecha de fin.')

if criterios_filtrado:
    df_actual = filtrar_campanas_por_criterios(df_actual, criterios_filtrado)

# --- Resultados de las Campañas ---
st.subheader('📊 Resultados de las Campañas')

if not df_actual.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Campañas", len(df_actual))
    with col2:
        st.metric("Agencias", df_actual['agencia'].nunique())
    with col3:
        st.metric("Sectores", df_actual['sector'].nunique())
    
    st.dataframe(df_actual, use_container_width=True)
else:
    st.warning("No se encontraron campañas con los criterios seleccionados.")

# --- Visualizaciones de Tendencias ---
st.subheader('📈 Visualizaciones de Tendencias')

if not df_actual.empty:
    # Visualización 1: Distribución de campañas por agencia.
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    sns.countplot(data=df_actual, x='agencia', order=df_actual['agencia'].value_counts().index, palette='viridis', hue='agencia', legend=False, ax=ax1)
    ax1.set_title('Distribución de Campañas por Agencia', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Agencia', fontsize=12)
    ax1.set_ylabel('Número de Campañas', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig1)

    # Visualización 2: Distribución de campañas por sector.
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    df_actual['sector'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, cmap='plasma', ax=ax2)
    ax2.set_title('Distribución de Campañas por Sector', fontsize=14, fontweight='bold')
    ax2.set_ylabel('')
    plt.tight_layout()
    st.pyplot(fig2)

    # Visualización 3: Distribución de campañas por tipo de medio.
    medios_desapilados_filtered = df_actual['medios'].explode()
    if not medios_desapilados_filtered.empty:
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        sns.countplot(x=medios_desapilados_filtered, order=medios_desapilados_filtered.value_counts().index, palette='magma', hue=medios_desapilados_filtered, legend=False, ax=ax3)
        ax3.set_title('Distribución de Campañas por Tipo de Medio', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Tipo de Medio', fontsize=12)
        ax3.set_ylabel('Número de Campañas', fontsize=12)
        ax3.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        st.pyplot(fig3)

    # Visualización 4: Evolución de 'tipo_estrategia' a lo largo del tiempo.
    estrategias_comunes_filtered = df_actual['tipo_estrategia'].value_counts().nlargest(5).index
    df_filtrado_estrategias_viz = df_actual[df_actual['tipo_estrategia'].isin(estrategias_comunes_filtered)]

    if not df_filtrado_estrategias_viz.empty:
        tendencia_estrategias_filtered = df_filtrado_estrategias_viz.groupby(['año_lanzamiento', 'tipo_estrategia']).size().unstack(fill_value=0)

        fig4, ax4 = plt.subplots(figsize=(14, 7))
        tendencia_estrategias_filtered.plot(kind='line', marker='o', ax=ax4)
        ax4.set_title('Tendencia de Tipos de Estrategia a lo largo del Tiempo (Top 5)', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Año de Lanzamiento', fontsize=12)
        ax4.set_ylabel('Número de Campañas', fontsize=12)
        ax4.legend(title='Tipo de Estrategia', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig4)
else:
    st.info("No hay datos disponibles para generar visualizaciones.")
