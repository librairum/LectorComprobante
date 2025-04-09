import fitz
import re

archivo_pdf = 'facturas/FE- 1 10.01.23. Servcom agua bidon.pdf'

direccion_pattern = r'(CAL\.|PRO\.|JR\.|AV\.|PSJE\.)[\w\s\.\-º#]*?(HUARMEY|LIMA|ANCASH|CALLAO|CUSCO|AREQUIPA|TRUJILLO|PIURA|CHICLAYO)[\w\s\.\-º#]*'

with fitz.open(archivo_pdf) as pdf:
    texto_total = ""
    for pagina in pdf:
        texto_total += pagina.get_text()

direccion = re.search(direccion_pattern, texto_total)

if direccion:
    print("Dirección:", direccion.group())
else:
    print("No se encontró dirección.")