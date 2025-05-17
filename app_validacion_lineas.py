import streamlit as st
from fpdf import FPDF
from io import BytesIO
import datetime

st.set_page_config(page_title="Validación de Líneas de Acción", layout="centered")

# ---- CLASE PDF ACTUALIZADA CON FPDF2 ----
class PDFValidacion(FPDF):
    def header(self):
        self.image('logo.png', 10, 8, 22)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, 'Estrategia Sembremos Seguridad', ln=True, align='C')
        self.cell(0, 8, 'Informe de Validación de Líneas de Acción', ln=True, align='C')
        self.ln(10)
        self.set_line_width(0.6)
        self.line(10, 28, 200, 28)

    def footer(self):
        self.set_y(-20)
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f'Página {self.page_no()} - Modelo Preventivo de Gestión Policial', align='C')

    def add_section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.ln(10)
        self.cell(0, 10, title, ln=True)

    def add_text_field(self, label, content):
        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 8, f"{label}: {content}")

    def add_checkbox_list(self, title, items):
        self.add_section_title(title)
        for label, checked in items.items():
            status = '✔' if checked else '✘'
            self.add_text_field(f"{status} {label}", "")

    def add_validation_table(self, items):
        self.add_section_title("Contenido Validado y Tipo de Modificación")
        self.set_font('Helvetica', 'B', 11)
        self.cell(70, 8, "Elemento Validado", border=1, align='C')
        self.cell(30, 8, "¿Fue validado?", border=1, align='C')
        self.cell(90, 8, "Tipo de cambio", border=1, align='C')
        self.ln()
        self.set_font('Helvetica', '', 11)
        for item in items:
            self.cell(70, 8, item['elemento'], border=1)
            self.cell(30, 8, item['validado'], border=1, align='C')
            self.cell(90, 8, item['tipo_cambio'], border=1)
            self.ln()

    def add_observaciones(self, texto):
        self.add_section_title("Observaciones")
        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 8, texto)

def generar_pdf_validacion(datos):
    pdf = PDFValidacion()
    pdf.add_page()
    pdf.add_text_field("Período 2025-2026", datos["periodo"])
    pdf.add_text_field("Fecha", datos["fecha"])
    pdf.add_text_field("Delegación", datos["delegacion"])
    pdf.add_checkbox_list("Participación en el proceso de validación del gobierno local", datos["participacion"])
    pdf.add_text_field("¿Se emitió un oficio de validación?", datos["oficio_emitido"])
    pdf.add_text_field("Número de oficio", datos["numero_oficio"])
    pdf.add_text_field("¿Se realizaron modificaciones en las líneas de acción?", datos["modificaciones"])
    pdf.add_validation_table(datos["validaciones"])
    pdf.add_observaciones(datos["observaciones"])

    buffer = BytesIO()
    pdf.output(buffer, 'F')  # Con 'F' para escribir en buffer
    buffer.seek(0)
    return buffer

# ---- FORMULARIO EN STREAMLIT ----
st.title("📄 Validación de Líneas de Acción")

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
    modificaciones = st.radio("¿Se realizaron modificaciones en las líneas de acción?", ["Sí", "No"])

    st.markdown("### Contenido validado y tipo de modificación")
    validaciones = []
    elementos = [
        "Línea de acción", "Acción estratégica", "Indicadores", "Metas", "Líder estratégico"
    ]
    for e in elementos:
        col1, col2 = st.columns(2)
        with col1:
            validado = st.checkbox(f"{e} validado", key=f"{e}_validado")
        with col2:
            tipo = st.selectbox(f"Tipo de cambio - {e}", ["Total", "Parcial", "Anuales", "Bimestrales", "Modificación de líder"], key=f"{e}_tipo")
        validaciones.append({
            "elemento": e,
            "validado": "✔" if validado else "✘",
            "tipo_cambio": tipo
        })

    observaciones = st.text_area("Observaciones")

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
        "observaciones": observaciones
    }

    pdf_buffer = generar_pdf_validacion(datos)
    nombre_archivo = f"Validacion_Lineas_{delegacion.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"

    st.download_button(
        label="⬇️ Descargar Informe en PDF",
        data=pdf_buffer,
        file_name=nombre_archivo,
        mime="application/pdf"
    )
