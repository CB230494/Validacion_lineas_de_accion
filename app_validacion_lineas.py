import streamlit as st
from fpdf import FPDF
from io import BytesIO
from PIL import Image
import datetime

st.set_page_config(page_title="Validación de Líneas de Acción", layout="centered")

class PDFValidacion(FPDF):
    def header(self):
        try:
            self.image("logo.png", 10, 8, 22)
        except:
            pass
        self.set_font("Arial", "B", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, "Estrategia Sembremos Seguridad", ln=True, align="C")
        self.cell(0, 8, "Informe de Validación de Líneas de Acción", ln=True, align="C")
        self.ln(8)
        self.line(10, self.get_y(), 200, self.get_y())

    def footer(self):
        self.set_y(-20)
        self.set_font("Arial", "I", 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"Página {self.page_no()} - Modelo Preventivo de Gestión Policial - Estrategia Sembremos Seguridad", align="C")

    def add_section_title(self, title):
        self.ln(10)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)

    def add_text_field(self, label, content):
        self.set_font("Arial", "", 11)
        texto = f"{label}: {content}" if content else f"{label}: "
        self.cell(0, 8, texto[:100], ln=True)

    def add_checkbox_list(self, title, items):
        self.add_section_title(title)
        for label, checked in items.items():
            estado = "SI" if checked else "NO"
            self.add_text_field(label, estado)

    def add_validation_table(self, items):
        self.add_section_title("Contenido validado y tipo de modificación")
        self.set_font("Arial", "B", 11)
        self.cell(70, 8, "Elemento validado", 1, 0, "C")
        self.cell(30, 8, "¿Fue validado?", 1, 0, "C")
        self.cell(90, 8, "Tipo de cambio realizado", 1, 1, "C")
        self.set_font("Arial", "", 11)
        for item in items:
            elemento = item.get("elemento", "")
            validado = "SI" if item.get("validado") == "✔" else "NO"
            tipo = item.get("tipo_cambio", "")
            if "Metas" in elemento:
                cambio = f"Bimestrales ({'X' if tipo == 'Bimestrales' else ' '})   Anuales ({'X' if tipo == 'Anuales' else ' '})"
            elif "Lider" in elemento or "Líder" in elemento:
                cambio = "Modificación de líder estratégico (X)" if tipo == "Modificación de líder estratégico" else "Modificación de líder estratégico ( )"
            else:
                cambio = f"Total ({'X' if tipo == 'Total' else ' '})   Parcial ({'X' if tipo == 'Parcial' else ' '})"
            self.cell(70, 8, elemento[:40], 1)
            self.cell(30, 8, validado, 1, 0, "C")
            self.cell(90, 8, cambio, 1, 1)

    def add_observaciones(self, texto):
        self.add_section_title("Observaciones")
        self.set_font("Arial", "", 11)
        if texto:
            for linea in str(texto).splitlines():
                self.cell(0, 8, linea[:100], ln=True)
        else:
            self.cell(0, 8, "Sin observaciones", ln=True)

    def add_adjuntos(self, archivos):
        if not archivos:
            return
        self.add_section_title("Archivos adjuntos")
        for archivo in archivos:
            nombre = archivo.name
            if nombre.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    img = Image.open(archivo)
                    w, h = img.size
                    max_w = 180
                    ratio = max_w / w
                    img_height = h * ratio
                    archivo.seek(0)
                    self.image(archivo, x=15, w=max_w, h=img_height)
                    self.ln(10)
                except Exception:
                    self.cell(0, 8, f"Imagen no soportada: {nombre}", ln=True)
            elif nombre.lower().endswith(".pdf"):
                self.cell(0, 8, f"PDF adjunto: {nombre}", ln=True)

def generar_pdf_validacion(datos):
    pdf = PDFValidacion()
    pdf.add_page()
    pdf.add_text_field("Período 2025-2026", datos.get("periodo"))
    pdf.add_text_field("Fecha", datos.get("fecha"))
    pdf.add_text_field("Delegación", datos.get("delegacion"))
    pdf.add_checkbox_list("Participación en el proceso de validación del gobierno local", datos.get("participacion", {}))
    pdf.add_text_field("¿Se emitió un oficio de validación?", datos.get("oficio_emitido"))
    pdf.add_text_field("Número de oficio", datos.get("numero_oficio"))
    pdf.add_text_field("¿Se realizaron modificaciones en las líneas de acción?", datos.get("modificaciones"))
    pdf.add_validation_table(datos.get("validaciones", []))
    pdf.add_observaciones(datos.get("observaciones"))
    pdf.add_adjuntos(datos.get("adjuntos", []))
    buffer = BytesIO()
    pdf.output(buffer, 'F')
    buffer.seek(0)
    return buffer

# --- FORMULARIO STREAMLIT ---
st.title("Validación de Líneas de Acción")

with st.form("formulario_validacion"):
    periodo = st.text_input("Período 2025-2026", value="Primer semestre")
    fecha = st.date_input("Fecha")
    delegacion = st.text_input("Delegación")

    st.markdown("### Participación en el proceso de validación del gobierno local")
    participacion = {
        "Alcalde / Alcaldesa": st.checkbox("Alcalde / Alcaldesa"),
        "Vicealcalde / Vicealcaldesa": st.checkbox("Vicealcalde / Vicealcaldesa"),
        "Mesa de articulación": st.checkbox("Mesa de articulación")
    }

    oficio_emitido = st.radio("¿Se emitió un oficio de validación?", ["Sí", "No"])
    numero_oficio = st.text_input("Número de oficio (si aplica)")
    modificaciones = st.radio("¿Se realizaron modificaciones?", ["Sí", "No"])

    st.markdown("### Contenido validado y tipo de modificación")
    validaciones = []
    opciones_tipo = {
        "Línea de acción": ["Total", "Parcial"],
        "Acción estratégica": ["Total", "Parcial"],
        "Indicadores": ["Total", "Parcial"],
        "Metas": ["Bimestrales", "Anuales"],
        "Lider estratégico": ["Modificación de líder estratégico"]
    }
    for e in opciones_tipo:
        col1, col2 = st.columns(2)
        with col1:
            validado = st.checkbox(f"{e} validado", key=f"{e}_validado")
        with col2:
            tipo = st.selectbox(f"Tipo de cambio - {e}", opciones_tipo[e], key=f"{e}_tipo")
        validaciones.append({
            "elemento": e,
            "validado": "✔" if validado else "✘",
            "tipo_cambio": tipo
        })

    observaciones = st.text_area("Observaciones")
    archivos = st.file_uploader("Subir archivos adjuntos (imágenes o PDF)", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)
    submit = st.form_submit_button("📥 Generar PDF")

if submit:
    datos = {
        "periodo": periodo,
        "fecha": fecha.strftime("%d/%m/%Y"),
        "delegacion": delegacion,
        "participacion": participacion,
        "oficio_emitido": oficio_emitido,
        "numero_oficio": numero_oficio,
        "modificaciones": modificaciones,
        "validaciones": validaciones,
        "observaciones": observaciones,
        "adjuntos": archivos
    }

    pdf_buffer = generar_pdf_validacion(datos)
    nombre_archivo = f"Validacion_Lineas_{delegacion.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
    st.download_button("Descargar Informe PDF", data=pdf_buffer, file_name=nombre_archivo, mime="application/pdf")
