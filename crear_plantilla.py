from PIL import Image, ImageDraw, ImageFont
import os

ANCHO = 1600
ALTO = 1100

os.makedirs("static/certificados/plantillas", exist_ok=True)

img = Image.new("RGB", (ANCHO, ALTO), "white")
draw = ImageDraw.Draw(img)

# Bordes
draw.rectangle((40, 40, ANCHO - 40, ALTO - 40), outline="black", width=6)
draw.rectangle((70, 70, ANCHO - 70, ALTO - 70), outline="black", width=2)

# Textos base
draw.text((ANCHO / 2, 150), "FUNDACIÓN DE ENFERMEROS MILITARES Y POLICÍA", anchor="mm", fill="black")
draw.text((ANCHO / 2, 210), "F.E.M.P.", anchor="mm", fill="black")
draw.text((ANCHO / 2, 330), "CERTIFICADO DE PARTICIPACIÓN", anchor="mm", fill="black")

draw.text((ANCHO / 2, 460), "Otorgado a:", anchor="mm", fill="black")
draw.text((ANCHO / 2, 560), "NOMBRE DEL ESTUDIANTE", anchor="mm", fill="black")

draw.text((ANCHO / 2, 680), "Por haber completado satisfactoriamente el curso:", anchor="mm", fill="black")
draw.text((ANCHO / 2, 760), "NOMBRE DEL CURSO", anchor="mm", fill="black")

draw.text((330, 900), "Fecha:", anchor="mm", fill="black")
draw.text((800, 900), "Duración:", anchor="mm", fill="black")
draw.text((1250, 900), "Código:", anchor="mm", fill="black")

draw.text((400, 1000), "________________________", anchor="mm", fill="black")
draw.text((400, 1040), "Director Académico", anchor="mm", fill="black")

draw.text((1200, 1000), "________________________", anchor="mm", fill="black")
draw.text((1200, 1040), "Instructor", anchor="mm", fill="black")

ruta = "static/certificados/plantillas/plantilla_base.png"
img.save(ruta)

print("Plantilla creada correctamente:")
print(ruta)