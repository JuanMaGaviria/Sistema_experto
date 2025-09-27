from flask import Flask, render_template, request, jsonify
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import io
import base64
import json
import time
app = Flask(__name__)

# Base de conocimiento
base_conocimiento = {
    "centro": {
        "descripcion": "Centro de la ciudad",
        "nodos": ["Plaza Central", "Catedral", "Alcaldía", "Banco", "Hospital Central"],
        "enlaces": [
            ("Plaza Central", "Catedral", 3),
            ("Plaza Central", "Alcaldía", 5),
            ("Catedral", "Banco", 4),
            ("Alcaldía", "Hospital Central", 6),
            ("Banco", "Hospital Central", 2),
            ("Plaza Central", "Hospital Central", 8)
        ]
    },
    "universidad": {
        "descripcion": "Zona universitaria",
        "nodos": ["Entrada Principal", "Biblioteca", "Cafetería", "Laboratorios", "Rectoría"],
        "enlaces": [
            ("Entrada Principal", "Biblioteca", 4),
            ("Entrada Principal", "Cafetería", 2),
            ("Biblioteca", "Laboratorios", 3),
            ("Cafetería", "Rectoría", 5),
            ("Laboratorios", "Rectoría", 4),
            ("Biblioteca", "Rectoría", 6)
        ]
    },
    "aeropuerto": {
        "descripcion": "Zona aeroportuaria",
        "nodos": ["Terminal 1", "Terminal 2", "Estacionamiento", "Hotel", "Centro Comercial"],
        "enlaces": [
            ("Terminal 1", "Terminal 2", 6),
            ("Terminal 1", "Estacionamiento", 3),
            ("Terminal 2", "Hotel", 4),
            ("Estacionamiento", "Centro Comercial", 5),
            ("Hotel", "Centro Comercial", 2),
            ("Terminal 1", "Centro Comercial", 8)
        ]
    }
}

# Motor de inferencia


# Instancia del motor de inferencia
motor = MotorInferencia()

@app.route('/')
def index():
    return render_template('index.html', zonas=list(base_conocimiento.keys()))

@app.route('/api/grafo/<zona>')
def obtener_grafo(zona):
    """API para obtener información del grafo"""
    info = motor.obtener_info_grafo(zona)
    if info:
        # Generar imagen del grafo
        imagen = motor.generar_imagen_grafo(zona)
        info['imagen'] = imagen
        return jsonify(info)
    return jsonify({"error": "Zona no encontrada"}), 404

@app.route('/api/grafo/<zona>/ruta')
def obtener_grafo_con_ruta(zona):
    """API para obtener grafo con ruta resaltada"""
    ruta = request.args.get('ruta', '').split(',') if request.args.get('ruta') else None
    nodo_actual = request.args.get('nodo_actual')
    
    info = motor.obtener_info_grafo(zona)
    if info:
        imagen = motor.generar_imagen_grafo(zona, ruta, nodo_actual)
        return jsonify({'imagen': imagen})
    return jsonify({"error": "Zona no encontrada"}), 404

@app.route('/api/ruta', methods=['POST'])
def calcular_ruta():
    """API para calcular la ruta óptima"""
    data = request.json
    zona = data.get('zona')
    origen = data.get('origen')
    destino = data.get('destino')
    
    if not all([zona, origen, destino]):
        return jsonify({"error": "Datos incompletos"}), 400
    
    resultado = motor.obtener_ruta_optima(zona, origen, destino)
    return jsonify(resultado)

if __name__ == '__main__':
    print("🚌 Sistema Experto de Transporte Masivo iniciando...")
    print("📍 Zonas disponibles:", list(base_conocimiento.keys()))
    print("🌐 Accede en: http://127.0.0.1:5000")
    print("📦 Dependencias requeridas: pip install flask networkx matplotlib")
    app.run(debug=True, host='127.0.0.1', port=5000)