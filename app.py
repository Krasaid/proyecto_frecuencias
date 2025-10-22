import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from utils.estadistica import calcular_frecuencias # Importa la función central de cálculo estadístico
import io

# =============================================================================
# 1. CONFIGURACIÓN INICIAL DE STREAMLIT
# =============================================================================
# Configuración de página: título de pestaña y layout amplio (wide)
st.set_page_config(page_title="Generador de Tablas de Frecuencia", layout="wide")

# ======== ESTILOS RESPONSIVOS (Inyección de CSS) ========
# Usa st.markdown para inyectar CSS customizado para una mejor UI/UX
st.markdown("""
    <style>
        /* Definición de variables de color (estilo "Dark Mode" con acentos ámbar) */
        :root {
            --amber-500: #F59E0B;
            --amber-400: #FBBF24;
            --gray-800: #1F2937;
            --gray-100: #F3F4F6;
        }

        /* Estilos base para el cuerpo y contenedor principal */
        body {
            background-color: var(--gray-800);
            color: var(--gray-100);
            font-family: 'Inter', sans-serif;
        }

        .main {
            background-color: var(--gray-800);
            padding: 1.5rem;
            border-radius: 16px;
        }

        /* Estilo para títulos (Headers) */
        h1, h2, h3 {
            color: var(--amber-500); /* Color de acento ámbar */
            font-weight: 700;
        }

        /* Botones (Aplica estilos a todos los tipos de botones de Streamlit) */
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stButton"] button {
            background: var(--amber-500);
            color: var(--gray-800);
            font-weight: 600;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            border: none;
            transition: 0.3s ease;
        }
        /* Efecto hover para botones */
        div[data-testid="stDownloadButton"] button:hover,
        div[data-testid="stButton"] button:hover {
            background: var(--amber-400);
            transform: scale(1.05);
        }

        /* Estilo para DataFrames (Tablas de Pandas) */
        .stDataFrame {
            background-color: #374151; /* Fondo oscuro sutil */
            border-radius: 12px;
        }

        /* Ajuste responsivo: Convierte columnas en filas en pantallas pequeñas */
        @media (max-width: 900px) {
            section[data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
            }
        }

        /* Asegura que todo el texto sea visible con el fondo oscuro */
        p, label, span {
            color: var(--gray-100) !important;
        }
    </style>
""", unsafe_allow_html=True) # Necesario para inyectar código HTML/CSS

# =============================================================================
# 2. INTERFAZ DE USUARIO Y ENTRADA DE DATOS
# =============================================================================
st.title("Generador de Tablas de Frecuencia y Gráficos Estadísticos")
st.write("Herramienta interactiva para estudiantes y docentes")

# Selector para el método de ingreso de datos
opcion = st.radio("Selecciona el método de ingreso de datos:", ["Manual", "Archivo Excel"])
datos = [] # Lista para almacenar los datos numéricos

# --- Lógica de Ingreso Manual ---
if opcion == "Manual":
    # Text area para que el usuario ingrese valores separados por coma
    valores = st.text_area("Introduce los valores numéricos separados por coma (Ejemplo: 12, 15, 18, 20, 25)")
    if valores:
        try:
            # Procesa la cadena de texto: separa por coma, elimina espacios y convierte a float
            datos = [float(x.strip()) for x in valores.split(",") if x.strip()]
        except:
            st.error("Asegúrate de que todos los valores sean numéricos.")
# --- Lógica de Ingreso por Archivo Excel ---
else:
    # Widget para subir archivo (solo acepta .xlsx)
    archivo = st.file_uploader("Sube un archivo Excel (.xlsx)", type=["xlsx"])
    if archivo:
        # Lee el archivo excel con Pandas
        df = pd.read_excel(archivo)
        # Permite al usuario seleccionar la columna de datos
        columna = st.selectbox("Selecciona la columna con los datos:", df.columns)
        # Extrae los datos de la columna seleccionada, elimina NaN y convierte a lista
        datos = df[columna].dropna().tolist()

