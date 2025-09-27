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
class MotorInferencia:
    def _init_(self):
        self.grafos = {}
        self._construir_grafos()
    
    def _construir_grafos(self):
        """Construye los grafos usando NetworkX"""
        for zona, datos in base_conocimiento.items():
            G = nx.Graph()
            G.add_nodes_from(datos["nodos"])
            G.add_weighted_edges_from(datos["enlaces"])
            self.grafos[zona] = G
    
    def obtener_ruta_optima(self, zona, origen, destino):
        """Encuentra la ruta más corta entre dos puntos"""
        try:
            grafo = self.grafos[zona]
            ruta = nx.shortest_path(grafo, origen, destino, weight='weight')
            distancia = nx.shortest_path_length(grafo, origen, destino, weight='weight')
            return {
                "ruta": ruta,
                "distancia": distancia,
                "exito": True
            }
        except nx.NetworkXNoPath:
            return {
                "ruta": [],
                "distancia": float('inf'),
                "exito": False,
                "mensaje": "No hay ruta disponible"
            }
    
    def generar_imagen_grafo(self, zona, ruta_resaltada=None, nodo_actual=None):
        """Genera imagen del grafo para visualización"""
        if zona not in self.grafos:
            return None
            
        grafo = self.grafos[zona]
        plt.figure(figsize=(10, 8))
        
        # Posiciones de los nodos
        pos = nx.spring_layout(grafo, seed=42)
        
        # Dibujar todos los enlaces
        nx.draw_networkx_edges(grafo, pos, alpha=0.6, width=2, edge_color='gray')
        
        # Resaltar ruta si existe
        if ruta_resaltada and len(ruta_resaltada) > 1:
            ruta_edges = [(ruta_resaltada[i], ruta_resaltada[i+1]) for i in range(len(ruta_resaltada)-1)]
            nx.draw_networkx_edges(grafo, pos, edgelist=ruta_edges, 
                                 edge_color='red', width=4, alpha=0.8)
        
        # Dibujar nodos
        colores_nodos = []
        for nodo in grafo.nodes():
            if nodo == nodo_actual:
                colores_nodos.append('orange')  # Nodo actual
            elif ruta_resaltada and nodo in ruta_resaltada:
                if nodo == ruta_resaltada[0]:
                    colores_nodos.append('green')  # Origen
                elif nodo == ruta_resaltada[-1]:
                    colores_nodos.append('red')    # Destino
                else:
                    colores_nodos.append('yellow') # Ruta
            else:
                colores_nodos.append('lightblue')
                
        nx.draw_networkx_nodes(grafo, pos, node_color=colores_nodos, 
                             node_size=1000, alpha=0.9)
        
        # Etiquetas de nodos
        nx.draw_networkx_labels(grafo, pos, font_size=8, font_weight='bold')
        
        # Etiquetas de pesos en enlaces
        edge_labels = nx.get_edge_attributes(grafo, 'weight')
        nx.draw_networkx_edge_labels(grafo, pos, edge_labels, font_size=8)
        
        plt.title(f'Grafo de {zona.title()} - {base_conocimiento[zona]["descripcion"]}', 
                 fontsize=14, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # Convertir a base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return img_base64
    
    def obtener_info_grafo(self, zona):
        """Obtiene información del grafo para visualización"""
        if zona not in self.grafos:
            return None
        
        grafo = self.grafos[zona]
        nodos = list(grafo.nodes())
        enlaces = [(u, v, grafo[u][v]['weight']) for u, v in grafo.edges()]
        
        return {
            "nodos": nodos,
            "enlaces": enlaces,
            "descripcion": base_conocimiento[zona]["descripcion"]
        }

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
