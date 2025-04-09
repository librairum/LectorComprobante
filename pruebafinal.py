import fitz  
import re
import os
import pandas as pd  

def extraer_razon_social(pdf_path):
    doc = fitz.open(pdf_path)
    texto_superior = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["bbox"][1] < 150:
                            if span["text"].isupper():
                                texto_superior.append(span["text"])
        break  

    texto_superior_filtrado = [linea for linea in texto_superior if not any(palabra in linea for palabra in ["RUC", "FACTURA", "BOLETA", "ELECTRONICA", "E001"])]
    razon_social = texto_superior_filtrado[0] if texto_superior_filtrado else ""
    return razon_social

def extraer_direccion(pdf_path):
    direccion_pattern = r'(CAL\.|PRO\.|JR\.|AV\.|PSJE\.)[\w\s\.\-º#]*?(HUARMEY|LIMA|ANCASH|CALLAO|CUSCO|AREQUIPA|TRUJILLO|PIURA|CHICLAYO)[\w\s\.\-º#]*'
    with fitz.open(pdf_path) as pdf:
        texto_total = ""
        for pagina in pdf:
            texto_total += pagina.get_text()

    direccion = re.search(direccion_pattern, texto_total)
    return direccion.group() if direccion else "No se encontró dirección."

def extraer_datos(pdf_file_path):
    with open(pdf_file_path, 'rb') as file:
        pdf_reader = fitz.open(pdf_file_path)
        text = '\n'.join([page.get_text() for page in pdf_reader])

    patrones = {
        "RUC": r'RUC\s*:?\s*(\d{11})',
        "Número de Documento": r'(E\d{3}-\d+)',
        "Fecha Emisión": r'Fecha\s*de\s*Emisión\s*:?\s*(\d{2}/\d{2}/\d{4})',
        "Tipo de Moneda": r'Moneda\s*:?\s*(\w+)',
        "Forma de Pago": r'Forma de pago\s*:?\s*([\w\s]+)',
        "Importe Total": r'Importe\s*T\s*otal\s*:?\s*S?/\s*([\d,]+\.\d{2})'
    }

    datos_extraidos = {}
    for campo, patron in patrones.items():
        match = re.search(patron, text, re.IGNORECASE)
        datos_extraidos[campo] = match.group(1).strip() if match else 'No encontrado'

    datos_extraidos["Razón Social"] = extraer_razon_social(pdf_file_path)
    datos_extraidos["Dirección"] = extraer_direccion(pdf_file_path)

    return datos_extraidos

def procesar_pdfs_en_carpeta(carpeta):
    resultados = []
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".pdf"):
            pdf_path = os.path.join(carpeta, archivo)
            datos = extraer_datos(pdf_path)

            datos_filtrados = {clave: valor for clave, valor in datos.items() if valor != "No encontrado"}

            resultados.append(datos_filtrados)

    df = pd.DataFrame(resultados)

    df.to_excel("resultados_facturas.xlsx", index=False)

    print("Datos guardados en 'resultados_facturas.xlsx'.")

pdf_folder = "facturas/"  
procesar_pdfs_en_carpeta(pdf_folder)