# =============================================================================
# 3. PROCESAMIENTO Y VISUALIZACIÓN DE RESULTADOS
# =============================================================================
if datos:
    st.success(f"{len(datos)} datos cargados correctamente.")

    # Llama a la función de utilidad para generar la tabla de frecuencias
    # Se asume que esta función maneja la agrupación por intervalos.
    tabla = calcular_frecuencias(datos)

    st.subheader("Tabla de Distribución de Frecuencias")
    # Muestra el DataFrame en la aplicación de Streamlit
    st.dataframe(tabla, use_container_width=True)

    # ======== GRÁFICOS (Matplotlib y Seaborn) ========
    # Divide la interfaz en dos columnas para mostrar gráficos lado a lado
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gráfico de Barras")
        # Crea la figura y los ejes de Matplotlib con fondo oscuro
        fig, ax = plt.subplots(facecolor="#1F2937")
        # Genera el gráfico de barras usando Seaborn
        sns.barplot(x="Marca de clase", y="Frecuencia absoluta", data=tabla, ax=ax, color="#F59E0B")
        # Aplica estilos para que el gráfico se integre con el tema oscuro
        ax.set_facecolor("#1F2937")
        ax.tick_params(colors="#F3F4F6") # Color de ticks
        ax.set_xlabel("Marca de clase", color="#F3F4F6") # Color de etiqueta X
        ax.set_ylabel("Frecuencia absoluta", color="#F3F4F6") # Color de etiqueta Y
        st.pyplot(fig) # Muestra el gráfico en Streamlit

    with col2:
        st.subheader("Gráfico Circular")
        fig2, ax2 = plt.subplots(facecolor="#1F2937")
        # Genera el gráfico de pastel (pie chart) usando la frecuencia absoluta
        ax2.pie(tabla["Frecuencia absoluta"], labels=tabla["Marca de clase"], autopct="%1.1f%%",
                # Colores personalizados (ámbar en diferentes tonos)
                colors=["#F59E0B", "#FBBF24", "#FDE68A", "#FEF3C7"])
        st.pyplot(fig2)

    # Histograma (Gráfico de distribución)
    st.subheader("Histograma")
    fig3, ax3 = plt.subplots(facecolor="#1F2937")
    # Usa `datos` originales y el número de intervalos (len(tabla)) para los 'bins'
    ax3.hist(datos, bins=len(tabla), edgecolor="#F3F4F6", color="#F59E0B")
    # Aplica estilos de tema oscuro
    ax3.set_facecolor("#1F2937")
    ax3.tick_params(colors="#F3F4F6")
    ax3.set_xlabel("Datos", color="#F3F4F6")
    ax3.set_ylabel("Frecuencia", color="#F3F4F6")
    st.pyplot(fig3)

    # =============================================================================
    # 4. EXPORTAR RESULTADOS (Excel y PDF)
    # =============================================================================
    st.subheader(" Exportar Resultados")

    # --- Exportar a Excel ---
    excel_buffer = io.BytesIO() # Crea un buffer en memoria para el archivo
    # Usa ExcelWriter para escribir el DataFrame en el buffer
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        tabla.to_excel(writer, index=False, sheet_name="Frecuencias")
    excel_buffer.seek(0) # Vuelve al inicio del buffer
    # Botón de descarga para el archivo Excel
    st.download_button(
        "⬇Descargar Excel",
        data=excel_buffer,
        file_name="tabla_frecuencias.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # --- Exportar a PDF (Usando fpdf) ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Tabla de Frecuencias", ln=True, align="C")
    pdf.ln(8)
    # Itera sobre las filas del DataFrame para generar el contenido del PDF
    for _, row in tabla.iterrows():
        # Formato de la línea para el PDF
        line = f"{row['Límite inferior']} - {row['Límite superior']} | f={row['Frecuencia absoluta']} | fr={row['Frecuencia relativa']}"
        pdf.cell(200, 8, txt=line, ln=True)
    # Obtiene la salida del PDF como bytes
    pdf_output = io.BytesIO(pdf.output(dest="S").encode("latin1"))
    # Botón de descarga para el archivo PDF
    st.download_button(
        "Descargar PDF",
        data=pdf_output,
        file_name="tabla_frecuencias.pdf",
        mime="application/pdf",
    )

# Mensaje de estado inicial
else:
    st.info("Esperando datos para procesar...")