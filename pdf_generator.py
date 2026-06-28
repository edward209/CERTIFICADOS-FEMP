from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from pypdf import PdfReader, PdfWriter
import qrcode
import io
import os


def crear_qr(datos):
    os.makedirs("static/certificados/qr", exist_ok=True)

    codigo = datos["codigo"]
    url_validacion = f"https://certificados-femp.onrender.com/verificar?codigo={codigo}"

    ruta_qr = f"static/certificados/qr/{codigo}.png"

    qr = qrcode.make(url_validacion)
    qr.save(ruta_qr)

    return ruta_qr


def crear_pdf_certificado(datos):
    plantilla_pdf = f"static/certificados/plantillas/{datos['plantilla']}"
    salida_pdf = f"static/certificados/generados/{datos['codigo']}.pdf"

    os.makedirs("static/certificados/generados", exist_ok=True)

    ruta_qr = crear_qr(datos)

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(A4))
    ancho, alto = landscape(A4)

    c.setFillColorRGB(0, 0, 0)

    # =========================
    # PÁGINA 1
    # =========================

    # Nombre del estudiante
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(ancho / 2, 267, datos["nombre"].upper())

    c.showPage()

    # =========================
    # PÁGINA 2
    # =========================

    # Código del certificado
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(ancho / 2, 163, datos["codigo"])

    # Cédula del estudiante
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(ancho / 2, 148, datos["cedula"])

    # QR
    c.drawImage(ruta_qr, 700, 85, width=80, height=80)

    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(740, 75, "VALIDAR CERTIFICADO")

    c.save()
    packet.seek(0)

    overlay_pdf = PdfReader(packet)
    plantilla = PdfReader(plantilla_pdf)
    writer = PdfWriter()

    for i in range(len(plantilla.pages)):
        pagina_base = plantilla.pages[i]

        if i < len(overlay_pdf.pages):
            pagina_base.merge_page(overlay_pdf.pages[i])

        writer.add_page(pagina_base)

    with open(salida_pdf, "wb") as archivo_salida:
        writer.write(archivo_salida)

    return salida_pdf