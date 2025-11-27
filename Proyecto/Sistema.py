from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import pyodbc
import bcrypt
import webbrowser
import os
from werkzeug.utils import secure_filename
import fitz
import re
import pandas as pd
from datetime import datetime
import numpy as np
from pdf2image import convert_from_path
import pytesseract

app = Flask(__name__)
app.secret_key = "clave_secreta"

# ====== SQL SERVER ======
conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-FMAPHMT\\SQLDEVELOPER;'
    'DATABASE=Proyecto_PPP;'
    'UID=sa;'
    'PWD=Ijuma31;'
    'TrustServerCertificate=yes;'
)
cursor = conn.cursor()

# ====== STORAGE LOCAL ======
BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

RESULTADOS_EXTRAIDOS = [] 

# ====== CONFIG OCR EMISOR ======
RUTA_POPPLER = r"C:\poppler\poppler-25.11.0\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

RUTA_EXCEL_EMISOR = os.path.join(EXPORT_DIR, "emisor_extraccion.xlsx")


# ========= FUNCIONES OCR EMISOR =========
def pdf_a_texto_emisor(ruta_pdf):
    paginas = convert_from_path(ruta_pdf, dpi=300, poppler_path=RUTA_POPPLER)
    imagen = np.array(paginas[0]) 
    texto = pytesseract.image_to_string(imagen, lang="spa")
    return texto


def _parse_monto_emisor(cadena):
    if not cadena:
        return 0.0

    s = str(cadena).strip()
    s = (
        s.replace("S/.", "")
        .replace("S/", "")
        .replace("s/.", "")
        .replace("s/", "")
        .replace(" ", "")
    )

    if "," in s and "." not in s:
        s = s.replace(",", ".")
    elif "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")

    try:
        return float(s)
    except:
        return 0.0


