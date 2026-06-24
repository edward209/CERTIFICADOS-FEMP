from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from pypdf import PdfReader, PdfWriter, Transformation
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


def crear_overlay(datos, ruta_qr):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(A4))
    ancho, alto = landscape(A4)

    c.setFillColorRGB(0, 0, 0)

    # =========================
    # PÁGINA 1
    # =========================

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(ancho / 2, 267, datos["nombre"].upper())

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(114, 219, datos["curso"].upper())

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(196, 197, datos["duracion"].upper())

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(716, 198, datos["fecha"].upper())

    c.showPage()

    # =========================
    # PÁGINA 2
    # =========================

    c.setFillColorRGB(0, 0, 0)

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(ancho / 2, 163, datos["codigo"])

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(ancho / 2, 148, datos["cedula"])

    c.drawImage(ruta_qr, 700, 85, width=80, height=80)

    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(740, 75, "VALIDAR CERTIFICADO")

    c.save()
    packet.seek(0)

    return PdfReader(packet)


def crear_pdf_certificado(datos):
    plantilla_pdf = f"static/certificados/plantillas/{datos['plantilla']}"
    salida_pdf = f"static/certificados/generados/{datos['codigo']}.pdf"

    os.makedirs("static/certificados/generados", exist_ok=True)

    ruta_qr = crear_qr(datos)

    plantilla = PdfReader(plantilla_pdf)
    overlay_pdf = crear_overlay(datos, ruta_qr)

    writer = PdfWriter()

    for i in range(len(plantilla.pages)):
        pagina_base = plantilla.pages[i]

        if i < len(overlay_pdf.pages):
            pagina_base.merge_transformed_page(
                overlay_pdf.pages[i],
                Transformation()
            )

        writer.add_page(pagina_base)

    with open(salida_pdf, "wb") as archivo_salida:
        writer.write(archivo_salida)

    return salida_pdf