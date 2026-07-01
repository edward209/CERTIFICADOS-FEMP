import fitz
import qrcode
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

    documento = fitz.open(plantilla_pdf)

    # =========================
    # PÁGINA 1
    # =========================
    pagina1 = documento[0]

    ancho = pagina1.rect.width

    nombre = datos["nombre"].upper()

    pagina1.insert_text(
        (ancho / 2 - 86, 344),
        nombre,
        fontsize=22,
        fontname="helv",
        color=(0, 0, 0)
    )

    # =========================
    # PÁGINA 2
    # =========================
    if len(documento) > 1:
        pagina2 = documento[1]

        codigo = datos["codigo"]
        cedula = datos["cedula"]

        pagina2.insert_text(
            (360, 445),
            codigo,
            fontsize=11,
            fontname="helv",
            color=(0, 0, 0)
        )

        pagina2.insert_text(
            (360, 460),
            cedula,
            fontsize=11,
            fontname="helv",
            color=(0, 0, 0)
        )

        rect_qr = fitz.Rect(700, 430, 780, 510)
        pagina2.insert_image(rect_qr, filename=ruta_qr)

        pagina2.insert_text(
            (700, 525),
            "VALIDAR CERTIFICADO",
            fontsize=8,
            fontname="helv",
            color=(0, 0, 0)
        )

    documento.save(salida_pdf)
    documento.close()

    return salida_pdf