def extraer_campos_emisor(texto):
    datos = {
        "tipo": "",
        "nrodocumento": "",
        "fechaemision": "",
        "ruc": "",
        "razon_social": "",
        "medio_pago": "",
        "moneda": "",
        "subtotal": 0.0,
        "anticipos": 0.0,
        "descuentos": 0.0,
        "valor_venta": 0.0,
        "isc": 0.0,
        "igv": 0.0,
        "icbper": 0.0,
        "otro_cargo": 0.0,
        "otros_tributos": 0.0,
        "monto_redondeo": 0.0,
        "importe_total": 0.0,
    }

    lineas = [l.strip() for l in texto.splitlines() if l.strip()]
    texto_upper = texto.upper()

    # ---------- TIPO ----------
    if "FACTURA" in texto_upper:
        datos["tipo"] = "factura"
    elif "BOLETA" in texto_upper:
        datos["tipo"] = "boleta"

    # ---------- RUC EMISOR + RAZÓN SOCIAL ----------
    for i, lin in enumerate(lineas):
        m = re.search(r"R\.?U\.?C\.?\s*[:\-]?\s*(\d{11})", lin, re.IGNORECASE)
        if not m:
            continue

        ruc_encontrado = m.group(1)
        contexto = lin.upper()
        if i > 0:
            contexto += " " + lineas[i - 1].upper()

        if "CLIENTE" in contexto or "SEÑOR" in contexto or "SENOR" in contexto:
            continue

        datos["ruc"] = ruc_encontrado

        razon_idx = None

        for j in range(i - 6, i + 1):
            if j < 0:
                continue
            txt_j = lineas[j].strip()
            up_j = txt_j.upper()

            if any(p in up_j for p in ["NOMBRE", "RAZON", "RAZÓN", "CLIENTE"]):
                continue

            if re.search(r"(S\.A\.C|SAC|EIRL|S\.R\.L|S\.A\.A)", txt_j, re.IGNORECASE):
                razon_idx = j
                break

        if razon_idx is None:
            for j in range(i - 6, i):
                if j < 0:
                    continue
                txt_j = lineas[j].strip()
                up_j = txt_j.upper()

                tiene_letras = re.search(r"[A-ZÁÉÍÓÚÑ]{3,}", up_j) is not None
                muchos_digitos = len(re.findall(r"\d", up_j)) > 4
                es_ban_word = any(
                    palabra in up_j
                    for palabra in [
                        "RUC", "CLIENTE", "FACTURA", "BOLETA",
                        "DIRECCION", "DIRECCIÓN",
                        "NOMBRE", "RAZON", "RAZÓN",
                        "MONEDA", "FORMA DE PAGO",
                        "AV.", "JR.", "CALLE", "S/"
                    ]
                )
                if tiene_letras and not muchos_digitos and not es_ban_word:
                    razon_idx = j
                    break

        # último recurso: línea anterior
        if razon_idx is None and i > 0:
            razon_idx = i - 1

        # concatenación de línea anterior si parece parte del nombre
        if razon_idx is not None and razon_idx >= 0:
            nombre = lineas[razon_idx].strip()
            if razon_idx - 1 >= 0:
                prev = lineas[razon_idx - 1].strip()
                up_prev = prev.upper()
                tiene_letras_prev = re.search(r"[A-ZÁÉÍÓÚÑ]{3,}", up_prev) is not None
                es_ban_prev = any(
                    p in up_prev
                    for p in [
                        "RUC", "CLIENTE", "FACTURA", "BOLETA",
                        "DIRECCION", "DIRECCIÓN",
                        "NOMBRE", "RAZON", "RAZÓN",
                        "MONEDA", "FORMA DE PAGO",
                        "AV.", "JR.", "CALLE", "S/"
                    ]
                )
                if tiene_letras_prev and not es_ban_prev and len(prev) < 40:
                    nombre = prev + " " + nombre

            datos["razon_social"] = nombre

        break  # ya tenemos RUC y razón social

    # ---------- NRO DOCUMENTO ----------
    serie_regex = r"\b([A-Z0-9]{1,4}\s*[-–]\s*\d{3,10})\b"
    candidatos = re.findall(serie_regex, texto_upper)
    if candidatos:
        datos["nrodocumento"] = candidatos[0].replace(" ", "")

    # ---------- FECHA EMISIÓN ----------
    m_fecha_tag = re.search(
        r"FECHA\s*[:\-]?\s*([0-3]?\d[\/\-.][01]?\d[\/\-.][12]\d{3})", texto_upper
    )
    if m_fecha_tag:
        datos["fechaemision"] = m_fecha_tag.group(1)
    else:
        m1 = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", texto)
        if m1:
            datos["fechaemision"] = m1.group(1)
        else:
            m2 = re.search(r"(\d{4})(\d{2})(\d{2})\s+\d{2}:\d{2}:\d{2}", texto)
            if m2:
                datos["fechaemision"] = f"{m2.group(3)}/{m2.group(2)}/{m2.group(1)}"

    # ---------- MONEDA ----------
    if "MONEDA" in texto_upper:
        m = re.search(r"MONEDA\s*[:\-]?\s*([A-ZÁÉÍÓÚ ]+)", texto_upper)
        if m:
            txt = m.group(1)
            if "SOL" in txt:
                datos["moneda"] = "soles"
            elif "DOL" in txt or "USD" in txt:
                datos["moneda"] = "dolares"
    else:
        if "S/." in texto or "S/" in texto:
            datos["moneda"] = "soles"

    # ---------- MEDIO DE PAGO ----------
    if "CONTADO" in texto_upper:
        datos["medio_pago"] = "contado"
    elif "CRÉDITO" in texto_upper or "CREDITO" in texto_upper:
        datos["medio_pago"] = "credito"
    elif "EFECTIVO" in texto_upper:
        datos["medio_pago"] = "efectivo"
    elif any(m in texto_upper for m in ["TARJETA", "VISA", "MASTERCARD"]):
        datos["medio_pago"] = "tarjeta"

    # ---------- SUBTOTAL / VALOR VENTA ----------
    for lin in lineas:
        up = lin.upper()
        if any(p in up for p in ["SUB", "GRAVADO", "GRAVADA", "VALOR VENTA", "VALOR DE VENTA", "OP. GRAVADA"]):
            nums = re.findall(r"([\d.,]+)", lin)
            if nums:
                datos["subtotal"] = _parse_monto_emisor(nums[-1])
                datos["valor_venta"] = datos["subtotal"]

    # ---------- DESCUENTOS ----------
    for lin in lineas:
        if "DESCUENTO" in lin.upper():
            nums = re.findall(r"([\d.,]+)", lin)
            if nums:
                datos["descuentos"] = _parse_monto_emisor(nums[-1])

    # ---------- ANTICIPOS ----------
    for lin in lineas:
        if "ANTICIPO" in lin.upper():
            nums = re.findall(r"([\d.,]+)", lin)
            if nums:
                datos["anticipos"] = _parse_monto_emisor(nums[-1])

    # ---------- ISC ----------
    for lin in lineas:
        if "ISC" in lin.upper():
            nums = re.findall(r"([\d.,]+)", lin)
            if nums:
                datos["isc"] = _parse_monto_emisor(nums[-1])

    # ---------- IGV ----------
    for lin in lineas:
        up = lin.upper()
        if "IGV" in up or "I.G.V" in up or "TGV" in up:
            nums = re.findall(r"([\d.,]+)", lin)
            if nums:
                datos["igv"] = _parse_monto_emisor(nums[-1])

    # ---------- ICBPER ----------
    for lin in lineas:
        up = lin.upper()
        if "ICBPER" in up or "BOLSA" in up:
            nums = re.findall(r"([\d.,]+)", lin)
            if nums:
                datos["icbper"] = _parse_monto_emisor(nums[-1])

    # ---------- OTROS CARGOS ----------
    for lin in lineas:
        up = lin.upper()
        if "OTRO" in up and "CARGO" in up:
            nums = re.findall(r"([\d.,]+)", lin)
            if nums:
                datos["otro_cargo"] = _parse_monto_emisor(nums[-1])

    # ---------- OTROS TRIBUTOS ----------
    for lin in lineas:
        up = lin.upper()
        if "OTRO" in up and "TRIBUTO" in up:
            nums = re.findall(r"([\d.,]+)", lin)
            if nums:
                datos["otros_tributos"] = _parse_monto_emisor(nums[-1])

    # ---------- MONTO REDONDEO ----------
    for lin in lineas:
        up = lin.upper()
        if "REDONDEO" in up:
            nums = re.findall(r"([\d.,]+)", lin)
            if nums:
                datos["monto_redondeo"] = _parse_monto_emisor(nums[-1])

    # ---------- IMPORTE TOTAL ----------
    totales_candidatos = []
    for lin in lineas:
        up = lin.upper()
        if "TOTAL" in up and "SUB" not in up:
            nums = re.findall(r"([\d.,]+)", lin)
            if nums:
                totales_candidatos.append(_parse_monto_emisor(nums[-1]))

    if totales_candidatos:
        datos["importe_total"] = max(totales_candidatos)

    # ---------- FALLBACK IGV ----------
    if datos["subtotal"] > 0 and datos["importe_total"] > 0 and datos["igv"] == 0:
        dif = round(datos["importe_total"] - datos["subtotal"], 2)
        if 0 < dif < datos["subtotal"]:
            datos["igv"] = dif

    return datos


