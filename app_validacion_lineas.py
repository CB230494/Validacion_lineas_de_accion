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

    def add_text_field(self, label, content):
        self.set_font("Arial", "", 11)
        self.cell(0, 8, f"{label}: {content}", ln=True)

    def add_validation_table_custom(self, filas):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Contenido validado y tipo de modificación", ln=True)
        self.set_font("Arial", "B", 11)
        self.cell(70, 8, "Elemento validado", 1, 0, "C")
        self.cell(30, 8, "¿Fue validado?", 1, 0, "C")
        self.cell(90, 8, "Tipo de cambio realizado", 1, 1, "C")
        self.set_font("Arial", "", 11)

        for fila in filas:
            tipo = fila["tipo_cambio"].strip()
            if fila["elemento"] == "Metas":
                if tipo not in ["Bimestrales", "Anuales"]:
                    tipo_texto = "Bimestrales ( )   Anuales ( )"
                else:
                    tipo_texto = f"Bimestrales ({'X' if tipo == 'Bimestrales' else ' '})   Anuales ({'X' if tipo == 'Anuales' else ' '})"
            elif fila["elemento"] == "Líder estratégico":
                tipo_texto = "Modificación de líder estratégico (X)" if tipo == "Modificación de líder estratégico" else "Modificación de líder estratégico ( )"
            else:
                if tipo not in ["Total", "Parcial"]:
                    tipo_texto = "Total ( )   Parcial ( )"
                else:
                    tipo_texto = f"Total ({'X' if tipo == 'Total' else ' '})   Parcial ({'X' if tipo == 'Parcial' else ' '})"
            self.cell(70, 8, fila["elemento"], 1)
            self.cell(30, 8, fila["validado"], 1, 0, "C")
            self.cell(90, 8, tipo_texto, 1, 1)

    def add_observaciones(self, texto):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Observaciones", ln=True)
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, texto or "Sin observaciones")

    def add_adjuntos(self, archivos):
        imagenes = [a for a in archivos if a.name.lower().endswith((".png", ".jpg", ".jpeg"))]
        pdfs = [a for a in archivos if a.name.lower().endswith(".pdf")]

        if imagenes:
            self.add_page()
            self.set_font("Arial", "B", 12)
            self.set_y(30)
            self.cell(0, 10, "Archivos adjuntos", ln=True)
            self.set_y(65)  # margen ajustado más arriba
            for archivo in imagenes:
                try:
                    img = Image.open(archivo)
                    w, h = img.size
                    max_w = 120
                    ratio = max_w / w
                    img_height = h * ratio
                    archivo.seek(0)
                    x_centro = (210 - max_w) / 2
                    self.image(archivo, x=x_centro, y=self.get_y(), w=max_w, h=img_height)
                    self.ln(img_height + 10)
                except:
                    self.cell(0, 8, f"Imagen no soportada: {archivo.name}", ln=True)

        if pdfs:
            self.add_page()
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "PDFs adjuntos", ln=True)
            self.set_font("Arial", "", 11)
            for archivo in pdfs:
                self.cell(0, 8, f"PDF adjunto: {archivo.name}", ln=True)

def generar_pdf_validacion(datos):
    pdf = PDFValidacion()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Período 2025-2026", ln=True)
    pdf.add_text_field("Fecha", datos.get("fecha"))
    pdf.add_text_field("Delegación", datos.get("delegacion"))
    pdf.add_text_field("¿Se emitió un oficio de validación?", datos.get("oficio_emitido"))
    pdf.add_text_field("Número de oficio", datos.get("numero_oficio"))
    pdf.add_text_field("¿Se realizaron modificaciones en las líneas de acción?", datos.get("modificaciones"))
    pdf.add_validation_table_custom(datos["validaciones"])
    pdf.add_observaciones(datos.get("observaciones"))
    pdf.add_adjuntos(datos.get("adjuntos", []))
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# ---- FORMULARIO STREAMLIT ----
st.title("Validación de Líneas de Acción")
st.subheader("Período 2025-2026")

with st.form("formulario_validacion"):
    fecha = st.date_input("Fecha")
    delegacion = st.text_input("Delegación")
    oficio_emitido = st.radio("¿Se emitió un oficio de validación?", ["Sí", "No"])
    numero_oficio = st.text_input("Número de oficio (si aplica)")
    modificaciones = st.radio("¿Se realizaron modificaciones en las líneas de acción?", ["Sí", "No"])

    st.markdown("### Contenido validado y tipo de modificación")
    elementos = ["Línea de acción", "Acción estratégica", "Indicadores", "Metas", "Líder estratégico"]
    opciones_tipo = {
        "Línea de acción": ["", "Total", "Parcial"],
        "Acción estratégica": ["", "Total", "Parcial"],
        "Indicadores": ["", "Total", "Parcial"],
        "Metas": ["", "Bimestrales", "Anuales"],
        "Líder estratégico": ["", "Modificación de líder estratégico"]
    }

    validaciones = []
    for e in elementos:
        st.markdown(f"**{e}**")
        col1, col2 = st.columns(2)
        with col1:
            validado_key = f"{e}_val"
            validado = st.radio(f"¿Fue validado? - {e}", ["Sí", "No"], key=validado_key)
        if validado == "No":
            with col2:
                tipo_key = f"{e}_tipo"
                tipo = st.selectbox(f"Tipo de cambio - {e}", opciones_tipo[e], key=tipo_key)
        else:
            tipo = ""
        validaciones.append({
            "elemento": e,
            "validado": "SI" if validado == "Sí" else "NO",
            "tipo_cambio": tipo
        })

    observaciones = st.text_area("Observaciones")
    archivos = st.file_uploader("Subir archivos adjuntos (imágenes o PDF)", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

    submit = st.form_submit_button("📥 Generar PDF")

if submit:
    datos = {
        "fecha": fecha.strftime("%d/%m/%Y"),
        "delegacion": delegacion,
        "oficio_emitido": oficio_emitido,
        "numero_oficio": numero_oficio,
        "modificaciones": modificaciones,
        "validaciones": validaciones,
        "observaciones": observaciones,
        "adjuntos": archivos
    }

    pdf_buffer = generar_pdf_validacion(datos)
    nombre_archivo = f"Validacion_Lineas_{delegacion.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
    st.download_button("📥 Descargar Informe PDF", data=pdf_buffer, file_name=nombre_archivo, mime="application/pdf")
