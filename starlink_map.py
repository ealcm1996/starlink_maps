from flask import Flask, render_template, jsonify, send_from_directory, send_file
import sys
import os
import logging
from pyngrok import ngrok
import requests
import json

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Asegurarnos que podemos importar el módulo starlink_grpc desde el directorio actual
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import starlink_grpc
import time

app = Flask(__name__)
# Deshabilitar el caché de templates
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Añadir estas variables globales
NGROK_TUNNEL = None
STARLINK_LOCAL_URL = "http://192.168.100.1"

def setup_ngrok_tunnel():
    global NGROK_TUNNEL
    try:
        if os.environ.get('RENDER'):
            # Configurar ngrok con el token (debes configurar esto en las variables de entorno de Render)
            ngrok_token = os.environ.get('NGROK_TOKEN')
            if not ngrok_token:
                logger.error("NGROK_TOKEN no configurado en variables de entorno")
                return False
                
            ngrok.set_auth_token(ngrok_token)
            
            # Crear túnel TCP a la IP del Starlink
            NGROK_TUNNEL = ngrok.connect(STARLINK_LOCAL_URL, "tcp")
            logger.info(f"Túnel ngrok creado: {NGROK_TUNNEL.public_url}")
            return True
    except Exception as e:
        logger.error(f"Error al crear túnel ngrok: {str(e)}")
        return False
    return True

def test_starlink_connection():
    try:
        if os.environ.get('RENDER'):
            if not NGROK_TUNNEL:
                if not setup_ngrok_tunnel():
                    return False
            
            # Usar la URL del túnel para conectar
            base_url = NGROK_TUNNEL.public_url
            context = starlink_grpc.ChannelContext(target=base_url)
        else:
            # Conexión local normal
            context = starlink_grpc.ChannelContext()
            
        dish_id = starlink_grpc.get_id(context=context)
        logger.info(f"Conexión exitosa con el plato Starlink. ID: {dish_id}")
        return True
    except Exception as e:
        logger.error(f"Error al conectar con el plato Starlink: {str(e)}")
        return False
    finally:
        if 'context' in locals():
            context.close()

def get_starlink_location():
    try:
        # Primero verificar si hay conexión
        if not test_starlink_connection():
            logger.error("No hay conexión con el plato Starlink")
            return {"error": "No se detecta conexión con el plato Starlink"}
            
        logger.debug("Intentando obtener ubicación del plato...")
        context = starlink_grpc.ChannelContext()
        location_data = starlink_grpc.location_data(context=context)
        
        logger.debug(f"Datos de ubicación recibidos: {location_data}")
        
        if location_data["latitude"] is None or location_data["longitude"] is None:
            logger.warning("No se pudo obtener la ubicación - valores nulos")
            return {
                "error": "No se pudo obtener la ubicación. Asegúrate de que el acceso a la ubicación esté habilitado en el plato."
            }
            
        return {
            "latitude": location_data["latitude"],
            "longitude": location_data["longitude"],
            "altitude": location_data["altitude"],
            "status": "active",
            "id": "oficina"
        }
        
    except Exception as e:
        logger.error(f"Error al obtener ubicación: {str(e)}")
        return {"error": f"Error de conexión con el plato: {str(e)}"}
    finally:
        if 'context' in locals():
            context.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_location')
def location():
    logger.debug("Recibiendo petición de ubicación")
    location_data = get_starlink_location()
    logger.debug(f"Enviando datos: {location_data}")
    return jsonify(location_data)

@app.route('/test')
def test():
    """Ruta de prueba para verificar que el servidor está funcionando"""
    return jsonify({"status": "ok", "message": "Servidor funcionando correctamente"})

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('C:/xampp/htdocs/starlink-grpc-tools-main', filename)

@app.route('/manifest.json')
def manifest():
    return send_file('manifest.json', mimetype='application/json')

@app.route('/sw.js')
def service_worker():
    return send_file('sw.js', mimetype='application/javascript')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Modificar el main para inicializar el túnel
if __name__ == '__main__':
    try:
        logger.info("Verificando conexión con el plato Starlink...")
        if os.environ.get('RENDER'):
            setup_ngrok_tunnel()
        
        if test_starlink_connection():
            logger.info("Iniciando servidor web...")
            app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
        else:
            logger.error("No se pudo establecer conexión con el plato Starlink")
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {str(e)}", exc_info=True) 