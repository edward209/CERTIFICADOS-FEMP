from flask import Flask, render_template, request, redirect, session, send_file
import json
import os
from datetime import datetime
from pdf_generator import crear_pdf_certificado
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = "clave-secreta-femp"


def cargar_cursos():
    with open("data/cursos.json", "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def cargar_certificados():
    with open("data/certificados.json", "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_certificados(certificados):
    with open("data/certificados.json", "w", encoding="utf-8") as archivo:
        json.dump(certificados, archivo, indent=4, ensure_ascii=False)


def cargar_usuarios():
    with open("data/usuarios.json", "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def generar_codigo():
    certificados = cargar_certificados()
    numero = len(certificados) + 1
    año = datetime.now().year
    return f"FEMP-{año}-{numero:04d}"


def formatear_fecha(fecha_str):
    meses = {
        "01": "ENERO",
        "02": "FEBRERO",
        "03": "MARZO",
        "04": "ABRIL",
        "05": "MAYO",
        "06": "JUNIO",
        "07": "JULIO",
        "08": "AGOSTO",
        "09": "SEPTIEMBRE",
        "10": "OCTUBRE",
        "11": "NOVIEMBRE",
        "12": "DICIEMBRE"
    }

    año, mes, dia = fecha_str.split("-")
    return f"{dia} DE {meses[mes]} DE {año}"


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]

        usuarios = cargar_usuarios()

        for user in usuarios:
            if user["usuario"] == usuario and user["clave"] == clave:
                session["admin"] = True
                return redirect("/admin")

        error = "Usuario o contraseña incorrectos"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/crear", methods=["GET", "POST"])
def crear_certificado():

    if not session.get("admin"):
        return redirect("/login")
        
    cursos = cargar_cursos()

    if request.method == "POST":
        nombre = request.form["nombre"]
        cedula = request.form["cedula"]
        curso_nombre = request.form["curso"]
        fecha = request.form["fecha"]
        fecha_pdf = formatear_fecha(fecha)

        duracion = ""
        plantilla = ""

        for curso in cursos:
            if curso["nombre"] == curso_nombre:
                duracion = curso["duracion"]
                plantilla = curso["plantilla"]
                break

        codigo = generar_codigo()

        nuevo_certificado = {
            "codigo": codigo,
            "nombre": nombre,
            "cedula": cedula,
            "curso": curso_nombre,
            "duracion": duracion,
            "fecha": fecha_pdf,
            "plantilla": plantilla
        }

        ruta_pdf = crear_pdf_certificado(nuevo_certificado)
        nuevo_certificado["pdf"] = ruta_pdf

        certificados = cargar_certificados()
        certificados.append(nuevo_certificado)
        guardar_certificados(certificados)

        return render_template(
            "certificado_generado.html",
            nombre=nombre,
            cedula=cedula,
            curso=curso_nombre,
            duracion=duracion,
            fecha=fecha_pdf,
            codigo=codigo,
            plantilla=plantilla,
            ruta_pdf=ruta_pdf
        )

    return render_template("crear_certificado.html", cursos=cursos)


@app.route("/verificar", methods=["GET", "POST"])
def verificar_certificado():
    resultado = None

    codigo_url = request.args.get("codigo", "").strip().upper()

    if codigo_url:
        certificados = cargar_certificados()

        for certificado in certificados:
            if certificado["codigo"].upper() == codigo_url:
                resultado = {
                    "valido": True,
                    "codigo": certificado["codigo"],
                    "nombre": certificado["nombre"],
                    "cedula": certificado["cedula"],
                    "curso": certificado["curso"],
                    "duracion": certificado["duracion"],
                    "fecha": certificado["fecha"]
                }
                break

        if resultado is None:
            resultado = {"valido": False}

    if request.method == "POST":
        codigo_buscado = request.form["codigo"].strip().upper()
        certificados = cargar_certificados()

        for certificado in certificados:
            if certificado["codigo"].upper() == codigo_buscado:
                resultado = {
                    "valido": True,
                    "codigo": certificado["codigo"],
                    "nombre": certificado["nombre"],
                    "cedula": certificado["cedula"],
                    "curso": certificado["curso"],
                    "duracion": certificado["duracion"],
                    "fecha": certificado["fecha"]
                }
                break

        if resultado is None:
            resultado = {"valido": False}

    return render_template("verificar_certificado.html", resultado=resultado)

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    busqueda = request.args.get("buscar", "").strip().lower()

    certificados = cargar_certificados()

    if busqueda:
        certificados = [
            cert for cert in certificados
            if busqueda in cert["codigo"].lower()
            or busqueda in cert["nombre"].lower()
            or busqueda in cert["cedula"].lower()
            or busqueda in cert["curso"].lower()
        ]

    estadisticas = {}

    for cert in certificados:
        curso = cert["curso"]

        if curso not in estadisticas:
            estadisticas[curso] = 0

        estadisticas[curso] += 1

    return render_template(
        "admin.html",
        certificados=certificados,
        busqueda=busqueda,
        estadisticas=estadisticas,
        total=len(certificados)
    )


@app.route("/eliminar/<codigo>", methods=["POST"])
def eliminar_certificado(codigo):
    if not session.get("admin"):
        return redirect("/login")

    certificados = cargar_certificados()

    pdf_a_eliminar = None

    for cert in certificados:
        if cert["codigo"] == codigo:
            pdf_a_eliminar = cert.get("pdf")
            break

    certificados_actualizados = [
        cert for cert in certificados
        if cert["codigo"] != codigo
    ]

    guardar_certificados(certificados_actualizados)

    if pdf_a_eliminar and os.path.exists(pdf_a_eliminar):
        os.remove(pdf_a_eliminar)

    return redirect("/admin")

@app.route("/plantillas", methods=["GET", "POST"])
def plantillas():

    if not session.get("admin"):
        return redirect("/login")

    carpeta_plantillas = "static/certificados/plantillas"

    if request.method == "POST":
        nombre = request.form["nombre"]
        archivo = request.files["archivo"]

        if archivo and archivo.filename.endswith(".pdf"):
            nombre_seguro = secure_filename(nombre)

            if not nombre_seguro.endswith(".pdf"):
                nombre_seguro += ".pdf"

            ruta_guardado = os.path.join(carpeta_plantillas, nombre_seguro)
            archivo.save(ruta_guardado)

            return redirect("/plantillas")

    archivos = [
        archivo for archivo in os.listdir(carpeta_plantillas)
        if archivo.endswith(".pdf")
    ]

    return render_template(
        "plantillas.html",
        plantillas=archivos
    )


@app.route("/cursos", methods=["GET", "POST"])
def cursos():

    if not session.get("admin"):
        return redirect("/login")

    carpeta_plantillas = "static/certificados/plantillas"

    if request.method == "POST":
        nombre = request.form["nombre"]
        duracion = request.form["duracion"]
        plantilla = request.form["plantilla"]

        cursos = cargar_cursos()

        nuevo_curso = {
            "nombre": nombre,
            "duracion": duracion,
            "plantilla": plantilla
        }

        cursos.append(nuevo_curso)

        with open("data/cursos.json", "w", encoding="utf-8") as archivo:
            json.dump(cursos, archivo, indent=4, ensure_ascii=False)

        return redirect("/cursos")

    cursos = cargar_cursos()

    plantillas = [
        archivo for archivo in os.listdir(carpeta_plantillas)
        if archivo.endswith(".pdf")
    ]

    return render_template(
        "cursos.html",
        cursos=cursos,
        plantillas=plantillas
    )

@app.route("/editar/<codigo>", methods=["GET", "POST"])
def editar_certificado(codigo):

    if not session.get("admin"):
        return redirect("/login")

    certificados = cargar_certificados()
    cursos = cargar_cursos()

    certificado = None

    for cert in certificados:
        if cert["codigo"] == codigo:
            certificado = cert
            break

    if certificado is None:
        return redirect("/admin")

    if request.method == "POST":

        nombre = request.form["nombre"]
        cedula = request.form["cedula"]
        curso_nombre = request.form["curso"]
        fecha = request.form["fecha"]

        fecha_pdf = formatear_fecha(fecha)

        duracion = ""
        plantilla = ""

        for curso in cursos:
            if curso["nombre"] == curso_nombre:
                duracion = curso["duracion"]
                plantilla = curso["plantilla"]
                break

        certificado["nombre"] = nombre
        certificado["cedula"] = cedula
        certificado["curso"] = curso_nombre
        certificado["duracion"] = duracion
        certificado["fecha"] = fecha_pdf
        certificado["plantilla"] = plantilla

        # Regenerar PDF
        ruta_pdf = crear_pdf_certificado(certificado)
        certificado["pdf"] = ruta_pdf

        guardar_certificados(certificados)

        return redirect("/admin")

    return render_template(
        "editar_certificado.html",
        certificado=certificado,
        cursos=cursos
    )

@app.route("/descargar", methods=["GET", "POST"])
def cargar_solicitudes():
    with open("data/solicitudes.json", "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_solicitudes(solicitudes):
    with open("data/solicitudes.json", "w", encoding="utf-8") as archivo:
        json.dump(solicitudes, archivo, indent=4, ensure_ascii=False)

    error = None

    if request.method == "POST":

        codigo = request.form["codigo"].strip().upper()
        fecha = formatear_fecha(request.form["fecha"])

        certificados = cargar_certificados()

        for cert in certificados:

            if (
                cert["codigo"].upper() == codigo
                and cert["fecha"].upper() == fecha.upper()
            ):
                return render_template(
                    "descargar_certificado.html",
                    certificado=cert
                )

        error = "Código o fecha incorrectos"

    return render_template(
        "descargar_certificado.html",
        error=error
    )

@app.route("/descargar-pdf/<codigo>")
def descargar_pdf(codigo):

    certificados = cargar_certificados()

    for cert in certificados:

        if cert["codigo"].upper() == codigo.upper():

            ruta_pdf = crear_pdf_certificado(cert)

            return send_file(
                ruta_pdf,
                as_attachment=True,
                download_name=f"{cert['codigo']}.pdf"
            )

    return redirect("/descargar")

@app.route("/solicitar", methods=["GET", "POST"])
def solicitar_certificado():
    cursos = cargar_cursos()

    if request.method == "POST":
        solicitudes = cargar_solicitudes()

        nueva_solicitud = {
            "id": len(solicitudes) + 1,
            "nombre": request.form["nombre"],
            "cedula": request.form["cedula"],
            "correo": request.form["correo"],
            "telefono": request.form["telefono"],
            "curso": request.form["curso"],
            "fecha": formatear_fecha(request.form["fecha"]),
            "estado": "Pendiente"
        }

        solicitudes.append(nueva_solicitud)
        guardar_solicitudes(solicitudes)

        return """
        <h1>Solicitud enviada correctamente</h1>
        <p>Su solicitud será revisada por la administración.</p>
        <a href="/">Volver al inicio</a>
        """

    return render_template("solicitar_certificado.html", cursos=cursos)

if __name__ == "__main__":
    app.run(debug=True)