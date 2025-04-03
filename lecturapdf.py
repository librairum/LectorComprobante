import PyPDF2
import re
import os

def extract_pdf_info(pdf_file_path):
    with open(pdf_file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = '\n'.join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    
    #lineas que no van al caso
    lineas = text.split('\n')
    lineas_filtradas = [linea for linea in lineas if not re.search(r'CantidadUnidad|MedidaCódigo|Descripción|Valor Unitario', linea, re.IGNORECASE)]
    text = '\n'.join(lineas_filtradas)
    
    # Expresiones regulares
    patrones = {
        "RUC": r'RUC\s*:?\s*(\d{11})',
        "Razón Social": r'([\w\s\.,\-]+)',
        "Dirección Razón Social": r'([\w\s\.,\-]+)',
        "Número de Documento": r'(E\d{3}-\d+)',
        "Fecha Emisión": r'Fecha\s*de\s*Emisión\s*:?\s*(\d{2}/\d{2}/\d{4})',
        "Tipo de Moneda": r'Moneda\s*:?\s*(\w+)',
        "Forma de Pago": r'Forma de pago\s*:?\s*([\w\s]+)',
        "Importe Total": r'Importe\s*T\s*otal\s*:?\s*S?/\s*([\d,]+\.\d{2})'
    }

    # Buscar datos
    datos_extraidos = {campo: re.search(patron, text, re.IGNORECASE) for campo, patron in patrones.items()}
    datos_extraidos = {campo: match.group(1).strip() if match else 'No encontrado' for campo, match in datos_extraidos.items()}

    # Mostrar datos
    print(f"\n--- Datos Extraídos de la Factura ({os.path.basename(pdf_file_path)}) ---")
    for clave, valor in datos_extraidos.items():
        print(f"{clave}: {valor}")

def procesar_pdfs_en_carpeta(carpeta):
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".pdf"):
            pdf_path = os.path.join(carpeta, archivo)
            extract_pdf_info(pdf_path)

pdf_folder = "facturas/"
procesar_pdfs_en_carpeta(pdf_folder)
