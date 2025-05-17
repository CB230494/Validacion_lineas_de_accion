import streamlit as st
from fpdf import FPDF
from io import BytesIO
import datetime

st.set_page_config(page_title="Validacion de Lineas de Accion", layout="centered")

class PDFValidacion(FPDF):
    def header(self):
        try:
            self.image("logo.png", 10, 8, 22)
        except:
            pass
        self.set_font("Arial", "B", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, "Estrategia Sembremos Seguridad", ln=True, align="C")
        self.cell(0, 8, "Informe de Validacion de Lineas de Accion", ln=True, align="C")
        self.ln(8)
        self.line(10, self.get_y(), 200, self.get_y())

    def footer(self):
        self.set_y(-20)
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, f"Pagina {self.page_no()} - Modelo Preventivo de Gestion Policial", align="C")

    def add_section_title(self, title):
        self.ln(10)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, str(title), ln=True)

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
        self.add_section_title("Contenido Validado y Tipo de Modificacion")
        self.set_font("Arial", "B", 11)
        self.cell(70, 8, "Elemento Validado", 1, 0, "C")
        self.cell(30, 8, "Validado", 1, 0, "C")
        self.cell(90, 8, "Tipo de cambio", 1, 1, "C")
        self.set_font("Arial", "", 11)
        for item in items:
            self.cell(70, 8, str(item.get("elemento", ""))[:40], 1)
            self.cell(30, 8, "SI" if item.get("validado") == "✔" else "NO", 1, 0, "C")
            self.cell(90, 8, str(item.get("tipo_cambio", ""))[:45], 1, 1)

    def add_observaciones(self, texto):
        self.add_section_title("Observaciones")
        self.set_font("Arial", "", 11)
        if texto:
            for linea in str(texto).splitlines():
                self.cell(0, 8, linea[:100], ln=True)
        else:
            self.cell(0, 8, "Sin observaciones", ln=True)

def generar_pdf_validacion(datos):
    pdf = PDFValidacion()
    pdf.add_page()
    pdf.add_text_field("Periodo 2025-2026", datos.get("periodo"))
    pdf.add_text_field("Fecha", datos.get("fecha"))
    pdf.add_text_field("Delegacion", datos.get("delegacion"))
    pdf.add_checkbox_list("Participacion en el proceso de validacion del gobierno local", datos.get("participacion", {}))
    pdf.add_text_field("Oficio de validacion emitido", datos.get("oficio_emitido"))
    pdf.add_text_field("Numero de oficio", datos.get("numero_oficio"))
    pdf.add_text_field("Modificaciones realizadas", datos.get("modificaciones"))
    pdf.add_validation_table(datos.get("validaciones", []))
    pdf.add_observaciones(datos.get("observaciones"))
    buffer = BytesIO()
    pdf.output(buffer, 'F')
    buffer.seek(0)
    return buffer

# --- FORMULARIO STREAMLIT ---
st.title("Validacion de Lineas de Accion")

with st.form("formulario_validacion"):
    periodo = st.text_input("Periodo 2025-2026", value="Primer semestre")
    fecha = st.date_input("Fecha")
    delegacion = st.text_input("Delegacion")

    st.markdown("### Participacion en el proceso de validacion del gobierno local")
    participacion = {
        "Alcalde / Alcaldesa": st.checkbox("Alcalde / Alcaldesa"),
        "Vicealcalde / Vicealcaldesa": st.checkbox("Vicealcalde / Vicealcaldesa"),
        "Mesa de articulacion": st.checkbox("Mesa de articulacion")
    }

    oficio_emitido = st.radio("¿Se emitio un oficio de validacion?", ["Si", "No"])
    numero_oficio = st.text_input("Numero de oficio (si aplica)")
    modificaciones = st.radio("¿Se realizaron modificaciones?", ["Si", "No"])

    st.markdown("### Contenido validado y tipo de modificacion")
    validaciones = []
    elementos = ["Linea de accion", "Accion estrategica", "Indicadores", "Metas", "Lider estrategico"]
    for e in elementos:
        col1, col2 = st.columns(2)
        with col1:
            validado = st.checkbox(f"{e} validado", key=f"{e}_validado")
        with col2:
            tipo = st.selectbox(f"Tipo de cambio - {e}", ["Total", "Parcial", "Anuales", "Bimestrales", "Modificacion de lider"], key=f"{e}_tipo")
        validaciones.append({
            "elemento": e,
            "validado": "✔" if validado else "✘",
            "tipo_cambio": tipo
        })

    observaciones = st.text_area("Observaciones")
    submit = st.form_submit_button("Generar PDF")

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
    st.download_button("Descargar Informe PDF", data=pdf_buffer, file_name=nombre_archivo, mime="application/pdf")