def guardar_en_excel_emisor(datos, ruta_excel=RUTA_EXCEL_EMISOR):
    fila = pd.DataFrame([datos])
    if os.path.exists(ruta_excel):
        df_existente = pd.read_excel(ruta_excel)
        df_nuevo = pd.concat([df_existente, fila], ignore_index=True)
        df_nuevo.to_excel(ruta_excel, index=False)
    else:
        fila.to_excel(ruta_excel, index=False)


# ========= EXTRACCIÓN (ACTUAL) REGISTRO COMPRA =========
def extraer_razon_social(pdf_path):
    doc = fitz.open(pdf_path)
    texto_superior = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["bbox"][1] < 150 and span["text"].isupper():
                            texto_superior.append(span["text"])
        break
    texto_superior_filtrado = [
        linea for linea in texto_superior
        if not any(p in linea for p in ["RUC", "FACTURA", "BOLETA", "ELECTRONICA", "E001"])
    ]
    return texto_superior_filtrado[0] if texto_superior_filtrado else ""


def extraer_direccion(pdf_path):
    posibles_inicios = ("CAL.", "PRO.", "JR.", "AV.", "PSJE.")
    palabras_fin = {"RUC", "Fecha de Emisión", "Tipo de Moneda", "Forma de Pago", "Importe Total", "Número de Documento"}
    with fitz.open(pdf_path) as pdf:
        texto_total = "".join([p.get_text() for p in pdf])
    lineas = texto_total.split('\n')
    direccion_lineas, recolectando = [], False
    for linea in lineas:
        if any(linea.strip().startswith(pref) for pref in posibles_inicios):
            direccion_lineas.append(linea.strip()); recolectando = True
        elif recolectando:
            if any(palabra in linea for palabra in palabras_fin): break
            direccion_lineas.append(linea.strip())
    return ' '.join(direccion_lineas) if direccion_lineas else "No se encontró dirección."


