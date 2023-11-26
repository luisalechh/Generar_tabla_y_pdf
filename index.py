from flask import Flask, render_template, request, redirect, url_for, Response
from reportlab.pdfgen import canvas
from io import BytesIO
import json

app = Flask(__name__)

def obtener_datos():
    try:
        with open('database.json', 'r') as json_file:
            datos = json.load(json_file)
    except FileNotFoundError:
        datos = []
    return datos

def calcular_resultados(datos):
    for fila in datos:
        fila['multiplicacion'] = fila['a1'] * fila['b2']

def guardar_en_json(datos):
    with open('database.json', 'w') as json_file:
        json.dump(datos, json_file, indent=4)

@app.route('/tabla')
def mostrar_tabla():
    datos = obtener_datos()
    return render_template('tabla.html', datos=datos)

@app.route('/calcular', methods=['POST'])
def calcular():
    datos = obtener_datos()
    calcular_resultados(datos)
    guardar_en_json(datos)
    return redirect(url_for('mostrar_tabla'))

@app.route('/insertar', methods=['POST'])
def insertar():
    nuevo_dato = {
        'a1': float(request.form['valor_a']),
        'b2': float(request.form['valor_b']),
        'multiplicacion': None
    }

    datos = obtener_datos()
    datos.append(nuevo_dato)
    guardar_en_json(datos)

    return redirect(url_for('mostrar_tabla'))

@app.route('/eliminar', methods=['POST'])
def eliminar():
    fila_id = int(request.form['fila_id'])
    datos = obtener_datos()

    if 0 <= fila_id < len(datos):
        del datos[fila_id]

    guardar_en_json(datos)

    return redirect(url_for('mostrar_tabla'))

@app.route('/modificar', methods=['POST'])
def modificar():
    fila_id = int(request.form['fila_id'])
    nuevo_valor_a = float(request.form['nuevo_valor_a'])
    nuevo_valor_b = float(request.form['nuevo_valor_b'])

    datos = obtener_datos()

    if 0 <= fila_id < len(datos):
        datos[fila_id]['a1'] = nuevo_valor_a
        datos[fila_id]['b2'] = nuevo_valor_b

    guardar_en_json(datos)

    return redirect(url_for('mostrar_tabla'))



@app.route('/generar_pdf')
def generar_pdf():
    # Obtén los datos actuales
    datos = obtener_datos()

    # Genera el PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 800, "Valores de la Tabla")

    # Encabezados
    pdf.drawString(100, 780, "A")
    pdf.drawString(200, 780, "B")
    pdf.drawString(300, 780, "Multiplicación")

    y_position = 760  # Ajusta la posición vertical de acuerdo a tus necesidades
    for fila in datos:
        # Dibujar valores
        pdf.drawString(100, y_position, str(fila['a1']))
        pdf.drawString(200, y_position, str(fila['b2']))
        pdf.drawString(300, y_position, str(fila['multiplicacion']))

        y_position -= 15  # Ajusta la posición vertical de acuerdo a tus necesidades

    pdf.save()
    buffer.seek(0)

    # Envía el PDF como respuesta
    response = Response(buffer.getvalue(), content_type='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=tabla.pdf'

    return response

if __name__ == '__main__':
    app.run(debug=True)
