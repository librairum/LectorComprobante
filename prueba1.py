import fitz

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

pdf_path = "pdfs/FE-6 150223impres. planos.pdf"
print("Razón Social:", extraer_razon_social(pdf_path))