def extraer_datos(pdf_file_path):
    with fitz.open(pdf_file_path) as pdf_reader:
        text = '\n'.join([page.get_text() for page in pdf_reader])
    lineas = text.split('\n')
    lineas_filtradas = [
        l for l in lineas if l.strip() not in {
            "Cantidad Unidad", "Cantidad", "Unidad Medida", "ICBPER", "Medida", "Descripción", "Valor Unitario", "Código", "Fecha Emisión"
        }
    ]
    text_filtrado = '\n'.join(lineas_filtradas)
    patrones = {
        "RUC": r'RUC\s*:?\s*(\d{11})',
        "Número de Documento": r'(E\d{3}-\d+)',
        "Fecha de Emisión": r'Fecha\s*de\s*Emisión\s*:?\s*(\d{2}/\d{2}/\d{4})',
        "Tipo de Moneda": r'Moneda\s*:?\s*(\w+)',
        "Forma de Pago": r'Forma de pago\s*:?\s*([\w\s]+)',
        "Importe Total": r'Importe\s*T\s*otal\s*:?\s*S?/?\s*([\d,]+\.\d{2})'
    }
    datos = {}
    for campo, patron in patrones.items():
        m = re.search(patron, text_filtrado, re.IGNORECASE)
        datos[campo] = m.group(1).strip() if m else 'No encontrado'
    datos["Razón Social"] = extraer_razon_social(pdf_file_path)
    datos["Dirección"] = extraer_direccion(pdf_file_path)
    return datos


# ========= OPERACIONES =========
def registrar_operacion(usuario_id, tipo, nombre_archivo, ruta_archivo, estado):
    cursor.execute("""
        INSERT INTO dbo.Operaciones (Tipo, NombreArchivo, RutaArchivo, Estado, FechaCreacion, UsuarioID)
        VALUES (?, ?, ?, ?, GETDATE(), ?)
    """, (tipo, nombre_archivo, ruta_archivo, estado, usuario_id))
    conn.commit()

def obtener_reportes(limit=50):
    cursor.execute(f"""
        SELECT TOP {limit} OperacionID, NombreArchivo, RutaArchivo, FechaCreacion, Tipo
        FROM dbo.Operaciones
        WHERE Tipo IN ('EXPORTACION','REPORTE')
        ORDER BY FechaCreacion DESC
    """)
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, r)) for r in cursor.fetchall()]

def obtener_operacion(op_id):
    cursor.execute("""
        SELECT OperacionID, NombreArchivo, RutaArchivo, Tipo, Estado, FechaCreacion
        FROM dbo.Operaciones WHERE OperacionID=?
    """, (op_id,))
    return cursor.fetchone()

def kpi_reportes_total():
    cursor.execute("""
        SELECT COUNT(*) FROM dbo.Operaciones
        WHERE Tipo IN ('EXPORTACION','REPORTE')
    """)
    return cursor.fetchone()[0]

def kpi_exportaciones_total():
    cursor.execute("""
        SELECT COUNT(*) FROM dbo.Operaciones
        WHERE Tipo='EXPORTACION'
    """)
    return cursor.fetchone()[0]

def kpi_usuarios_activos():
    cursor.execute("SELECT COUNT(*) FROM dbo.Usuarios WHERE Estado='Activo'")
    return cursor.fetchone()[0]

def ultimas_operaciones(limit=10):
    cursor.execute(f"""
        SELECT TOP {limit}
               O.OperacionID,
               O.Tipo,
               O.NombreArchivo,
               O.Estado,
               O.FechaCreacion,
               U.NombreCompleto
        FROM dbo.Operaciones O
        JOIN dbo.Usuarios   U ON U.UsuarioID = O.UsuarioID
        ORDER BY O.FechaCreacion DESC
    """)
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, r)) for r in cursor.fetchall()]


