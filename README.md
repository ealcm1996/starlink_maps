# Starlink Location Monitor

Monitor de ubicación para antenas Starlink con interfaz web responsive.

## Características
- Monitoreo en tiempo real de la ubicación de antenas Starlink
- Interfaz web responsive (desktop y móvil)
- Visualización en mapa con vista satélite
- PWA (Progressive Web App) instalable
- Soporte para múltiples antenas

## Requisitos
- Python 3.8+
- Flask
- gRPC
- Conexión a antena Starlink

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/starlink-monitor.git
cd starlink-monitor
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación:
```bash
python starlink_map.py
```

5. Abrir en el navegador:
```
http://localhost:5000
```

## Estructura del Proyecto
```
starlink-monitor/
├── static/
│   ├── icons/
│   └── Starlink_Logo.png
├── templates/
│   └── index.html
├── starlink_map.py
├── manifest.json
├── sw.js
├── requirements.txt
└── README.md
```

## Licencia
MIT
