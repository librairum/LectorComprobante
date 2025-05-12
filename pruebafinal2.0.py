import fitz  # PyMuPDF
import re
import os

# Función para extraer la razón social
def extraer_razon_social(pdf_path):
    doc = fitz.open(pdf_path)
    texto_superior = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["bbox"][1] < 150:  # Parte superior
                            if span["text"].isupper():
                                texto_superior.append(span["text"])
        break  # Solo primera página

    texto_superior_filtrado = [linea for linea in texto_superior if not any(palabra in linea for palabra in ["RUC", "FACTURA", "BOLETA", "ELECTRONICA", "E001"])]
    razon_social = texto_superior_filtrado[0] if texto_superior_filtrado else ""
    return razon_social

# Función mejorada para extraer dirección
def extraer_direccion(pdf_path):
    posibles_inicios = ("CAL.", "PRO.", "JR.", "AV.", "PSJE.")
    palabras_fin = {"RUC", "Fecha de Emisión", "Tipo de Moneda", "Forma de Pago", "Importe Total", "Número de Documento"}

    with fitz.open(pdf_path) as pdf:
        texto_total = ""
        for pagina in pdf:
            texto_total += pagina.get_text()

    lineas = texto_total.split('\n')
    direccion_lineas = []
    recolectando = False

    for linea in lineas:
        if any(linea.strip().startswith(pref) for pref in posibles_inicios):
            direccion_lineas.append(linea.strip())
            recolectando = True
        elif recolectando:
            if any(palabra in linea for palabra in palabras_fin):
                break
            direccion_lineas.append(linea.strip())

    if direccion_lineas:
        return ' '.join(direccion_lineas)
    else:
        return "No se encontró dirección."

# Función para extraer otros datos con expresiones regulares
def extraer_datos(pdf_file_path):
    with open(pdf_file_path, 'rb') as file:
        pdf_reader = fitz.open(pdf_file_path)
        text = '\n'.join([page.get_text() for page in pdf_reader])

    lineas = text.split('\n')
    lineas_filtradas = [
        linea for linea in lineas
        if linea.strip() not in {"Cantidad Unidad", "Medida", "Descripción", "Valor Unitario", "Código", "Fecha Emisión"}
    ]
    text_filtrado = '\n'.join(lineas_filtradas)

    # Expresiones regulares
    patrones = {
        "RUC": r'RUC\s*:?\s*(\d{11})',
        "Número de Documento": r'(E\d{3}-\d+)',
        "Fecha de Emisión": r'Fecha\s*de\s*Emisión\s*:?\s*(\d{2}/\d{2}/\d{4})',
        "Tipo de Moneda": r'Moneda\s*:?\s*(\w+)',
        "Forma de Pago": r'Forma de pago\s*:?\s*([\w\s]+)',
        "Importe Total": r'Importe\s*T\s*otal\s*:?\s*S?/?\s*([\d,]+\.\d{2})'
    }

    # Buscar datos usando expresiones regulares
    datos_extraidos = {}
    for campo, patron in patrones.items():
        match = re.search(patron, text_filtrado, re.IGNORECASE)
        datos_extraidos[campo] = match.group(1).strip() if match else 'No encontrado'

    # Agregar Razón Social y Dirección (funciones separadas)
    datos_extraidos["Razón Social"] = extraer_razon_social(pdf_file_path)
    datos_extraidos["Dirección"] = extraer_direccion(pdf_file_path)

    return datos_extraidos

# Función para procesar todos los PDFs en una carpeta
def procesar_pdfs_en_carpeta(carpeta):
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".pdf"):
            pdf_path = os.path.join(carpeta, archivo)
            datos = extraer_datos(pdf_path)

            print(f"\n--- Datos Extraídos de la Factura ({os.path.basename(pdf_path)}) ---")
            for clave, valor in datos.items():
                print(f"{clave}: {valor}")

# Ruta de la carpeta con los PDFs
pdf_folder = "BANCOS/"
procesar_pdfs_en_carpeta(pdf_folder)