# ----------- LOGIN ----------
@app.route('/')
def home():
    return render_template('login.html')

# ----------- REGISTRO ----------
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        confirmar_contrasena = request.form['confirmar_contrasena']
        if contrasena != confirmar_contrasena:
            flash("❌ Las contraseñas no coinciden", "error")
            return redirect(url_for('registro'))
        hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
        try:
            cursor.execute("""
                INSERT INTO Usuarios (NombreCompleto, CorreoElectronico, Contrasena, FechaRegistro, Estado)
                VALUES (?, ?, ?, GETDATE(), 'Inactivo')
            """, (nombre, correo, hashed.decode('utf-8')))
            conn.commit()
            flash("✅ Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"⚠️ Error al registrar: {e}", "error")
            return redirect(url_for('registro'))
    return render_template('registro.html')

# ----------- INICIAR SESIÓN ----------
@app.route('/iniciar-sesion', methods=['POST'])
def iniciar_sesion():
    correo = request.form['correo']
    contrasena = request.form['contrasena']
    cursor.execute("SELECT UsuarioID, NombreCompleto, CorreoElectronico, Contrasena FROM Usuarios WHERE CorreoElectronico = ?", (correo,))
    user = cursor.fetchone()
    if user:
        user_id, nombre, correo_db, hashed_password = user
        if bcrypt.checkpw(contrasena.encode('utf-8'), hashed_password.encode('utf-8')):
            cursor.execute("UPDATE Usuarios SET UltimoAcceso=GETDATE(), Estado='Activo' WHERE UsuarioID=?", (user_id,))
            conn.commit()
            session['usuario_id'] = user_id
            session['nombre'] = nombre
            session['correo'] = correo_db
            return redirect(url_for('principal'))
        else:
            flash("❌ Contraseña incorrecta", "error")
    else:
        flash("⚠️ El correo no está registrado", "error")
    return redirect(url_for('home'))

# ----------- PRINCIPAL ----------
@app.route('/principal')
def principal():
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    user_id = session['usuario_id']
    cursor.execute("""
        SELECT NombreCompleto, CorreoElectronico, FechaRegistro, UltimoAcceso, Estado
        FROM Usuarios WHERE UsuarioID=?
    """, (user_id,))
    nombre, correo_db, fecha_creacion, ultimo_acceso, estado = cursor.fetchone()

    usuarios_activos  = kpi_usuarios_activos()
    reportes_total    = kpi_reportes_total()
    exportaciones_tot = kpi_exportaciones_total()
    ultimas10         = ultimas_operaciones(10)
    reportes          = obtener_reportes()

    return render_template(
        'principal.html',
        nombre=nombre, correo=correo_db,
        fecha_creacion=fecha_creacion, ultimo_acceso=ultimo_acceso, estado=estado,
        usuarios_activos=usuarios_activos,
        reportes_total=reportes_total,
        exportaciones_tot=exportaciones_tot,
        ultimas10=ultimas10,
        reportes=reportes
    )

# ----------- SUBIR PDF (REGISTRO DE COMPRA) ----------
@app.route('/pdf/subir', methods=['POST'])
def subir_pdf():
    if 'usuario_id' not in session:
        flash("Inicia sesión para continuar", "error")
        return redirect(url_for('home'))

    file = request.files.get('archivo')
    if not file or file.filename == '':
        flash("Selecciona un archivo PDF", "error")
        return redirect(url_for('principal') + "#subir")

    filename = secure_filename(file.filename)
    if not filename.lower().endswith(".pdf"):
        flash("Solo se permiten archivos PDF", "error")
        return redirect(url_for('principal') + "#subir")

    save_path = os.path.join(UPLOAD_DIR, filename)
    file.save(save_path)

    session['ultimo_archivo'] = save_path
    registrar_operacion(session['usuario_id'], 'PDF', filename, save_path, 'CREADO')
    flash("Archivo subido correctamente", "success")
    return redirect(url_for('principal') + "#subir")

# ----------- PROCESAR PDF (REGISTRO DE COMPRA) ----------
@app.route('/procesar', methods=['POST'])
def procesar():
    if 'usuario_id' not in session:
        flash("Inicia sesión para continuar", "error")
        return redirect(url_for('home'))

    ruta = session.get('ultimo_archivo')
    if not ruta or not os.path.exists(ruta):
        flash("No hay archivo para procesar. Sube un PDF primero.", "error")
        return redirect(url_for('principal') + "#subir")

    try:
        datos = extraer_datos(ruta)
        RESULTADOS_EXTRAIDOS.append(datos)
        registrar_operacion(session['usuario_id'], 'PDF', os.path.basename(ruta), ruta, 'PROCESADO')
        flash("Procesamiento completado. Datos extraídos listos para exportar.", "success")
    except Exception as e:
        flash(f"Error al procesar el PDF: {e}", "error")

    return redirect(url_for('principal') + "#subir")

# ----------- EXPORTAR A EXCEL (REGISTRO DE COMPRA) ----------
@app.route('/exportar', methods=['GET'])
def exportar():
    if 'usuario_id' not in session:
        flash("Inicia sesión para continuar", "error")
        return redirect(url_for('home'))

    if not RESULTADOS_EXTRAIDOS:
        flash("No hay datos procesados para exportar.", "error")
        return redirect(url_for('principal') + "#subir")

    df = pd.DataFrame(RESULTADOS_EXTRAIDOS)
    export_name = f"resultados_facturas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    export_path = os.path.join(EXPORT_DIR, export_name)

    try:
        df.to_excel(export_path, index=False)
        registrar_operacion(session['usuario_id'], 'EXPORTACION', export_name, export_path, 'EXPORTADO')
    except Exception as e:
        flash(f"No se pudo generar el Excel: {e}", "error")
        return redirect(url_for('principal') + "#subir")

    return send_file(export_path, as_attachment=True, download_name=export_name)

# ----------- SUBIR PDF EMISOR (REGISTRO DE EMISOR) ----------
@app.route('/emisor/subir', methods=['POST'])
def subir_emisor():
    if 'usuario_id' not in session:
        flash("Inicia sesión para continuar", "error")
        return redirect(url_for('home'))

    file = request.files.get('archivo_emisor')
    if not file or file.filename == '':
        flash("Selecciona un archivo PDF de emisor", "error")
        return redirect(url_for('principal') + "#emisor")

    filename = secure_filename(file.filename)
    if not filename.lower().endswith(".pdf"):
        flash("Solo se permiten archivos PDF", "error")
        return redirect(url_for('principal') + "#emisor")

    save_path = os.path.join(UPLOAD_DIR, f"emisor_{filename}")
    file.save(save_path)

    session['ultimo_archivo_emisor'] = save_path
    registrar_operacion(session['usuario_id'], 'PDF_EMISOR', filename, save_path, 'CREADO')
    flash("Archivo de emisor subido correctamente", "success")
    return redirect(url_for('principal') + "#emisor")

# ----------- PROCESAR PDF EMISOR ----------
@app.route('/emisor/procesar', methods=['POST'])
def procesar_emisor():
    if 'usuario_id' not in session:
        flash("Inicia sesión para continuar", "error")
        return redirect(url_for('home'))

    ruta = session.get('ultimo_archivo_emisor')
    if not ruta or not os.path.exists(ruta):
        flash("No hay archivo de emisor para procesar. Sube un PDF primero.", "error")
        return redirect(url_for('principal') + "#emisor")

    try:
        texto = pdf_a_texto_emisor(ruta)
        datos = extraer_campos_emisor(texto)
        guardar_en_excel_emisor(datos, RUTA_EXCEL_EMISOR)
        registrar_operacion(session['usuario_id'], 'EMISOR', os.path.basename(ruta), ruta, 'PROCESADO')
        flash("Emisor procesado y agregado al Excel acumulado.", "success")
    except Exception as e:
        flash(f"Error al procesar el PDF de emisor: {e}", "error")

    return redirect(url_for('principal') + "#emisor")

# ----------- EXPORTAR EMISOR (DESCARGAR EXCEL ACUMULADO) ----------
@app.route('/emisor/exportar', methods=['GET'])
def exportar_emisor():
    if 'usuario_id' not in session:
        flash("Inicia sesión para continuar", "error")
        return redirect(url_for('home'))

    if not os.path.exists(RUTA_EXCEL_EMISOR):
        flash("No hay datos de emisores procesados para exportar.", "error")
        return redirect(url_for('principal') + "#emisor")

    df = pd.read_excel(RUTA_EXCEL_EMISOR)
    export_name = f"emisores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    export_path = os.path.join(EXPORT_DIR, export_name)

    try:
        df.to_excel(export_path, index=False)
        registrar_operacion(session['usuario_id'], 'EXPORTACION', export_name, export_path, 'EXPORTADO')
    except Exception as e:
        flash(f"No se pudo generar el Excel de emisores: {e}", "error")
        return redirect(url_for('principal') + "#emisor")

    return send_file(export_path, as_attachment=True, download_name=export_name)

# ----------- DESCARGAR / VER REPORTE DESDE TABLA -----------
@app.route('/operacion/<int:op_id>/descargar')
def descargar_operacion(op_id):
    op = obtener_operacion(op_id)
    if not op:
        flash("Operación no encontrada", "error")
        return redirect(url_for('principal') + "#reportes")
    _, nombre, ruta, tipo, _, _ = op
    if not os.path.exists(ruta):
        flash("Archivo no disponible en el servidor.", "error")
        return redirect(url_for('principal') + "#reportes")
    return send_file(ruta, as_attachment=True, download_name=nombre)

@app.route('/operacion/<int:op_id>/ver')
def ver_operacion(op_id):
    op = obtener_operacion(op_id)
    if not op:
        flash("Operación no encontrada", "error")
        return redirect(url_for('principal') + "#reportes")
    _, nombre, ruta, tipo, _, _ = op
    if not os.path.exists(ruta) or not ruta.lower().endswith(".pdf"):
        flash("Vista previa solo disponible para PDF.", "error")
        return redirect(url_for('principal') + "#reportes")
    return send_file(ruta, as_attachment=False, download_name=nombre)

# ----------- EDITAR DATOS ----------
@app.route('/editar_usuario', methods=['POST'])
def editar_usuario():
    if 'usuario_id' not in session:
        return jsonify({"mensaje": "No autorizado"}), 401

    nombre = request.form['nombre']
    correo = request.form['correo']
    usuario_id = session['usuario_id']

    try:
        cursor.execute("""
            UPDATE Usuarios 
            SET NombreCompleto = ?, CorreoElectronico = ? 
            WHERE UsuarioID = ?
        """, (nombre, correo, usuario_id))
        conn.commit()
        session['nombre'] = nombre
        session['correo'] = correo
        return jsonify({"mensaje": "Datos actualizados correctamente"})
    except Exception as e:
        return jsonify({"mensaje": f"Error: {e}"}), 500

# ----------- CAMBIAR PASSWORD ----------
@app.route('/cambiar_password', methods=['POST'])
def cambiar_password():
    if 'usuario_id' not in session:
        return jsonify({"mensaje": "No autorizado"}), 401

    actual = request.form['actual']
    nueva = request.form['nueva']
    confirmar = request.form['confirmar']
    usuario_id = session['usuario_id']

    cursor.execute("SELECT Contrasena FROM Usuarios WHERE UsuarioID = ?", (usuario_id,))
    hashed_actual = cursor.fetchone()

    if not hashed_actual or not bcrypt.checkpw(actual.encode('utf-8'), hashed_actual[0].encode('utf-8')):
        return jsonify({"mensaje": "Contraseña actual incorrecta"}), 400

    if nueva != confirmar:
        return jsonify({"mensaje": "Las contraseñas no coinciden"}), 400

    hashed_nueva = bcrypt.hashpw(nueva.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("UPDATE Usuarios SET Contrasena=? WHERE UsuarioID=?", (hashed_nueva.decode('utf-8'), usuario_id))
    conn.commit()

    return jsonify({"mensaje": "Contraseña cambiada correctamente"})

# ----------- LOGOUT ----------
@app.route('/logout')
def logout():
    if 'usuario_id' in session:
        cursor.execute("UPDATE Usuarios SET Estado='Inactivo' WHERE UsuarioID=?", (session['usuario_id'],))
        conn.commit()
    session.clear()
    flash("👋 Sesión cerrada correctamente", "info")
    return redirect(url_for('home'))

# ----------- MAIN ----------
if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)
