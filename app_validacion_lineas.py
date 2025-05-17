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
        self.add_page()
        self.ln(10)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)

    def add_text_field(self, label, content):
        self.set_font("Arial", "", 11)
        texto = f"{label}: {content}" if content else f"{label}: "
        self.cell(0, 8, texto[:100], ln=True)

    def add_validation_table_static(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Contenido validado y tipo de modificación", ln=True)
        self.set_font("Arial", "B", 11)
        self.cell(70, 8, "Elemento validado", 1, 0, "C")
        self.cell(30, 8, "¿Fue validado?", 1, 0, "C")
        self.cell(90, 8, "Tipo de cambio realizado", 1, 1, "C")
        self.set_font("Arial", "", 11)
        filas = [
            ("Línea de acción", "NO", "Total ( )   Parcial ( )"),
            ("Acción estratégica", "NO", "Total ( )   Parcial ( )"),
            ("Indicadores", "NO", "Total ( )   Parcial ( )"),
            ("Metas", "NO", "Bimestrales ( )   Anuales ( )"),
            ("Líder estratégico", "NO", "Modificación de líder estratégico ( )")
        ]
        for fila in filas:
            self.cell(70, 8, fila[0], 1)
            self.cell(30, 8, fila[1], 1, 0, "C")
            self.cell(90, 8, fila[2], 1, 1)

    def add_observaciones(self, texto):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Observaciones", ln=True)
        self.set_font("Arial", "", 11)
        if texto:
            for linea in str(texto).splitlines():
                self.cell(0, 8, linea[:100], ln=True)
        else:
            self.cell(0, 8, "Sin observaciones", ln=True)

    def add_adjuntos(self, archivos):
        if not archivos:
            return
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Archivos adjuntos", ln=True)
        self.set_font("Arial", "", 11)
        for archivo in archivos:
            nombre = archivo.name
            if nombre.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    self.add_page()
                    img = Image.open(archivo)
                    w, h = img.size
                    max_w = 120
                    ratio = max_w / w
                    img_height = h * ratio
                    archivo.seek(0)
                    x_centro = (210 - max_w) / 2
                    self.image(archivo, x=x_centro, w=max_w, h=img_height)
                    self.ln(5)
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
    pdf.add_text_field("¿Se emitió un oficio de validación?", datos.get("oficio_emitido"))
    pdf.add_text_field("Número de oficio", datos.get("numero_oficio"))
    pdf.add_text_field("¿Se realizaron modificaciones en las líneas de acción?", datos.get("modificaciones"))
    pdf.add_validation_table_static()
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
    st.markdown("### Oficio de Validación")
    oficio_emitido = st.radio("¿Se emitió un oficio de validación?", ["Sí", "No"])
    numero_oficio = st.text_input("Número de oficio (si aplica)")
    modificaciones = st.radio("¿Se realizaron modificaciones?", ["Sí", "No"])
    st.markdown("### Contenido validado y tipo de modificación")
    st.markdown("*Esta sección se genera automáticamente en el PDF con todos los campos visibles.*")
    observaciones = st.text_area("Observaciones")
    archivos = st.file_uploader("Subir archivos adjuntos (imágenes o PDF)", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)
    submit = st.form_submit_button("📥 Generar PDF")

if submit:
    datos = {
        "periodo": periodo,
        "fecha": fecha.strftime("%d/%m/%Y"),
        "delegacion": delegacion,
        "oficio_emitido": oficio_emitido,
        "numero_oficio": numero_oficio,
        "modificaciones": modificaciones,
        "observaciones": observaciones,
        "adjuntos": archivos
    }

    pdf_buffer = generar_pdf_validacion(datos)
    nombre_archivo = f"Validacion_Lineas_{delegacion.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
    st.download_button("Descargar Informe PDF", data=pdf_buffer, file_name=nombre_archivo, mime="application/pdf")

